import numpy as np
import gurobipy as gp
from gurobipy import GRB
import networkx as nx
import matplotlib.pyplot as plt
from Params import *


class SinglePeriod:

    def __init__(self, params: Params):
        self.model = gp.Model('single period MILP')
        self.params = params
        self.solved = False
        self.G = nx.MultiDiGraph()

        # Define Variables
        # network flow vars
        self.y = self.model.addVars(params.E, params.K, name='flow')
        self.z = self.model.addVars(params.E, vtype=GRB.BINARY, name='link_usage')
        self.x = self.model.addVars(params.V, params.K, lb=float('-inf'), ub=0.0, name='demand_satisfied')  # negative

        # production/inventory vars
        self.L = self.model.addVars(params.V, params.K, name='run_length')
        self.zeta = self.model.addVars(params.V, vtype=GRB.BINARY, name='prodLine_usage')
        self.I = self.model.addVars(params.V, params.K, name='inventory')

        # penalty terms
        self.delta_d = self.model.addVars(params.V, params.K, name='penalty_demand')
        self.delta_I = self.model.addVars(params.V, params.K, name='penalty_inv')

        # Define Objectives
        self.cost = self.model.setObjectiveN(gp.quicksum(params.f[i, j] * self.z[i, j] for i, j in params.E) +
                                             gp.quicksum(params.phi[i] * self.zeta[i] for i in params.V) +
                                             gp.quicksum(
                                                 params.c[i, j, k] * self.y[i, j, k] for i, j in params.E for k in
                                                 params.K) +
                                             gp.quicksum(params.h[i, k] * self.I[i, k] +
                                                         params.e[i, k] * self.L[i, k] +
                                                         params.rho_I[i, k] * self.delta_I[i, k] +
                                                         params.rho_d[i, k] * self.delta_d[i, k] for i in params.V for k
                                                         in params.K), index=0)

        self.profit = self.model.setObjectiveN(
            gp.quicksum(params.Pi[i, k] * self.x[i, k] for i in params.V for k in params.K), index=1)

        # Define Constraints
        # flow balance
        self.model.addConstrs(
            (self.y.sum(i, '*', k) - self.y.sum('*', i, k) + gp.quicksum(
                params.r[k, k1] * params.p[i, k1] * self.L[i, k1] for k1 in params.K) - params.p[i, k] * self.L[i, k] ==
             self.x[i, k] +
             params.I_0[i, k] - self.I[i, k]
             for i in params.V for k in params.K), 'flow balance')

        # link capacity
        self.model.addConstrs(
            (self.y.sum(i, j, '*') <= params.u[i, j] * self.z[i, j]
             for i, j in params.E), 'link capacity'
        )

        # production capacity
        self.model.addConstrs(
            (self.L.sum(i, '*') <= params.Lmax[i] * self.zeta[i]
             for i in params.V), 'production capacity'
        )

        # penalty terms
        self.model.addConstrs((self.delta_d[i, k] >= self.x[i, k] - params.d[i, k] for i in params.V for k in params.K),
                              'penalty demand')
        self.model.addConstrs(
            (self.delta_I[i, k] >= params.I_s[i, k] - self.I[i, k] for i in params.V for k in params.K), 'penalty inv')

        # feasibility
        self.model.addConstrs((-self.x[i, k] <= - params.d[i, k] for i in params.V for k in params.K),
                              'no excessive demand')


    def solve(self):
        self.model.optimize()
        if self.model.status == GRB.OPTIMAL:
            self.solved = True
            self.output_data()
        else:
            self.diagnosis()

    def diagnosis(self):
        removed_constrs = []
        while self.model.status != GRB.OPTIMAL:
            self.model.computeIIS()
            # Print the violated constraints
            for c in self.model.getConstrs():
                if c.IISConstr:
                    print("Violated constraints: ", c)
                    removed_constrs.append(str(c))
                    self.model.remove(c)
                    break
            self.solve()
        if len(removed_constrs) != 0:
            print("Following constraints are removed: ", removed_constrs)

    def output_data(self):
        # Flow y
        print("The non-zero product flows are")
        for l in self.params.E:
            for k in self.params.K:
                if self.y[l[0], l[1], k].x > 1e-6:
                    print(str(l), "for product", str(k), ":", self.y[l[0], l[1], k].x)

        # # Inventory I
        # inventory = pd.DataFrame(columns=P, index=vertices)
        # print("The non-zero inventory is")
        # for v_p in vertices_with_products:
        #     inventory.loc[v_p[0], v_p[1]] = I[v_p].x
        #     if I[v_p].x > 1e-6:
        #         print(str(v_p), ":", I[v_p].x)
        #
        # # Added capacity Q
        # added_capacity = pd.DataFrame(columns=["Q"], index=pd.MultiIndex.from_tuples(links, names=('start', 'end')))
        # print("The non-zero added capacity is")
        # for l in links:
        #     added_capacity.loc[l, "Q"] = Q[l].x
        #     if Q[l].x > 1e-6:
        #         print(str(l), ":", Q[l].x)
        #
        # # Production p*L
        # production = pd.DataFrame(columns=P, index=vertices)
        # print("The non-zero production is")
        # for v_p in vertices_with_products:
        #     production.loc[v_p[0], v_p[1]] = a[v_p].x
        #     if a[v_p].x > 1e-6:
        #         print(str(v_p), ":", a[v_p].x)

    def visualize(self):
        if not self.solved:
            self.G.add_edges_from(self.params.E)
            self.G.add_nodes_from(self.params.V)
        else:
            for i in self.params.V:
                produced_unit = {}
                demand_unit = {}
                for k in self.params.K:
                    if self.L[i, k].x > 1e-6:
                        produced_unit.update({k: self.params.p[i, k] * self.L[i, k].x})
                    if self.x[i, k].x < -1e-6:
                        demand_unit.update({k: -self.x[i, k].x})
                # NEED REVISION. CURRENTLY DOES NOT CONSIDER BOTH PRODUCTION AND DEMAND AT THE SAME NODE
                if len(produced_unit) > 0:
                    self.G.add_node(i, type='production', product=produced_unit)
                elif len(demand_unit) > 0:
                    self.G.add_node(i, type='buyer', product=demand_unit)
                else:
                    self.G.add_node(i)

            for i, j in self.params.E:
                for k in self.params.K:
                    if self.y[i, j, k].x > 1e-6:
                        self.G.add_edge(i, j, product=k, flow=self.y[i, j, k].x)

            pos = nx.random_layout(self.G)
            nx.draw(self.G, pos=pos, with_labels=True)

            if self.solved is True:
                edge_labels = dict([((i, j), str(d['product']) + ': ' + str(d['flow']))
                                    for i, j, d in self.G.edges(data=True)])
                nx.draw_networkx_edge_labels(self.G, pos=pos, edge_labels=edge_labels)

            #plt.tight_layout()
            plt.axis("off")
            plt.show()
