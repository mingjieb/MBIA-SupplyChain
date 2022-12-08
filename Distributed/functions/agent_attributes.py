#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""
import matplotlib.pyplot as plt
from Distributed.initialization import network

def calculate_attributes(agent_network, agent_name, initial_flows, initial_productions):
    ag = network.find_agent_by_name(agent_network, agent_name)
    in_degree, out_degree, com_degree = calculate_degrees(ag)
    capability_redundancy, capacity_proportion = calculate_capability_capacity(ag)
    flow_contribution = calculate_flow_contributions(ag, initial_productions)
    max_steps = get_production_steps(agent_network, ag)

    attributes = attributes_summary(in_degree, out_degree, com_degree, capability_redundancy, capacity_proportion, flow_contribution, max_steps)
    return attributes

def calculate_degrees(agent):
    inflow_agents = []
    for inflow in agent.state.inflow.keys():
        if inflow[0] not in inflow_agents:
            inflow_agents.append(inflow[0])
    in_degree = len(inflow_agents)

    outflow_agents = []
    for outflow in agent.state.outflow.keys():
        if outflow[0] not in outflow_agents:
            outflow_agents.append(outflow[0])
    out_degree = len(outflow_agents)

    com_agents = []
    for product in agent.environment.upstream_agent.keys():
        for ag in agent.environment.upstream_agent[product]:
            if ag.name not in com_agents:
                com_agents.append(ag.name)
    for product in agent.environment.downstream_agent.keys():
        for ag in agent.environment.downstream_agent[product]:
            if ag.name not in com_agents:
                com_agents.append(ag.name)
    for product in agent.environment.clustering_agent.keys():
        for ag in agent.environment.clustering_agent[product]:
            if ag.name not in com_agents:
                com_agents.append(ag.name)
    com_degree = len(com_agents)

    return in_degree, out_degree, com_degree

def calculate_capability_capacity(agent):
    capability_redundancy = {}
    capacity_proportion = {}
    for product in agent.capability.knowledge["Production"]:
        try:
            capability_redundancy[product] = len(agent.environment.clustering_agent[product])
            total_cap = 0
            for ag in agent.environment.clustering_agent[product]:
                total_cap += ag.capability.get_capacity()
            capacity_proportion[product] = agent.capability.get_capacity() / (agent.capability.get_capacity() + total_cap)
        except:
            capability_redundancy[product] = 0
            capacity_proportion[product] = 1
    return capability_redundancy, capacity_proportion

def calculate_flow_contributions(agent, initial_productions):
    flow_contribution = {}
    for prod in agent.state.production.keys():
        network_production = 0
        for key in initial_productions.keys():
            if key[1] == prod:
                network_production += initial_productions[key]
        flow_contribution[prod] = agent.state.production[prod]/network_production
    return flow_contribution

def get_production_steps(agent_network, agent):
    production_hierarchy = {}
    for product in set(agent_network.product_structure.index):
        try:
            production_hierarchy[product] = list(agent_network.product_structure.loc[product, "Needed"].values)
        except:
            production_hierarchy[product] = [agent_network.product_structure.loc[product, "Needed"]]
    final_products = [p for p in production_hierarchy.keys() if "cockpit" in p]
    production_steps = {key: set() for key in final_products}
    for key in production_steps:
        component = production_hierarchy[key].copy()
        while len(component) != 0:
            p = component.pop()
            production_steps[key].add(p)
            try:
                component += production_hierarchy[p]
            except: pass
    
    contributed_final_products = []
    for prod in agent.capability.knowledge["Production"]:
        for final_prod in production_steps:
            if (prod in production_steps[final_prod] or final_prod in agent.capability.knowledge["Production"]) and final_prod not in contributed_final_products:
                contributed_final_products.append(final_prod)

    max_steps = max(len(production_steps[final_prod]) for final_prod in contributed_final_products)
    return max_steps

def attributes_summary(in_degree, out_degree, com_degree, capability_redundancy, capacity_proportion, flow_contribution, max_steps):
    attributes = {
        'g_in': in_degree,
        'g_out': out_degree,
        'g_com': com_degree,
        'l_max': max_steps,
        'P': capability_redundancy,
        'Q': capacity_proportion,
        'F': flow_contribution
    }
    return attributes


# def plot_agent_attribute():
#
#     # nodes = [ag for key in ["Distributor", "OEM", "ManufacturingSupplier"] for ag in agent_list[key]]
#     # x_axis = [ag.name for ag in nodes]
#     # degree = [sum(ag.flow_indicator[key] for key in ag.flow_indicator.keys()) for ag in nodes]
#     # plt.bar(x_axis, degree)
#     # plt.show()
#
#     node_name = ["T4:1", "T6:2", "T3:2", "T8:3", "O1:10"]
#     ini_flow_cost = 59505.67835884318
#     ini_production_cost = 165731.68999999994
#
#     d_flow_cost = [x - ini_flow_cost for x in [58144.22292236816, 59480.19964217602, 57963.759227782386,
#                                                59493.25851738464, 61738.98604390395]]
#     c_flow_cost = [x - ini_flow_cost for x in [57762.96442379725, 59476.44150096135, 57964.059227782374,
#                                                59461.96714122662, 61487.17301098378]]
#
#     fig, ax = plt.subplots()
#     ax.plot(node_name, d_flow_cost)
#     ax.plot(node_name, c_flow_cost)
#     ax.legend(['distributed_flow_cost', 'centralized_flow_cost'])
#     # plt.plot(node_name, d_flow_cost, c_flow_cost)
#     plt.xlabel("Lost agent: degree")
#     plt.ylabel("Flow cost change")
#     plt.show()
#     d_production_cost = [x - ini_production_cost for x in [171771.58, 165931.58, 168026.58,
#                                                            165881.58, 165529.78999999998]]
#     c_production_cost = [x - ini_production_cost for x in [171621.24999999997, 165931.67999999996, 168026.67999999996,
#                                                            165881.67999999996, 165135.38]]
#
#     fig, ax = plt.subplots()
#     ax.plot(node_name, d_production_cost)
#     ax.plot(node_name, c_production_cost)
#     ax.legend(['distributed_production_cost', 'centralized_production_cost'])
#     # plt.plot(node_name, d_flow_cost, c_flow_cost)
#     plt.xlabel("Lost agent: degree")
#     plt.ylabel("Production cost change")
#     plt.show()
#
#     d_changed_flow = [0, 1, 1, 1, 6]
#     c_changed_flow = [12, 3, 1, 3, 12]
#
#     fig, ax = plt.subplots()
#     ax.plot(node_name, d_changed_flow)
#     ax.plot(node_name, c_changed_flow)
#     ax.legend(['distributed_changed_flow', 'centralized_changed_flow'])
#     # plt.plot(node_name, d_flow_cost, c_flow_cost)
#     plt.xlabel("Lost agent: degree")
#     plt.ylabel("Number of changed flow")
#     plt.show()
#
#     d_added_flow = [1, 1, 1, 2, 8]
#     c_added_flow = [3, 1, 1, 3, 12]
#
#     fig, ax = plt.subplots()
#     ax.plot(node_name, d_added_flow)
#     ax.plot(node_name, c_added_flow)
#     ax.legend(['distributed_added_flow', 'centralized_added_flow'])
#     # plt.plot(node_name, d_flow_cost, c_flow_cost)
#     plt.xlabel("Lost agent: degree")
#     plt.ylabel("Number of added flow")
#     plt.show()
#
#     d_communication = [6, 6, 6, 6, 46]
#     c_communication = [57, 52, 51, 53, 63]
#
#     fig, ax = plt.subplots()
#     ax.plot(node_name, d_communication)
#     ax.plot(node_name, c_communication)
#     ax.legend(['distributed_communication', 'centralized_communication'])
#     # plt.plot(node_name, d_flow_cost, c_flow_cost)
#     plt.xlabel("Lost agent: degree")
#     plt.ylabel("Number of communication")
#     plt.show()



