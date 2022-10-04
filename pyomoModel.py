import numpy as np
# import gurobipy as gp
# from gurobipy import GRB
import networkx as nx
import matplotlib.pyplot as plt
from Params import *
import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition


def create_model():
    model = pyo.AbstractModel()

    # Define Sets
    model.V = pyo.Set()  # vertices
    model.K = pyo.Set()  # product range
    model.E = pyo.Set(dimen=2)  # links

    # Define Parameters
    # network flow
    model.u = pyo.Param(model.E)  # link capacity
    model.f = pyo.Param(model.E)  # link cost
    model.c = pyo.Param(model.E, model.K)  # transport cost

    # production
    model.phi = pyo.Param(model.V)  # production line opening fixed cost
    model.p = pyo.Param(model.V, model.K)  # production rate
    model.Lmax = pyo.Param(model.V)  # production run length capacity
    model.e = pyo.Param(model.V, model.K)  # production cost
    model.r = pyo.Param(model.K, model.K)  # product conversion rate

    # demand/inventory
    model.d = pyo.Param(model.V, model.K)  # demand
    # model.Pi = pyo.Param(model.V, model.K)  # revenue
    model.h = pyo.Param(model.V, model.K)  # unit holding cost
    model.I_0 = pyo.Param(model.V, model.K)  # initial inventory
    model.I_s = pyo.Param(model.V, model.K)  # safety inventory target

    # penalty
    model.rho_d = pyo.Param(model.V, model.K)  # penalty cost for unsatisfied demand
    model.rho_I = pyo.Param(model.V, model.K)  # penalty cost for unsatisfied inventory target

    # Define Variables
    # network flow
    model.y = pyo.Var(model.E, model.K, within=pyo.NonNegativeReals)  # flow
    model.z = pyo.Var(model.E, within=pyo.Binary, initialize=0)  # link usage
    model.x = pyo.Var(model.V, model.K, within=pyo.Reals)  # demand satisfied

    # production/inventory
    model.L = pyo.Var(model.V, model.K, within=pyo.NonNegativeReals)  # run length
    model.zeta = pyo.Var(model.V, within=pyo.Binary, initialize=0)  # product line usage
    model.I = pyo.Var(model.V, model.K, within=pyo.NonNegativeReals)  # inventory

    # penalty
    model.delta_d = pyo.Var(model.V, model.K, within=pyo.NonNegativeReals)  # demand penalty term
    model.delta_I = pyo.Var(model.V, model.K, within=pyo.NonNegativeReals)  # inventory penalty term

    # Define Objectives
    def cost_rule(model):
        return (sum(model.f[i, j] * model.z[i, j] for i, j in model.E) +
                sum(model.phi[i] * model.zeta[i] for i in model.V) +
                sum(model.c[i, j, k] * model.y[i, j, k] for i, j in model.E for k in
                    model.K) +
                sum(model.h[i, k] * model.I[i, k] +
                    model.e[i, k] * model.L[i, k] +
                    model.rho_I[i, k] * model.delta_I[i, k] +
                    model.rho_d[i, k] * model.delta_d[i, k] for i in model.V for k
                    in model.K))

    model.cost = pyo.Objective(rule=cost_rule)

    # model.profit = pyo.Objective()

    # Define Constraints
    # flow balance
    def balance_rule(model, i, k):
        return (sum(model.y[i, j, k] for _, j in model.E if _ == i) - sum(
            model.y[j, i, k] for j, _ in model.E if _ == i) + sum(
            model.r[k, k1] * model.p[i, k1] * model.L[i, k1] for k1 in model.K) - model.p[i, k] *
                model.L[i, k] == model.x[i, k] + model.I_0[i, k] - model.I[i, k])

    model.flow_balance = pyo.Constraint(model.V, model.K, rule=balance_rule)

    # link capacity
    def link_cap_rule(model, i, j):
        return sum(model.y[i, j, k] for k in model.K) <= model.u[i, j] * model.z[i, j]

    model.link_capacity = pyo.Constraint(model.E, rule=link_cap_rule)

    # production capacity
    def prod_cap_rule(model, i):
        return sum(model.L[i, k] for k in model.K) <= model.Lmax[i] * model.zeta[i]

    model.prod_capacity = pyo.Constraint(model.V, rule=prod_cap_rule)

    # penalty terms
    def demand_pel_rule(model, i, k):
        return model.delta_d[i, k] >= model.x[i, k] - model.d[i, k]

    model.demand_penalty = pyo.Constraint(model.V, model.K, rule=demand_pel_rule)

    def inv_pel_rule(model, i, k):
        return model.delta_I[i, k] >= model.I_s[i, k] - model.I[i, k]

    model.inventory_penalty = pyo.Constraint(model.V, model.K, rule=inv_pel_rule)

    # TODO: ADD DISRUPTION REACTIONS

    return model


class SinglePeriod:

    def __init__(self, exist_G=False, soft=True):
        self.model = create_model()
        self.instance = self.model.is_constructed()
        self.results = None
        self.solved = False
        self.G = nx.MultiDiGraph()
        self.network_change = False

        if exist_G:
            self.model.exist_z = pyo.Param(self.model.E)
            self.model.exist_zeta = pyo.Param(self.model.V)

            self.model.delta_V = pyo.Var(self.model.V, within=pyo.Binary, initialize=0)
            self.model.delta_E = pyo.Var(self.model.E, within=pyo.Binary, initialize=0)

            def vertex_pel_rule1(model, i):
                return model.delta_V[i] >= model.zeta[i] - model.exist_zeta[i]

            self.model.vertexChange_penalty1 = pyo.Constraint(self.model.V, rule=vertex_pel_rule1)

            def vertex_pel_rule2(model, i):
                return model.delta_V[i] >= model.exist_zeta[i] - model.zeta[i]

            self.model.vertexChange_penalty2 = pyo.Constraint(self.model.V, rule=vertex_pel_rule2)

            def edge_pel_rule1(model, i, j):
                return model.delta_E[i, j] >= model.z[i, j] - model.exist_z[i, j]

            self.model.linkChange_penalty_1 = pyo.Constraint(self.model.E, rule=edge_pel_rule1)

            def edge_pel_rule2(model, i, j):
                return model.delta_E[i, j] >= model.exist_z[i, j] - model.z[i, j]

            self.model.Rho = pyo.Param(initialize=0)
            self.model.cost.deactivate()
            self.model.linkChange_penalty_2 = pyo.Constraint(self.model.E, rule=edge_pel_rule2)

            def cost_networkChange_rule(model):
                return (sum(model.f[i, j] * model.z[i, j] for i, j in model.E) +
                        sum(model.phi[i] * model.zeta[i] for i in model.V) +
                        sum(model.c[i, j, k] * model.y[i, j, k] for i, j in model.E for k in
                            model.K) +
                        sum(model.h[i, k] * model.I[i, k] +
                            model.e[i, k] * model.L[i, k] +
                            model.rho_I[i, k] * model.delta_I[i, k] +
                            model.rho_d[i, k] * model.delta_d[i, k] for i in model.V for k
                            in model.K) +
                        model.Rho * (sum(model.delta_E[i, j] for i, j in model.E) + sum(
                            model.delta_V[i] for i in model.V)))

            self.model.cost_networkChange = pyo.Objective(rule=cost_networkChange_rule)
            self.model.cost_networkChange.activate()
            if soft is False:
                self.model.Emax = pyo.Param(initialize=0)
                self.model.delta_Eplus = pyo.Var(self.model.E, within=pyo.Binary, initialize=0)

                def edge_pel_rule3(model, i, j):
                    return model.delta_Eplus[i, j] >= model.z[i, j] - model.exist_z[i, j]

                self.model.linkChange_penalty_3 = pyo.Constraint(self.model.E, rule=edge_pel_rule3)

                def edge_pel_rule4(model):
                    return sum(model.delta_Eplus[i, j] for i, j in model.E) <= model.Emax
                self.model.linkChange_penalty_4 = pyo.Constraint(rule=edge_pel_rule4)

            self.soft = soft
            self.network_change = True


    def create_instance(self, filenames: list):
        # https://pyomo.readthedocs.io/en/stable/working_abstractmodels/data/raw_dicts.html
        # https://pyomo.readthedocs.io/en/stable/working_abstractmodels/data/dataportals.html
        # TODO: CREATE SUITABLE DATA IMPORT PORTAL
        data = pyo.DataPortal()
        for filename in filenames:
            data.load(filename=filename)
        self.instance = self.model.create_instance(data)

    def get(self, attrs):
        if len(attrs) == 0:
            return
        output = dict()
        for attr in attrs:
            output[attr] = {index: pyo.value(getattr(self.instance, attr)[index]) for index in
                            getattr(self.instance, attr)}
        return output

    def solve(self, solver='gurobi', tee=True):
        opt = pyo.SolverFactory(solver)
        # opt.options['Presolve'] = 0
        if self.instance is None:
            print("Error: Model has not been instantiated. Call create_instance()")
        else:
            self.results = opt.solve(self.instance, tee=tee)
            if (self.results.solver.status == SolverStatus.ok) and (
                    self.results.solver.termination_condition == TerminationCondition.optimal):
                print("The instance is feasible and solved to optimal")

                prodCost = sum(self.instance.phi[i] * pyo.value(self.instance.zeta[i]) for i in self.instance.V) + sum(
                    self.instance.e[i, k] * pyo.value(self.instance.L[i, k]) for i in self.instance.V for k in
                    self.instance.K)
                transCost = sum(
                    self.instance.f[i, j] * pyo.value(self.instance.z[i, j]) for i, j in self.instance.E) + sum(
                    self.instance.c[i, j, k] * pyo.value(self.instance.y[i, j, k]) for i, j in self.instance.E for k in
                    self.instance.K)
                penalty_demand = sum(
                    self.instance.rho_d[i, k] * pyo.value(self.instance.delta_d[i, k]) for i in self.instance.V for k in
                    self.instance.K)
                reactCost = 0

                print("The production cost is: " + str(prodCost))
                print("The transportation cost is: " + str(transCost))

                if abs(penalty_demand) < 1e-5:
                    print("All demands are satisfied.")
                else:
                    print("Penalty cost for demand lost: " + str(penalty_demand))
                    print("Unmet demand: ")
                    for k in self.instance.K:
                        for v in self.instance.V:
                            if pyo.value(self.instance.delta_d[v, k]) > 1e-4:
                                print(str((v, k)) + ": " + str(pyo.value(self.instance.delta_d[v, k])))

                if self.network_change:
                    reactCost = reactCost + self.instance.Rho * (
                            sum(pyo.value(self.instance.delta_V[i]) for i in self.instance.V) + sum(
                        pyo.value(self.instance.delta_E[i, j]) for i, j in self.instance.E))
                    print("The reaction cost is: " + str(reactCost))
                    print("Total changes of vertices: " + str(
                        sum(pyo.value(self.instance.delta_V[i]) for i in self.instance.V)))
                    if sum(pyo.value(self.instance.delta_V[i]) for i in self.instance.V) > 1e-2:
                        for i in self.instance.V:
                            if pyo.value(self.instance.delta_V[i]) > 1e-4:
                                if pyo.value(self.instance.zeta[v]) > 1e-4:
                                    print(str(v) + ": Added")
                                else:
                                    print(str(v) + ": Removed")
                    print("Total changes of edges: " + str(
                        sum(pyo.value(self.instance.delta_E[i, j]) for i, j in self.instance.E)))
                    if sum(pyo.value(self.instance.delta_E[i, j]) for i, j in self.instance.E) > 1e-2:
                        for i, j in self.instance.E:
                            if pyo.value(self.instance.delta_E[i, j]) > 1e-4:
                                if pyo.value(self.instance.z[i, j]) > 1e-4:
                                    print(str((i, j)) + ": Added")
                                else:
                                    print(str((i, j)) + ": Removed")

                print("Productions:")
                for k in self.instance.K:
                    for v in self.instance.V:
                        if abs(pyo.value(self.instance.L[v, k])) > 1e-8:
                            print(str((v, k)) + ": " + str(pyo.value(self.instance.L[v, k])))
                print("Flows:")
                for k in self.instance.K:
                    for link in self.instance.E:
                        if abs(pyo.value(self.instance.y[link, k])) > 1e-8:
                            print(str(link + (k,)) + ": " + str(pyo.value(self.instance.y[link, k])))
                print("")
            elif self.results.solver.termination_condition == TerminationCondition.infeasible:
                print("The instance is infeasible?")
            else:
                # something else is wrong
                print(str(self.results.solver))

    # TODO: update function for disruption inputs, scenario results storage and comparisons
    def update(self):
        # function for modifying coefficients
        pass
        # function for automatic random
