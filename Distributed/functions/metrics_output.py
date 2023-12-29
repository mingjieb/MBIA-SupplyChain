#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""
from Distributed.initialization import network
import json


def calculate_metrics(agent_network, initial_flows, initial_productions, run_time, initial_flow_cost, initial_production_cost):
    unmet_demand = get_unmet_demand(agent_network)
    flow_over_capacity_cost, production_over_capacity_cost = over_capacity_cost(agent_network)
    number_of_communications = agent_network.occurred_communication

    current_flows, current_productions = get_current_info(agent_network)

    changed_flows, added_edge, removed_edge = flow_difference(agent_network, initial_flows, current_flows)

    changed_productions, added_agent, removed_agent = production_difference(agent_network,
                                                                            initial_productions,
                                                                            current_productions)

    flow_cost_difference, production_cost_difference = get_cost_difference(agent_network, current_flows,
                                                                           current_productions, initial_flow_cost, initial_production_cost)

    result = result_summary(unmet_demand, flow_over_capacity_cost, production_over_capacity_cost,
                            changed_flows, added_edge, removed_edge, changed_productions, added_agent, removed_agent,
                            flow_cost_difference, production_cost_difference, number_of_communications, run_time)
    # return result
    return {"res": result, "flow": current_flows.copy(), "prod": current_productions.copy(), "changed_flow": changed_flows.copy(), "changed_production": changed_productions.copy()}

def reformat(file_name):
    with open(file_name) as f:
        data = json.load(f)
    input_plan = {}
    for ag in data.keys():
        input_plan[ag] = {}
        flows = {}
        for fl in data[ag]['flows']:
            flows[(fl['Source'], fl['Dest'], fl['Product'])] = fl["Value"]
        productions ={}
        for prod in data[ag]['prods']:
            productions[(prod['Agent'], prod['Product'])] = prod["Value"]
        input_plan[ag]["flow"] = flows.copy()
        input_plan[ag]["prod"] = productions.copy()
    return input_plan

def get_unmet_demand(agent_network):
    unmet_demand = 0
    for ag in agent_network.agent_list["Customer"]:
        for product in ag.demand.keys():
            received = 0
            for flow in ag.state.inflow.keys():
                if flow[1] == product:
                    received += ag.state.inflow[flow]
            unmet_demand += (ag.demand[product] - received)
    return unmet_demand


def over_capacity_cost(agent_network):
    flow_over_cap_cost = 0
    prod_over_cap_cost = 0
    overcapacity_multiplier = 2
    transportation = network.find_agent_by_name(agent_network, "Transportation")
    for flow in transportation.flow.keys():
        cap = transportation.capability.characteristics["Transportation"][(flow[0], flow[1])]["Capacity"]
        unit_over_cost = overcapacity_multiplier * \
                         transportation.capability.characteristics["Transportation"][(flow[0], flow[1])]["Cost"]
        amount = transportation.get_transportaion_amount(flow[0], flow[1])
        over_cap = max(0, amount - cap)
        flow_over_cap_cost += over_cap * unit_over_cost
        if over_cap > 0:
            print(flow)


    for ag in agent_network.agent_list["Assembly"] + agent_network.agent_list["TierSupplier"]:
        cap = ag.capability.get_capacity()
        unit_over_cost = overcapacity_multiplier * ag.capability.get_ave_cost()
        prod = 0
        for product in ag.state.production.keys():
            prod += ag.state.production[product]
        over_cap = max(0, prod - cap)
        prod_over_cap_cost += over_cap * unit_over_cost
        # if over_cap > 0:
        #     print(ag)

    return flow_over_cap_cost, prod_over_cap_cost


def get_current_info(agent_network):
    transportation = network.find_agent_by_name(agent_network, "Transportation")
    current_flows = transportation.flow
    current_productions = {}
    for ag_type in agent_network.agent_list.keys():
        for ag in agent_network.agent_list[ag_type]:
            for product in ag.state.production.keys():
                current_productions[(ag.name, product)] = ag.state.production[product]

    return current_flows, current_productions


def flow_difference(agent_network, initial_flows, current_flows):
    changed_flows = {}
    added_edge = {}
    removed_edge = {}

    initial = set(initial_flows.items())
    current = set(current_flows.items())
    lost_from_initial = initial - current
    new_in_current = current - initial

    initial_edge = set()
    for flow in initial_flows.keys():
        initial_edge.add((flow[0], flow[1]))

    current_edge = set()
    for flow in current_flows.keys():
        current_edge.add((flow[0], flow[1]))

    for new in new_in_current:
        if (new[0][0], new[0][1]) in initial_edge:
            if new[0] not in initial_flows.keys():
                changed_flows[new[0]] = new[1]
            elif abs(new[1] - initial_flows[new[0]]) > 0.1:
                changed_flows[new[0]] = new[1]
    added_edge = current_edge - initial_edge
    # for lost in lost_from_initial:
    #     if (lost[0][0], lost[0][1]) not in current_edge:
    #         removed_edge[lost[0]] = lost[1]
    removed_edge = initial_edge - current_edge
    return changed_flows, added_edge, removed_edge


def production_difference(agent_network, initial_productions, current_productions):
    changed_productions = {}
    added_agent = {}
    removed_agent = {}

    initial = set(initial_productions.items())
    current = set(current_productions.items())
    lost_from_initial = initial - current
    new_in_current = current - initial

    initial_agent = set()
    for pd in initial_productions.keys():
        initial_agent.add(pd[0])

    current_agent = set()
    for pd in current_productions.keys():
        current_agent.add(pd[0])

    for new in new_in_current:
        if new[0][0] in initial_agent:
            if new[0] not in initial_productions.keys():
                changed_productions[new[0]] = new[1]
            elif abs(new[1] - initial_productions[new[0]]) > 0.1:
                changed_productions[new[0]] = new[1]
            # added_agent[new[0]] = new[1]
        #     pass
        # else:
        #     changed_productions[new[0]] = new[1]

    # for lost in lost_from_initial:
    #     if lost[0][0] not in current_agent:
    #         removed_agent[lost[0]] = lost[1]
    added_agent = current_agent - initial_agent
    removed_agent = initial_agent - current_agent
    return changed_productions, added_agent, removed_agent

def calculate_cost(ag_network, flows, productions):
    flow_cost = 0
    production_cost = 0
    transportation = network.find_agent_by_name(ag_network, "Transportation")
    for flow in flows:
        cost = transportation.capability.characteristics["Transportation"][(flow[0], flow[1])]["Cost"]
        cap = transportation.capability.characteristics["Transportation"][(flow[0], flow[1])]["Capacity"]
        flow_cost += min(flows[flow], cap) * cost

    for prod in productions:
        ag = network.find_agent_by_name(ag_network, prod[0])
        cost = ag.capability.characteristics["Production"][prod[1]]["Cost"]
        cap = ag.capability.get_capacity()
        production_cost += min(productions[prod], cap) * cost

    flow_over_cap_cost, prod_over_cap_cost = over_capacity_cost(ag_network)
    flow_cost += flow_over_cap_cost
    production_cost += prod_over_cap_cost

    return flow_cost, production_cost

def get_cost_difference(agent_network, current_flows, current_productions, initial_flow_cost, initial_production_cost):

    current_flow_cost, current_production_cost = calculate_cost(agent_network, current_flows, current_productions)

    return current_flow_cost - initial_flow_cost, current_production_cost - initial_production_cost


def result_summary(unmet_demand, flow_over_capacity_cost, production_over_capacity_cost, changed_flows,
                   added_edge, removed_edge, changed_productions, added_agent, removed_agent, flow_cost_difference,
                   production_cost_difference, number_of_communications, run_time):
    result = {
        'delta_d': unmet_demand,
        'O_c_flow': flow_over_capacity_cost,
        'O_c_production': production_over_capacity_cost,
        'C_f': flow_cost_difference,
        'C_p': production_cost_difference,
        'N_f': len(changed_flows.keys()) + len(removed_edge),
        'N_p': len(changed_productions.keys()) + len(removed_agent),
        'H_f': len(added_edge),
        'H_p': len(added_agent),
        'M_e': number_of_communications,
        'T_e': run_time
    }
    return result
# def print_result(agent_list):
# print("Flow:")
# total_flow_cost = 0
# for transportation in agent_list["Transportation"]:
#     print("Number of changed flow", transportation.flow_change)
#     print("Number of added flow", transportation.flow_added)
#     for flow in transportation.flow.items():
#         # print(flow)
#         total_flow_cost += transportation.capability[(flow[0][0], flow[0][1])]["cost"] * flow[1]
#     check_centralized_difference(transportation.flow)
# print("Total flow cost:", total_flow_cost)
#
# print("Production:")
# total_production_cost = 0
# for key in agent_list.keys():
#     for ag in agent_list[key]:
#         if "Production" in ag.capability.keys():
#             if ag.production.__len__() != 0:
#                 for pd in ag.production.items():
#                     print(pd)
#                     total_production_cost += ag.capability["Production"][pd[0][1]]["Cost"] * pd[1]
# print("Total production cost:", total_production_cost)
