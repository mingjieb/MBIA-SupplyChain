#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

from agent.agent import Agent


class RawMaterialAgent(Agent):
    def __init__(self, name):
        Agent.__init__(self, name, "Raw Material Supplier")
        self.inventory = dict()
        self.supply = dict()

    # agent checks its current knowledge for response
    def check_request(self, requestingAgent, product, unit):
        # TODO: determine the amount of product it can provide
        # Now assume provide enough to meet demand
        provide_unit = unit
        bid_response = []
        if product in self.inventory.keys():
            if provide_unit <= self.inventory[product]:
                transport_list = self.find_transportation(product, provide_unit)
                for TA in transport_list:
                    p = 1  # TODO: get price and cost
                    response = {"Agent": self, "TA": TA, "Product": product, "Unit": provide_unit, "Price": p}
                    bid_response.append(response)
        return bid_response

    # TODO: transportation decision
    def find_transportation(self, product, unit):
        transport_response = []
        for transport in self.environment:
            if transport.name == "Transportation":
                transport_response.append(transport)
        return transport_response

    # TODO: optimization model of raw material supplier agent
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
