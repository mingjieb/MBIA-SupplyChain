#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

import gurobipy as gp
from gurobipy import GRB
from Distributed.agent.agent import Agent
from colorama import init
from termcolor import colored


class CustomerAgent(Agent):
    def __init__(self, name):
        Agent.__init__(self, name, "Customer")
        self.demand = dict()

    # TODO: optimization model of customer agent
    def decision_making(self, bid_response):
        model = gp.Model('CustomerDecisionMaking')
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
