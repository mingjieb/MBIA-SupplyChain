#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

from Distributed.agent.agent import Agent


class TransportationAgent(Agent):
    def __init__(self, name):
        Agent.__init__(self, name, "Transportation")
        self.flow = dict()
        self.flow_change = 0
        self.flow_added = 0
    def update_flow(self, flow, change):
        try:
            self.flow[flow] += change
        except:
            self.flow[flow] = change
        if self.flow[flow] - 0 < 0.1:
            self.flow.pop(flow)
    # agent checks its current knowledge for response
    def check_request(self, requestingAgent, product, unit):
        # TODO: determine the amount of product it can provide
        if product in self.inventory.keys():
            if unit <= self.inventory[product]:
                self.response(requestingAgent, product, unit)
                return True
            else:
                new_need = unit - self.inventory[product]
                if self.name != "Inventory":
                    print(self.name, "needs more product", product, ":", new_need)
                    req = self.request(product, new_need, self.environment)
                    if req:
                        self.response(requestingAgent, product, unit)
                        return True

        if "Production" in self.capability.keys() and product in list(self.capability["Production"]):
            new_need = self.find_need(unit)
            print(self.name, "needs", new_need, "for producing", product, ":", unit)
            req = self.request(new_need[0], new_need[1], self.environment)
            if req:  # find enough material for production
                self.production[(str(self.name), str(product))] = unit
                self.response(requestingAgent, product, unit)
                return True
        return False

    def get_available_capacity(self, start, end):
        capacity = self.capability.characteristics["Transportation"][(start, end)]["Capacity"][0]
        used_capacity = 0
        for key in self.flow.keys():
            if start == key[0] and end == key[1]:
                used_capacity += self.flow[key]

        return capacity-used_capacity

