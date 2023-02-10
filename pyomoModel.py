import json

import numpy as np
# import gurobipy as gp
# from gurobipy import GRB
import networkx as nx
import matplotlib.pyplot as plt
# from Params import *
import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition


def create_model(reschedule):
    model = pyo.AbstractModel()

    # Define Sets
    model.V = pyo.Set()  # vertices
    model.V_mfg = pyo.Set()
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
    # network flow*[
    model.y = pyo.Var(model.E, model.K, within=pyo.NonNegativeReals)  # flow
    model.z = pyo.Var(model.E, within=pyo.Binary, initialize=0)  # link usage
    model.x = pyo.Var(model.V, model.K, within=pyo.Integers)  # demand satisfied
    model.y_u = pyo.Var(model.E, model.K, within=pyo.NonNegativeReals) # under capacity
    model.y_o = pyo.Var(model.E, model.K, within=pyo.NonNegativeReals) # over capacity

    # production/inventory
    model.L = pyo.Var(model.V, model.K, within=pyo.NonNegativeIntegers)  # run length
    model.zeta = pyo.Var(model.V, within=pyo.Binary, initialize=0)  # product line usage
    model.I = pyo.Var(model.V, model.K, within=pyo.NonNegativeReals)  # inventory
    model.L_u = pyo.Var(model.V, model.K, within=pyo.NonNegativeIntegers)  # under capacity
    model.L_o = pyo.Var(model.V, model.K, within=pyo.NonNegativeIntegers)  # over capacity

    # penalty
    model.delta_d = pyo.Var(model.V, model.K, within=pyo.NonNegativeIntegers)  # demand penalty term
    model.delta_I = pyo.Var(model.V, model.K, within=pyo.NonNegativeReals)  # inventory penalty term

    # Define Objectives
    def cost_rule(model):
        return (sum(model.f[i, j] * model.z[i, j] for i, j in model.E) +
                sum(model.phi[i] * model.zeta[i] for i in model.V) +
                # sum(model.c[i, j, k] * model.y_u[i, j, k] + 2 * model.c[i, j, k] * model.y_o[i, j, k] for i, j in model.E for k in
                #     model.K) +
                sum(model.c[i, j, k] * model.y[i, j, k] for i, j in model.E for k in model.K) +
                sum(model.h[i, k] * model.I[i, k] +
                    # model.e[i, k] * model.L_u[i, k] + 2 * model.e[i, k] * model.L_o[i, k] +
                    model.e[i, k] * model.L[i, k] +
                    model.rho_I[i, k] * model.delta_I[i, k] +
                    model.rho_d[i, k] * model.delta_d[i, k] for i in model.V for k in model.K))

    def cost_rule_reschedule(model):
        return (sum(model.f[i, j] * model.z[i, j] for i, j in model.E) +
                sum(model.phi[i] * model.zeta[i] for i in model.V) +
                sum(model.c[i, j, k] * model.y_u[i, j, k] + 2 * model.c[i, j, k] * model.y_o[i, j, k] for i, j
                    in model.E for k in
                    model.K) +
                sum(model.h[i, k] * model.I[i, k] +
                    model.e[i, k] * model.L_u[i, k] + 2 * model.e[i, k] * model.L_o[i, k] +
                    model.rho_I[i, k] * model.delta_I[i, k] +
                    model.rho_d[i, k] * model.delta_d[i, k] for i in model.V for k in model.K))
    if reschedule:
        model.cost = pyo.Objective(rule=cost_rule_reschedule)
    else:
        model.cost = pyo.Objective(rule=cost_rule)

    # model.profit = pyo.Objective()

    def flow_rule(model, i, j, k):
        return model.y[i, j, k] == model.y_u[i, j, k] + model.y_o[i, j, k]

    def prod_rule(model, i, k):
        return model.L[i, k] == model.L_u[i, k] + model.L_o[i, k]

    # link capacity
    def link_cap_rule1(model, i, j):
        return sum(model.y_o[i, j, k] for k in model.K) <= 0.3 * model.u[i, j] * model.z[i, j]

    # production capacity
    def prod_cap_rule1(model, i):
        return sum(model.L_o[i, k] for k in model.K) <= 0.3 * model.Lmax[i] * model.zeta[i]

    # link capacity
    def link_cap_rule2(model, i, j):
        return sum(model.y_u[i, j, k] for k in model.K) <= model.u[i, j] * model.z[i, j]

    # production capacity
    def prod_cap_rule2(model, i):
        return sum(model.L_u[i, k] for k in model.K) <= model.Lmax[i] * model.zeta[i]

    if reschedule:
        model.flow_rule = pyo.Constraint(model.E, model.K, rule=flow_rule)
        model.prod_rule = pyo.Constraint(model.V, model.K, rule=prod_rule)
        model.link_capacity1 = pyo.Constraint(model.E, rule=link_cap_rule1)
        model.prod_capacity1 = pyo.Constraint(model.V, rule=prod_cap_rule1)
        model.link_capacity2 = pyo.Constraint(model.E, rule=link_cap_rule2)
        model.prod_capacity2 = pyo.Constraint(model.V, rule=prod_cap_rule2)

    # flow balance
    def balance_rule(model, i, k):
        return (sum(model.y[i, j, k] for _, j in model.E if _ == i) - sum(
            model.y[j, i, k] for j, _ in model.E if _ == i) + sum(
            model.r[k, k1] * model.p[i, k1] * model.L[i, k1] for k1 in model.K) - model.p[i, k] *
                model.L[i, k] == model.x[i, k] + model.I_0[i, k] - model.I[i, k])

    model.flow_balance = pyo.Constraint(model.V, model.K, rule=balance_rule)

    # Remove the over-capacity parameter when generating initial plans

    # link capacity
    def link_cap_rule(model, i, j):
        return sum(model.y[i, j, k] for k in model.K) <= model.u[i, j] * model.z[i, j]

    # production capacity
    def prod_cap_rule(model, i):
        return sum(model.L[i, k] for k in model.K) <= model.Lmax[i] * model.zeta[i]

    if not reschedule:
        model.link_capacity = pyo.Constraint(model.E, rule=link_cap_rule)
        model.prod_capacity = pyo.Constraint(model.V, rule=prod_cap_rule)


    # penalty terms
    def demand_pel_rule(model, i, k):
        return model.delta_d[i, k] >= model.x[i, k] - model.d[i, k]

    model.demand_penalty = pyo.Constraint(model.V, model.K, rule=demand_pel_rule)

    def demand_rule(model, i, k):
        return model.delta_d[i, k] <= 0.1

    model.demand_rule = pyo.Constraint(model.V_mfg, model.K, rule=demand_rule)

    def inv_pel_rule(model, i, k):
        return model.delta_I[i, k] >= model.I_s[i, k] - model.I[i, k]

    model.inventory_penalty = pyo.Constraint(model.V, model.K, rule=inv_pel_rule)

    # TODO: ADD DISRUPTION REACTIONS

    return model


class SinglePeriod:

    def __init__(self, exist_G=False, soft=True, reschedule=False):
        self.model = create_model(reschedule)
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

            self.model.linkChange_penalty_2 = pyo.Constraint(self.model.E, rule=edge_pel_rule2)

            # def remove_agent(model, i):
            #     return model.zeta[i] <= sum(model.L_u[i, k] + model.L_o[i, k] for k in model.K)
            #
            # self.model.remove_constraint = pyo.Constraint(self.model.V, rule=remove_agent)


            self.model.Rho = pyo.Param(initialize=0)
            self.model.cost.deactivate()

            def cost_networkChange_rule(model):
                return (sum(model.f[i, j] * model.z[i, j] for i, j in model.E) +
                        sum(model.phi[i] * model.zeta[i] for i in model.V) +
                        sum(model.c[i, j, k] * model.y_u[i, j, k] + 2 * model.c[i, j, k] * model.y_o[i, j, k] for i, j
                            in model.E for k in
                            model.K) +
                        # sum(model.c[i, j, k] * model.y[i, j, k] for i, j in model.E for k in model.K) +
                        sum(model.h[i, k] * model.I[i, k] +
                            model.e[i, k] * model.L_u[i, k] + 2 * model.e[i, k] * model.L_o[i, k] +
                            # model.e[i, k] * model.L[i, k] +
                            model.rho_I[i, k] * model.delta_I[i, k] +
                            model.rho_d[i, k] * model.delta_d[i, k] for i in model.V for k in model.K) +
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

    def solve(self, solver='gurobi', tee=True, case_name="initial"):
        opt = pyo.SolverFactory(solver)
        # opt.options['Presolve'] = 0
        results = {}

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

                print(case_name)
                print("The production cost is: " + str(prodCost))
                print("The transportation cost is: " + str(transCost))
                results['Production cost'] = float(prodCost)
                results['Flow cost'] = float(transCost)

                if abs(penalty_demand) < 1e-5:
                    print("All demands are satisfied.")
                else:
                    print("Penalty cost for demand lost: " + str(penalty_demand))
                    print("Unmet demand: ")
                    for k in self.instance.K:
                        for v in self.instance.V:
                            if pyo.value(self.instance.delta_d[v, k]) > 1e-4:
                                print(str((v, k)) + ": " + str(pyo.value(self.instance.delta_d[v, k])))
                                # print(str((v, k)) + ": " + str(pyo.value(self.instance.x[v, k])))

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
                                if pyo.value(self.instance.zeta[i]) > 1e-4:

                                    print(str(i) + ": Added")
                                else:
                                    print(str(i) + ": Removed")
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
                production = []
                for k in self.instance.K:
                    for v in self.instance.V:
                        if abs(pyo.value(self.instance.L[v, k])) > 1e-8:
                            # print(str((v, k)) + ": " + str(pyo.value(self.instance.L[v, k])))
                            prod = {'Agent': v, "Product": k, "Value": float(pyo.value(self.instance.L[v, k]))}
                            production.append(prod)
                results['Productions'] = production


                print("Flows:")
                flows = []
                for k in self.instance.K:
                    for link in self.instance.E:
                        if abs(pyo.value(self.instance.y[link, k])) > 1e-8:
                            # print(str(link + (k,)) + ": " + str(pyo.value(self.instance.y[link, k])))
                            fl = {'Source': link[0], "Dest": link[1], "Product": k, "Value": float(pyo.value(self.instance.y[link, k]))}
                            flows.append(fl)
                results['Flows'] = flows

                if case_name != "initial":
                    over_production = []
                    for k in self.instance.K:
                        for v in self.instance.V:
                            if abs(pyo.value(self.instance.L_o[v, k])) > 1e-8:
                                prod = {'Agent': v, "Product": k, "Value": float(pyo.value(self.instance.L_o[v, k]))}
                                over_production.append(prod)
                    results['OverProductions'] = over_production

                    print("Flows:")
                    over_flows = []
                    for k in self.instance.K:
                        for link in self.instance.E:
                            if abs(pyo.value(self.instance.y_o[link, k])) > 1e-8:
                                # print(str(link + (k,)) + ": " + str(pyo.value(self.instance.y[link, k])))
                                fl = {'Source': link[0], "Dest": link[1], "Product": k,
                                      "Value": float(pyo.value(self.instance.y_o[link, k]))}
                                over_flows.append(fl)
                    results['OverFlows'] = over_flows

                with open('CentralizedResults/%s.json' % case_name, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=4)

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
