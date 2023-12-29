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
<<<<<<< Updated upstream
=======
        self.over_flow = dict()
        self.flow_time = dict()
>>>>>>> Stashed changes
        self.flow_change = 0
        self.flow_added = 0
    def update_flow(self, flow, change):
        try:
            self.flow[flow] += change
        except:
            self.flow[flow] = change
        if self.flow[flow] - 0 < 0.1:
            self.flow.pop(flow)
            # self.flow_time.pop(flow)
    def update_over_flow(self, flow, change):
        try:
            self.over_flow[flow] += change
        except:
            self.over_flow[flow] = change
        if self.over_flow[flow] - 0 < 0.1:
            self.over_flow.pop(flow)
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

    def get_available_capacity(self, start, end, overcapacity_multiplier):
        capacity = self.capability.characteristics["Transportation"][(start, end)]["Capacity"] * overcapacity_multiplier
        used_capacity = 0
        for key in self.flow.keys():
            if start == key[0] and end == key[1]:
                used_capacity += self.flow[key]

        return capacity-used_capacity

    def get_normal_available_capacity(self, start, end):
        capacity = self.capability.characteristics["Transportation"][(start, end)]["Capacity"]
        used_capacity = 0
        for key in self.flow.keys():
            if start == key[0] and end == key[1]:
                used_capacity += self.flow[key]

        return max(0, capacity-used_capacity)

    def have_capacity(self, start, end):
        if (start, end) not in self.capability.knowledge["Transportation"]:
            return False
        capacity = self.capability.characteristics["Transportation"][(start, end)]["Capacity"]
        used_capacity = 0
        for key in self.flow.keys():
            if start == key[0] and end == key[1]:
                used_capacity += self.flow[key]

        if abs(1.3*capacity - used_capacity) > 0.5:
            return True
        else:
            return False

