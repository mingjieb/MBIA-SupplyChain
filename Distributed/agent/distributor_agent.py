#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

import gurobipy as gp
from gurobipy import GRB
from agent.agent import Agent
from colorama import init
from termcolor import colored


class DistributorAgent(Agent):
    def __init__(self, name):
        Agent.__init__(self, name, "Distributor")
        self.inventory = dict()

    # agent checks its current knowledge for response
    def check_request(self, requestingAgent, product, unit):
        # TODO: determine the amount of product it can provide
        # Now assume provide enough to meet demand
        provide_unit = unit
        bid_response = []
        if product in self.inventory.keys():
            [TA, tp_cost, tp_time, limit] = self.find_transportation(product, provide_unit, requestingAgent)
            p = self.get_price(tp_cost, unit, product, limit)  # TODO: get price and cost
            s = self.get_supply_date(tp_time, unit, product, limit)  # TODO: get supply date
            response = {"Agent": self, "TA": TA, "Product": product, "Unit": provide_unit, "Price": p, "Supply date": s}
            if len(p) != 0:
                bid_response.append(response)
        return bid_response

    # Get the price of each product
    def get_price(self, tp_cost, unit, product, limit):
        # TODO: decision making for price of each product
        cost = tp_cost
        upper_bound = limit
        if unit <= upper_bound:
            price = [cost for i in range(int(unit))]
        else:
            price = [cost for i in range(int(upper_bound))]
        return price

    # Get the price of each product
    def get_supply_date(self, tp_time, unit, product, limit):
        # TODO: decision making for supply date of each product
        # supply_date = [tp_time for i in range(unit)]
        upper_bound = limit
        if unit <= upper_bound:
            supply_date = [1 for i in range(int(unit))]
        else:
            supply_date = [1 for i in range(int(upper_bound))]
        return supply_date

    # Check whether need to propagate response if the agent is selected
    def propagate_request(self, product, unit, due_date, lost_flow):
        # If the need more product from the upstream
        if unit > self.inventory[product]:
            # TODO: check inventory first
            # print(self.name, "needs more product", product, ":", provide_unit - self.inventory[product])
            # for agent in self.environment:
            #     if "Inventory" in agent.name:
            #         unit_from_IA = provide_unit - self.inventory[product]
            #         self.request(product, unit_from_IA, self.environment)
            unit_from_OEM = unit - self.inventory[product]
            self.demand[str(product)] = unit_from_OEM
            self.due_date = due_date
            print(colored("Propagation:", 'blue'), self.name, "needs more product", product, ":", unit_from_OEM)
            self.request(product, unit_from_OEM, self.environment, lost_flow)

    # TODO: transportation decision
    def find_transportation(self, product, unit, requestingAgent):
        transport_response = []
        tp_cost = 0
        tp_time = 1
        limit = 100000
        for transport in self.environment:
            if transport.name == "Transportation":
                transport_response.append(transport)
                # if "Manuf" not in requestingAgent.name or "Manuf" not in self.name:
                if "Part" not in requestingAgent.name or "Part" not in self.name:
                    tp_cost = transport.capability[(self.name, requestingAgent.name)]["cost"]
                    limit = transport.get_available_capacity(self.name, requestingAgent.name)
        return [transport_response[0], tp_cost, tp_time, limit]

    # TODO: optimization model of distributor agent
    def decision_making(self, bid_response):
        model = gp.Model('DistributorDecisionMaking')
        model.Params.LogToConsole = 0
        n = len(bid_response)
        pt = [len(bid_response[i]["Price"]) for i in range(n)]
        pairs = [(i, j) for i in range(n) for j in range(pt[i])]
        x = model.addVars(pairs, vtype=GRB.BINARY, name="product")
        # obj = model.setObjective(gp.quicksum(bid_response[i]["Price"][j] * x[i, j] +
        #                                      (bid_response[i]["Supply date"][j] - self.due_date) * x[i, j]
        #                                      for i in range(n) for j in range(pt[i])), GRB.MINIMIZE)
        obj = model.setObjective(gp.quicksum(bid_response[i]["Price"][j] * x[i, j]
                                             for i in range(n) for j in range(pt[i])), GRB.MINIMIZE)
        supplier_constrs = model.addConstrs((gp.quicksum(x[i, j] for j in range(pt[i])) <= pt[i]
                                             for i in range(n)), name="supplier_limit")
        demand_constrs = model.addConstrs((gp.quicksum(x[i, j] for i in range(n) for j in range(pt[i]))
                                         == self.demand[key] for key in self.demand.keys()), name="demand_limit")
        model.optimize()
        xsol = model.getAttr('x', x)
        selection_decision = []
        for i in range(n):
            if sum(xsol[i, j] for j in range(pt[i])) > 0:
                response = bid_response[i]
                response["Result"] = sum(xsol[i, j] for j in range(pt[i]))
                selection_decision.append(response)
        return selection_decision
