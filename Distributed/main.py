#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

import sys

sys.path.append("/agent")
sys.path.append("/initialization")
sys.path.append("/algorithms")
from initialization import network
from colorama import init
from termcolor import colored


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
            if ag.name == "Manuf_01":
            # if ag.name == "Part_04":
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
            if ag.name == "Retail_09":
                ag.demand['marinatedBeef'] = 300
                disrupted_node = ag
                ag.request('marinatedBeef', 300, ag.environment, lost_flow)

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
        tp.flow = {('Part_01', 'Manuf_01', 'package_0'): 2181.0,
                   ('Part_01', 'Manuf_02', 'package_0'): 53.0,
                   ('Manuf_01', 'Wholesale_02', 'groundBeef'): 1881.0,
                   ('Wholesale_01', 'Retail_01', 'groundBeef'): 247.0,
                   ('Wholesale_02', 'Retail_03', 'groundBeef'): 193.0,
                   ('Wholesale_02', 'Retail_05', 'groundBeef'): 1688.0,
                   ('Manuf_02', 'Wholesale_01', 'groundBeef'): 53.0,
                   ('Manuf_01', 'Wholesale_01', 'groundBeef'): 300.0,
                   ('Wholesale_01', 'Retail_02', 'groundBeef'): 106.0,
                   ('Part_08', 'Manuf_01', 'seasoning'): 2000.0,
                   ('Part_08', 'Manuf_03', 'seasoning'): 1137.0,
                   ('Part_06', 'Manuf_02', 'seasoning'): 2137.0,
                   ('Part_07', 'Manuf_01', 'seasoning'): 222.0,
                   ('Part_08', 'Manuf_02', 'seasoning'): 1863.0,
                   ('Part_06', 'Manuf_01', 'seasoning'): 1863.0,
                   ('Manuf_02', 'Wholesale_03', 'marinatedBeef'): 1447.0,
                   ('Manuf_01', 'Wholesale_03', 'marinatedBeef'): 904.0,
                   ('Wholesale_04', 'Retail_08', 'marinatedBeef'): 1855.0,
                   ('Manuf_03', 'Wholesale_04', 'marinatedBeef'): 1137.0,
                   ('Wholesale_03', 'Retail_04', 'marinatedBeef'): 289.0,
                   ('Manuf_02', 'Wholesale_04', 'marinatedBeef'): 2500.0,
                   ('Wholesale_04', 'Retail_07', 'marinatedBeef'): 2782.0,
                   ('Wholesale_03', 'Retail_06', 'marinatedBeef'): 2062.0,
                   ('Manuf_01', 'Wholesale_04', 'marinatedBeef'): 1000.0,
                   ('Part_05', 'Manuf_03', 'package_1'): 1137.0,
                   ('Part_05', 'Manuf_02', 'package_1'): 3947.0,
                   ('Part_05', 'Manuf_01', 'package_1'): 1904.0,
                   ('Part_02', 'Manuf_01', 'rawBeef'): 722.0,
                   ('Part_04', 'Manuf_02', 'rawBeef'): 4000.0,
                   ('Part_03', 'Manuf_01', 'rawBeef'): 3363.0,
                   ('Part_03', 'Manuf_03', 'rawBeef'): 1137.0}

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
            oem.production = {('Manuf_02', 'groundBeef'): 53.0,
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
            print(flow)
            total_flow_cost += transportation.capability[(flow[0][0], flow[0][1])]["cost"] * flow[1]
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




if __name__ == '__main__':
    # Initialize the agent network
    agent_list = network.initialize_agent_network(network)

    # check_centralized_difference()
    # TODO:Trigger the communication to solve problem
    # for customer in agent_list["Customer"]:
    #     communication(customer)

    assign_initial_flow(agent_list)

    # Disruption scenario
    disruption_adaptation(agent_list)

    # Print result
    print_result(agent_list)
