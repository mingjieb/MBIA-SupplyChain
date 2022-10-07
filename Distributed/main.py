#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

import sys

from algorithms.check_flow_difference import check_centralized_difference

sys.path.append("/agent")
sys.path.append("/initialization")
sys.path.append("/algorithms")
from initialization import network
from algorithms import check_flow_difference
from colorama import init
from termcolor import colored
import matplotlib.pyplot as plt


def communication(customerAgent):
    for product in customerAgent.demand.keys():
        customerAgent.request(product, customerAgent.demand[product], customerAgent.environment)
    # customerAgent.decision_making(bid)


def disruption_adaptation(agent_list):
    # hard code to define a broken agent, lost product, lost amounts
    lost_production = []
    lost_flow = []

    # disruption effects identification
    for key in agent_list.keys():
        for ag in agent_list[key]:

            # identify disruption of losing a node
            # if ag.name == "Manuf_01":
            if ag.name == "Part_03":
                disrupted_node = ag
                lost_production.append(ag.production.copy())
                ag.production.clear()
                for transportation in agent_list["Transportation"]:

                    for item in transportation.flow.items():
                        if ag.name in item[0]:
                            lost_flow.append(item)
                    for f in lost_flow:
                        transportation.flow.pop(f[0])
                        if disrupted_node.name == f[0][1]:  # inflow to lost node
                            for k in agent_list.keys():
                                for a in agent_list[k]:
                                    if a.name == f[0][0]:
                                        a.production[(a.name, f[0][2])] -= f[1]

            # identify disruption of new demand
            # if ag.name == "Retail_09":
            #     ag.demand['marinatedBeef'] = 300
            #     disrupted_node = ag
            #     ag.request('marinatedBeef', 300, ag.environment, lost_flow)

    # print the disruption
    print(colored("Disrupted agent:", 'magenta'), disrupted_node.name)
    print(colored("Lost production:", 'magenta'))
    for p in lost_production:
        print(p)
    print(colored("Lost flow:", 'magenta'))
    for f in lost_flow:
        print(f)

    # start reconfiguration
    disrupted_node.adaptation(agent_list, lost_production, lost_flow)


def assign_initial_flow(agent_list):
    # hard code to assign the flow and production to agent
    for tp in agent_list["Transportation"]:
        tp.flow = {('Manuf_01', 'Wholesale_02', 'groundBeef'): 1881.0,
                   ('Wholesale_01', 'Retail_02', 'groundBeef'): 106.0,
                   ('Manuf_02', 'Wholesale_01', 'groundBeef'): 53.0,
                   ('Manuf_01', 'Wholesale_01', 'groundBeef'): 300.0,
                   ('Wholesale_02', 'Retail_05', 'groundBeef'): 1688.0,
                   ('Wholesale_02', 'Retail_03', 'groundBeef'): 193.0,
                   ('Wholesale_01', 'Retail_01', 'groundBeef'): 247.0,
                   ('Part_05', 'Manuf_02', 'package_1'): 3947.0,
                   ('Part_05', 'Manuf_03', 'package_1'): 1137.0,
                   ('Part_05', 'Manuf_01', 'package_1'): 1904.0,
                   ('Part_02', 'Manuf_01', 'rawBeef'): 722.0,
                   ('Part_04', 'Manuf_02', 'rawBeef'): 4000.0,
                   ('Part_03', 'Manuf_03', 'rawBeef'): 1137.0,
                   ('Part_03', 'Manuf_01', 'rawBeef'): 3363.0,
                   ('Manuf_03', 'Wholesale_04', 'marinatedBeef'): 1137.0,
                   ('Manuf_02', 'Wholesale_04', 'marinatedBeef'): 2500.0,
                   ('Wholesale_03', 'Retail_04', 'marinatedBeef'): 289.0,
                   ('Wholesale_04', 'Retail_07', 'marinatedBeef'): 2782.0,
                   ('Wholesale_03', 'Retail_06', 'marinatedBeef'): 2062.0,
                   ('Manuf_02', 'Wholesale_03', 'marinatedBeef'): 1447.0,
                   ('Wholesale_04', 'Retail_08', 'marinatedBeef'): 1855.0,
                   ('Manuf_01', 'Wholesale_04', 'marinatedBeef'): 1000.0,
                   ('Manuf_01', 'Wholesale_03', 'marinatedBeef'): 904.0,
                   ('Part_01', 'Manuf_01', 'package_0'): 2181.0,
                   ('Part_01', 'Manuf_02', 'package_0'): 53.0,
                   ('Part_08', 'Manuf_01', 'seasoning'): 2000.0,
                   ('Part_06', 'Manuf_01', 'seasoning'): 1863.0,
                   ('Part_08', 'Manuf_02', 'seasoning'): 1863.0,
                   ('Part_06', 'Manuf_02', 'seasoning'): 2137.0,
                   ('Part_07', 'Manuf_01', 'seasoning'): 222.0,
                   ('Part_08', 'Manuf_03', 'seasoning'): 1137.0}

        for key in tp.flow.keys():
            start = get_agent(key[0], agent_list)
            end = get_agent(key[1], agent_list)
            start.flow_indicator[key[1]] = 1
            end.flow_indicator[key[0]] = 1

    for mfg in agent_list["ManufacturingSupplier"]:
        if mfg.name == "Part_01":
            mfg.production = {('Part_01', 'package_0'): 2234.0}
        if mfg.name == "Part_02":
            mfg.production = {('Part_02', 'rawBeef'): 722.0}
        if mfg.name == "Part_03":
            mfg.production = {('Part_03', 'rawBeef'): 4500.0}
        if mfg.name == "Part_04":
            mfg.production = {('Part_04', 'rawBeef'): 4000.0}
        if mfg.name == "Part_05":
            mfg.production = {('Part_05', 'package_1'): 6988.0}
        if mfg.name == "Part_06":
            mfg.production = {('Part_06', 'seasoning'): 4000.0}
        if mfg.name == "Part_07":
            mfg.production = {('Part_07', 'seasoning'): 222.0}
        if mfg.name == "Part_08":
            mfg.production = {('Part_08', 'seasoning'): 5000.0}

    for oem in agent_list["OEM"]:
        if oem.name == "Manuf_01":
            oem.production = {('Manuf_01', 'groundBeef'): 2181.0,
                              ('Manuf_01', 'marinatedBeef'): 1904.0}
        if oem.name == "Manuf_02":
            oem.production = {('Manuf_01', 'groundBeef'): 53.0,
                              ('Manuf_02', 'marinatedBeef'): 3947.0}
        if oem.name == "Manuf_03":
            oem.production = {('Manuf_03', 'marinatedBeef'): 1137.0}



def print_result(agent_list):
    print("Flow:")
    total_flow_cost = 0
    for transportation in agent_list["Transportation"]:
        print("Number of changed flow", transportation.flow_change)
        print("Number of added flow", transportation.flow_added)
        for flow in transportation.flow.items():
            # print(flow)
            total_flow_cost += transportation.capability[(flow[0][0], flow[0][1])]["cost"] * flow[1]
        check_centralized_difference(transportation.flow)
    print("Total flow cost:", total_flow_cost)

    print("Production:")
    total_production_cost = 0
    for key in agent_list.keys():
        for ag in agent_list[key]:
            if "Production" in ag.capability.keys():
                if ag.production.__len__() != 0:
                    for pd in ag.production.items():
                        print(pd)
                        total_production_cost += ag.capability["Production"][pd[0][1]]["Cost"] * pd[1]
    print("Total production cost:", total_production_cost)


def get_agent(name, agent_list):
    for key in agent_list.keys():
        for ag in agent_list[key]:
            if ag.name == name:
                return ag

def plot_agent_attribute(agent_list):

    # nodes = [ag for key in ["Distributor", "OEM", "ManufacturingSupplier"] for ag in agent_list[key]]
    # x_axis = [ag.name for ag in nodes]
    # degree = [sum(ag.flow_indicator[key] for key in ag.flow_indicator.keys()) for ag in nodes]
    # plt.bar(x_axis, degree)
    # plt.show()

    node_name = ["T4:1", "T6:2", "T3:2", "T8:3", "O1:10"]
    ini_flow_cost = 59505.67835884318
    ini_production_cost = 165731.68999999994

    d_flow_cost = [x - ini_flow_cost for x in [58144.22292236816, 59480.19964217602, 57963.759227782386,
                                               59493.25851738464, 61738.98604390395]]
    c_flow_cost = [x - ini_flow_cost for x in [57762.96442379725, 59476.44150096135, 57964.059227782374,
                                               59461.96714122662, 61487.17301098378]]

    fig, ax = plt.subplots()
    ax.plot(node_name, d_flow_cost)
    ax.plot(node_name, c_flow_cost)
    ax.legend(['distributed_flow_cost', 'centralized_flow_cost'])
    # plt.plot(node_name, d_flow_cost, c_flow_cost)
    plt.xlabel("Lost agent: degree")
    plt.ylabel("Flow cost change")
    plt.show()
    d_production_cost = [x - ini_production_cost for x in [171771.58, 165931.58, 168026.58,
                                                           165881.58, 165529.78999999998]]
    c_production_cost = [x - ini_production_cost for x in [171621.24999999997, 165931.67999999996, 168026.67999999996,
                                                           165881.67999999996, 165135.38]]

    fig, ax = plt.subplots()
    ax.plot(node_name, d_production_cost)
    ax.plot(node_name, c_production_cost)
    ax.legend(['distributed_production_cost', 'centralized_production_cost'])
    # plt.plot(node_name, d_flow_cost, c_flow_cost)
    plt.xlabel("Lost agent: degree")
    plt.ylabel("Production cost change")
    plt.show()

    d_changed_flow = [0, 1, 1, 1, 6]
    c_changed_flow = [12, 3, 1, 3, 12]

    fig, ax = plt.subplots()
    ax.plot(node_name, d_changed_flow)
    ax.plot(node_name, c_changed_flow)
    ax.legend(['distributed_changed_flow', 'centralized_changed_flow'])
    # plt.plot(node_name, d_flow_cost, c_flow_cost)
    plt.xlabel("Lost agent: degree")
    plt.ylabel("Number of changed flow")
    plt.show()

    d_added_flow = [1, 1, 1, 2, 8]
    c_added_flow = [3, 1, 1, 3, 12]

    fig, ax = plt.subplots()
    ax.plot(node_name, d_added_flow)
    ax.plot(node_name, c_added_flow)
    ax.legend(['distributed_added_flow', 'centralized_added_flow'])
    # plt.plot(node_name, d_flow_cost, c_flow_cost)
    plt.xlabel("Lost agent: degree")
    plt.ylabel("Number of added flow")
    plt.show()

    d_communication = [6, 6, 6, 6, 46]
    c_communication = [57, 52, 51, 53, 63]

    fig, ax = plt.subplots()
    ax.plot(node_name, d_communication)
    ax.plot(node_name, c_communication)
    ax.legend(['distributed_communication', 'centralized_communication'])
    # plt.plot(node_name, d_flow_cost, c_flow_cost)
    plt.xlabel("Lost agent: degree")
    plt.ylabel("Number of communication")
    plt.show()




if __name__ == '__main__':
    # Initialize the agent network
    agent_list = network.initialize_agent_network(network)

    # check_centralized_difference()
    # TODO:Trigger the communication to solve problem
    # for customer in agent_list["Customer"]:
    #     communication(customer)

    # check_centralized_difference({})

    assign_initial_flow(agent_list)
    plot_agent_attribute(agent_list)

    # Disruption scenario
    disruption_adaptation(agent_list)

    # Print result
    print_result(agent_list)
