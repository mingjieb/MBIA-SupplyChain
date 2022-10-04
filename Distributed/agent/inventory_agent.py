#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

from agent.agent import Agent
from colorama import init
from termcolor import colored

class InventoryAgent(Agent):
    def __init__(self, name):
        Agent.__init__(self, name)
        self.inventory = dict()

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

    # TODO: should add this somewhere else
    def find_transportation(self, requestingAgent, product, unit):
        for transport in self.environment:
            if transport.name == "Transporation":
                transport.flow[(str(self.name), str(requestingAgent.name), str(product))] = unit
                return True
        return False

    # TODO: optimization model of inventory agent
    def decision_making(self):
        pass
