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


class ManufacturingAgent(Agent):
    def __init__(self, name):
        Agent.__init__(self, name, "Manufacturing Supplier")
        self.production = dict()
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
            # if len(p) >= unit:
                bid_response.append(response)
        return bid_response

    # Get the price of each product
    def get_price(self, tp_cost, unit, product, cap):
        # TODO: decision making for price of each product
        cost = self.capability["Production"][product]["Cost"] + tp_cost
        pd = 0
        for key in self.production.keys():
            pd += self.production[key]
        production_cap = self.capability["Production"][product]["Maximum"] - pd
        limit = min(production_cap, cap)
        if unit <= limit:
            price = [cost for i in range(int(unit))]
        else:
            price = [cost for i in range(int(limit))]
        return price

    # Get the price of each product
    def get_supply_date(self, tp_time, unit, product, cap):
        # TODO: decision making for supply date of each product
        # supply_date = [tp_time for i in range(unit)]
        pd = 0
        for key in self.production.keys():
            pd += self.production[key]
        production_cap = self.capability["Production"][product]["Maximum"] - pd
        limit = min(production_cap, cap)
        if unit <= limit:
            supply_date = [1 for i in range(int(unit))]
        else:
            supply_date = [1 for i in range(int(limit))]
        return supply_date

    # Check whether need to propagate response if the agent is selected
    def propagate_request(self, product, unit, due_date):

        # TODO: check inventory first
        if unit > self.inventory[product]:
            # print(self.name, "needs more product", product, ":", provide_unit - self.inventory[product])
            # for agent in self.environment:
            #     if "Inventory" in agent.name:
            #         unit_from_IA = provide_unit - self.inventory[product]
            #         self.request(product, unit_from_IA, self.environment)
            pass

        if product in list(self.capability["Production"]):
            unit_material = self.find_need(unit, product)
            self.demand[str(product)] = unit_material
            self.due_date = due_date
            for material in unit_material:
                print(colored("Propagation:", 'blue'), self.name, "needs", material, "for producing", product, ":", unit)
                self.request(material[0], material[1], self.environment)

    # calculate the amount of material for producing the requested product
    def find_need(self, requestUnit, product):
        material_list = self.capability["Production"][product]["Material"]
        need_material = []
        for m in material_list.keys():
            need = requestUnit * material_list[m]
            need_material.append((m, need))
        return need_material

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

    # TODO: optimization model of tier manufacturing supplier agent
    def decision_making(self, bid_response):
        model = gp.Model('MfgDecisionMaking')
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

    # agent checks its current knowledge for response for losing a node
    def determine_max_output(self, requestingAgent, requests):
        # determine the amount of product it can provide

        pd = 0
        for key in self.production.keys():
            pd += self.production[key]
        pd_max = self.capability["Production"][requests[0][1]]["Maximum"] - pd
        tp_max = {}
        cost = {}
        req_unit = []
        K = []
        dest = []
        requests.sort(key=lambda x:x[2])
        for req in requests:
            [TA, tp_cost, limit] = self.find_tp_lose_node(req)
            req_unit.append(req[2])
            product = req[1]
            cost[req[0], req[1]] = self.capability["Production"][product]["Cost"] + tp_cost
            if product not in K:
                K.append(product)
            if req[0] not in dest:
                dest.append(req[0])
                tp_max[req[0]] = limit
        bid_response = {"Agent": self, "TA": TA, "P_limit": pd_max, "T_limit": tp_max, "Price": cost}

        return bid_response

    def find_tp_lose_node(self, req):
        transport_response = []
        dest = req[0]
        product = req[1]
        tp_cost = 0
        limit = 100000
        for transport in self.environment:
            if transport.name == "Transportation":
                transport_response.append(transport)
                tp_cost = transport.capability[(self.name, dest)]["cost"]
                limit = transport.get_available_capacity(self.name, dest)
        return [transport_response[0], tp_cost, limit]

    # Optimize lost node
    def decision_making_lose_node(self, bid_response, bid_request):
        model = gp.Model('OEMDecisionMakingLoseNode')
        model.Params.LogToConsole = 0
        TA = {}
        for key in bid_response.keys():
            TA[key] = bid_response[key]["TA"]
        res_agents = bid_response.keys()
        dest = []
        K = {}
        request = {}
        for req in bid_request:
            request[(req[0], req[1])] = req[2]
            if req[0] not in dest:
                dest.append(req[0])
            if req[0] in K.keys():
                K[req[0]].append(req[1])
            else:
                K[req[0]] = [req[1]]

        pairs = [(i, j, k) for i in res_agents for j in dest for k in K[j]]
        x = model.addVars(pairs, vtype=GRB.INTEGER, name="flow")

        obj = model.setObjective(gp.quicksum(bid_response[i]["Price"][j, k] * x[i, j, k]
                                             for i in res_agents for j in dest for k in K[j]), GRB.MINIMIZE)

        tp_constrs = model.addConstrs((gp.quicksum(x[i, j, k] for k in K[j]) <= bid_response[i]["T_limit"][j]
                                       for i in res_agents for j in dest), name="tp_limit")
        pd_constrs = model.addConstrs((gp.quicksum(x[i, j, k] for j in dest for k in K[j]) <= bid_response[i]["P_limit"]
                                             for i in res_agents), name="pd_limit")
        demand_constrs = model.addConstrs((gp.quicksum(x[i, j, k] for i in res_agents) == request[(j, k)] for j in dest for k in K[j]), name="demand_limit")

        model.optimize()
        xsol = model.getAttr('x', x)
        selection_decision = []
        for i in res_agents:
            for j in dest:
                for k in K[j]:
                    if xsol[i, j, k]  > 0.1:
                        response = {"Agent": i, "Destination": j, "Product": k, "Unit": xsol[i, j, k], "Transportation": TA[i]}
                        selection_decision.append(response)
        return selection_decision