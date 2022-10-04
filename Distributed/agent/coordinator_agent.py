#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

from agent.agent import Agent


class CoordinatorAgent(Agent):
    def __init__(self, name):
        Agent.__init__(self, name, "Coordinator")

    # Check whether need to propagate response if the agent is selected
    def propagate_request(self, product, unit):
        # If the need more product from the upstream
        if unit > self.inventory[product]:
            # TODO: check inventory first
            # print(self.name, "needs more product", product, ":", provide_unit - self.inventory[product])
            # for agent in self.environment:
            #     if "Inventory" in agent.name:
            #         unit_from_IA = provide_unit - self.inventory[product]
            #         self.request(product, unit_from_IA, self.environment)
            unit_from_OEM = unit - self.inventory[product]
            print(self.name, "needs more product", product, ":", unit_from_OEM)
            self.request(product, unit_from_OEM, self.environment)

    # TODO: optimization model of distributor agent

    def decision_making(self, bid_response):
        cost = bid_response[0]["Price"]
        selected_agent = bid_response[0]["Agent"]
        for response in bid_response:
            if response["Price"] < cost:
                cost = response["Price"]
                selected_agent = response["Agent"]
        # Assume each agent can provide enough product
        selection_decision = []
        for response in bid_response:
            if response["Agent"] == selected_agent:
                selection_decision.append(response)
        return selection_decision
