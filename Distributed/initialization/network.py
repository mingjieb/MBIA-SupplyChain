#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

from Distributed.agent import customer_agent, distributor_agent, manufacturing_agent, oem_agent, \
    raw_material_agent, transportation_agent
import pandas as pd


# Information in the network
def __init__(self):
    self.agent_list = dict()
    self.link_list = list()
    self.occurred_communication
    self.product_structure


# Agent-based supply chain network initialization
def initialize_agent_network(self):
    # Read xlsx file to create all the agents and add them to the network
    filename = 'initialization/TASE_Setup.xlsx'
    info = pd.read_excel(filename, sheet_name=None)
    self.product_structure = info["ProductStructure"].set_index(['Product'])

    agent_initialization(self, info)

    return self


# Create agent network from the initialization json file
def agent_initialization(self, info):
    # Initialize the network
    self.agent_list = {
        "Customer": [],
        "Assembly": [],
        "TierSupplier": [],
        "Transportation": []
    }

    ag_set = set(info["Agent"]["AgentName"])
    for name in ag_set:
        if "sup" in name:
            ag = manufacturing_agent.ManufacturingAgent(name)
            self.agent_list["TierSupplier"].append(ag)
        elif "assy" in name:
            ag = oem_agent.OEMAgent(name)
            self.agent_list["Assembly"].append(ag)
        elif "Customer" in name:
            ag = customer_agent.CustomerAgent(name)
            self.agent_list["Customer"].append(ag)

    self.agent_list["Transportation"].append(transportation_agent.TransportationAgent("Transportation"))

    build_capability_model(self, info)

    # Initialize communication network
    build_environment_model(self, info)


# Build the initial environment model for each agent
# Environment model contains a list of agents that one agent can communicate
def build_environment_model(self, info):
    transport_link = info["Link"].set_index(['Source', 'Destination'])
    product_type = info["Agent"].set_index(['ProductType'])
    for link in transport_link.index:
        source_ag = find_agent_by_name(self, link[0])
        dest_ag = find_agent_by_name(self, link[1])

        if 'Customer' in dest_ag.name:
            for product in dest_ag.demand.keys():
                if source_ag.capability.have_capability("Production", product):
                    source_ag.environment.add_environment('downstream', product, dest_ag)
                    dest_ag.environment.add_environment('upstream', product, source_ag)
        else:
            for product in dest_ag.capability.characteristics["Production"]:
                for need in dest_ag.capability.characteristics["Production"][product]["Material"].keys():
                    if source_ag.capability.have_capability("Production", need):
                        source_ag.environment.add_environment('downstream', need, dest_ag)
                        dest_ag.environment.add_environment('upstream', need, source_ag)

    product_set = set(product_type.index)
    for product in product_set:
        try:
            cluster_name = product_type.loc[product, "AgentName"].tolist()
        except: pass
        else:
            agent_cluster = []
            for name in cluster_name:
                if "Customer" not in name:
                    agent_cluster.append(find_agent_by_name(self, name))
            for ag1 in agent_cluster:
                for ag2 in agent_cluster:
                    if ag1.name != ag2.name:
                        ag1.environment.add_environment('clustering', product, ag2)
                        ag2.environment.add_environment('clustering', product, ag1)

# Build the initial capability model for each agent
# Capability model contains the functionalities of one agent in the supply chain network and
# a list of products under each functionality
def build_capability_model(self, info):
    agent_product = info["Agent"].set_index(['AgentName', 'ProductType'])
    transport_link = info["Link"].set_index(['Source', 'Destination'])
    product_structure = info["ProductStructure"].set_index(['Product', 'Needed'])
    for idx in agent_product.index:
        ag = find_agent_by_name(self, idx[0])
        if 'Customer' in ag.name:
            ag.demand[idx[1]] = agent_product.loc[idx, "Demand"][0]
        else:
            prod_char = {}
            prod_char["Cost"] = agent_product.loc[idx, 'ProductionCost'][0]
            prod_char["Capacity"] = agent_product.loc[idx, 'ProductionCapacity'][0]
            prod_char["Material"] = {}
            for need in product_structure.index:
                if need[0] == idx[1]:
                    prod_char["Material"][need[1]] = product_structure.loc[need, "Amount"]
                
            ag.capability.add_capability("Production", idx[1], prod_char)
            ag.capability.add_capability("Inventory", idx[1], {'Cost': 0, 'Capacity': 0})

    tp = find_agent_by_name(self, "Transportation")
    for link in transport_link.index:
        tp.capability.knowledge["Transportation"].append((link[0], link[1]))
        tp.capability.characteristics["Transportation"][(link[0], link[1])] = \
            {"Cost": transport_link.loc[link, "TransportCost"],
             "Capacity": transport_link.loc[link, "TransportCapacity"]}


def find_agent_by_name(self, name):
    for key in self.agent_list:
        for ag in self.agent_list[key]:
            if name == ag.name:
                return ag