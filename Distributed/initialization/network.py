#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""
import sys

sys.path.append("/agent")
from agent import customer_agent, distributor_agent, inventory_agent, manufacturing_agent, oem_agent, \
    raw_material_agent, transportation_agent
from initialization.params import Params
import json
import pandas as pd


# Information in the network
def __init__(self):
    self.agent_network = dict()


# Agent-based supply chain network initialization
def initialize_agent_network(self):
    # Read json file to create all the agents and add them to the network
    params = []
    agent_initialization(self, params)

    # # Read the params file to add initial known knowledge to each agent
    # knowledge_base_initialization(self)

    return self.agent_network


# Initialize the prior known knowledge for each agent
# TODO: write xlsx file for agent parameters, write json file for capability and environment description
def knowledge_base_initialization(self):
    with open('initializationFiles/Customer.json') as f:
        data = json.load(f)
    for CA in self.agent_network["customer"]:
        CA.demand = {"Final Product": 44}
    for DA in self.agent_network["distributor"]:
        if DA.name == "distributor1":
            DA.inventory = {"Final Product": 6}
        else:
            DA.inventory = {"Final Product": 6}
    # for IA in self.agent_network["inventory"]:
    #     IA.inventory = {"Final Product": 3}
    for OEM in self.agent_network["oem"]:
        OEM.inventory = {"Final Product": 0}
    for MA in self.agent_network["manufacturing"]:
        # if MA.name == "Manufacturing Supplier1":
        #     MA.inventory = {"Component1": 0}
        # elif MA.name == "Manufacturing Supplier2":
        #     MA.inventory = {"Component2": 0}
        # else:
        #     MA.inventory = {"Component2": 0}
        MA.inventory = {"Component": 0}
    for RMA in self.agent_network["raw_material"]:
        if RMA.name == "Raw Material Supplier1":
            RMA.inventory = {"Raw Material1": 100}
        elif RMA.name == "Raw Material Supplier2":
            RMA.inventory = {"Raw Material1": 100}
        else:
            RMA.inventory = {"Raw Material2": 100}

    build_capability_model(self)
    build_environment_model(self)


# Create agent network from the initialization json file
def agent_initialization(self, Params):
    # Initialize the network
    self.agent_network = {
        "Customer": [],
        "Distributor": [],
        "OEM": [],
        "ManufacturingSupplier": [],
        "Transportation": []
    }

    # Create customer agent
    with open('initialization/initializationFiles/Customer.json') as f:
        customer = json.load(f)
    f.close()
    for agent_name in customer.keys():
        ag = customer_agent.CustomerAgent(agent_name)
        # ag.demand = customer[agent_name]["Demand"]
        ag.communication_nodes = customer[agent_name]["CommunicationNodes"]
        ag.flow_indicator = {key: 0 for key in ag.communication_nodes}
        self.agent_network["Customer"].append(ag)

    # Create distributor agent
    with open('initialization/initializationFiles/Distributor.json') as f:
        distributor = json.load(f)
    f.close()
    for agent_name in distributor.keys():
        ag = distributor_agent.DistributorAgent(agent_name)
        ag.inventory = distributor[agent_name]["Inventory"]
        ag.capability = {"Inventory": distributor[agent_name]["Inventory"].keys()}
        ag.communication_nodes = distributor[agent_name]["CommunicationNodes"]
        ag.flow_indicator = {key: 0 for key in ag.communication_nodes}
        self.agent_network["Distributor"].append(ag)

    # Create OEM agent
    with open('initialization/initializationFiles/OEM.json') as f:
        oem = json.load(f)
    f.close()
    for agent_name in oem.keys():
        ag = oem_agent.OEMAgent(agent_name)
        ag.inventory = oem[agent_name]["Inventory"]
        ag.capability = {"Production": oem[agent_name]["Production"],
                         "Inventory": oem[agent_name]["Inventory"].keys()}
        ag.communication_nodes = oem[agent_name]["CommunicationNodes"]
        ag.flow_indicator = {key: 0 for key in ag.communication_nodes}
        self.agent_network["OEM"].append(ag)

    # Create manufacturing supplier agent
    with open('initialization/initializationFiles/ManufacturingSupplier.json') as f:
        manufacturing = json.load(f)
    f.close()
    for agent_name in manufacturing.keys():
        ag = manufacturing_agent.ManufacturingAgent(agent_name)
        ag.inventory = manufacturing[agent_name]["Inventory"]
        ag.capability = {"Production": manufacturing[agent_name]["Production"],
                         "Inventory": manufacturing[agent_name]["Inventory"].keys()}
        ag.communication_nodes = manufacturing[agent_name]["CommunicationNodes"]
        ag.flow_indicator = {key: 0 for key in ag.communication_nodes}
        self.agent_network["ManufacturingSupplier"].append(ag)

    # Create raw material supplier agent
    # with open('initialization/initializationFiles/RawMaterial.json') as f:
    #     raw_material = json.load(f)
    # f.close()
    # for agent_name in customer.keys():
    #     ag = raw_material_agent.RawMaterialAgent(agent_name)
    #     ag.inventory = raw_material[agent_name]["Inventory"]
    #     ag.environment = raw_material[agent_name]["CommunicationNodes"]
    #     self.agent_network["RawMaterial"].append(ag)

    # Create transportation agent
    with open('initialization/initializationFiles/Transportation.json') as f:
        transportation = json.load(f)
    f.close()
    for agent_name in transportation.keys():
        ag = transportation_agent.TransportationAgent(agent_name)
        # ag.capability = {"Transport": transportation[agent_name]["Transport"].keys()}
        ag.capability = read_transportation(self)
        self.agent_network["Transportation"].append(ag)

    # Initialize communication network
    build_environment_model(self)


# Build the initial environment model for each agent
# Environment model contains a list of agents that one agent can communicate
# TODO: build the environment model to agent knowledge base
def build_environment_model(self):
    for key in self.agent_network:
        for ag in self.agent_network[key]:
            add_environment_agent(self, ag, ag.communication_nodes)


# Find the agents that have the certain name
def add_environment_agent(self, agent, environment_list):
    for key in self.agent_network:
        for ag in self.agent_network[key]:
            if ag.name in environment_list:
                agent.environment.append(ag)


# Build the initial capability model for each agent
# Capability model contains the functionalities of one agent in the supply chain network and
# a list of products under each functionality
# TODO: build the capability model to agent knowledge base
def build_capability_model(self):
    for DA in self.agent_network["distributor"]:
        DA.capability = {"Inventory": ["Final Product"]}
    # for IA in self.agent_network["inventory"]:
    #     IA.capability = {"Inventory": ["Final Product"]}
    for OEM in self.agent_network["oem"]:
        OEM.capability = {"Production": ["Final Product"], "Inventory": ["Final Product"]}
    for MA in self.agent_network["manufacturing"]:
        # if MA.name == "Manufacturing Supplier1":
        #     MA.capability = {"Production": ["Component1"], "Inventory": ["Component1"]}
        # else:
        #     MA.capability = {"Production": ["Component2"], "Inventory": ["Component2"]}
        MA.capability = {"Production": ["Component"], "Inventory": ["Component"]}
    for RMA in self.agent_network["raw_material"]:
        if RMA.name == "Raw Material Supplier3":
            RMA.capability = {"Inventory": ["Raw Material2"]}
        else:
            RMA.capability = {"Inventory": ["Raw Material1"]}
    for TA in self.agent_network["transportation"]:
        TA.capability = {"Transportation": ["Final Product", "Component", "Component2", "Raw Material1",
                                            "Raw Material2", "Raw Material3"]}


def read_transportation(self):
    filename = 'initialization/Conference Case - New.xlsx'
    info = pd.read_excel(filename, sheet_name='00_LL', index_col=0)
    start_vertex = list(info.index)
    end_vertex = list(info.get("destinationStage"))
    cost = list(info.get("transportCost"))
    capacity = list(info.get("transportCap"))
    transport_attributes = {}
    for i in range(len(start_vertex)):
        data = {}
        data["cost"] = cost[i]
        data["capacity"] = capacity[i]
        transport_attributes[(str(start_vertex[i]), str(end_vertex[i]))] = data
    return transport_attributes
