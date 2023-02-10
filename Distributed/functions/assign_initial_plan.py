#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

import json
from Distributed.initialization import network


def assign_initial_flow(ag_network, file_name):
    # hard code to assign the flow and production to agent
    with open(file_name) as f:
        data = json.load(f)

    flows = {}
    for fl in data['Flows']:
        flows[(fl['Source'], fl['Dest'], fl['Product'])] = fl["Value"]

    tp = network.find_agent_by_name(ag_network, "Transportation")
    tp.flow = flows.copy()

    for key in tp.flow.keys():
        start = network.find_agent_by_name(ag_network, key[0])
        end = network.find_agent_by_name(ag_network, key[1])
        start.state.update_flow("outflow", end.name, key[2], tp.flow[key])
        end.state.update_flow("inflow", start.name, key[2], tp.flow[key])
    #     start.flow_indicator[key[1]] = 1
    #     end.flow_indicator[key[0]] = 1

    productions ={}
    agent_with_productions = []
    for prod in data['Productions']:
        ag = network.find_agent_by_name(ag_network, prod['Agent'])
        ag.state.update_prod_inv("production", prod['Product'], prod["Value"])
        productions[(prod['Agent'], prod['Product'])] = prod["Value"]
        if ag.name not in agent_with_productions:
            agent_with_productions.append(ag.name)
            ag.used = True

    if 'OverProductions' in data.keys() or 'OverFlows' in data.keys():
        over_flows = {}
        for o_f in data["OverFlows"]:
            if o_f["Value"] > 1e-5:
                over_flows[(o_f['Source'], o_f['Dest'], o_f['Product'])] = o_f["Value"]
        tp.over_flow = over_flows.copy()

        for o_p in data['OverProductions']:
            if o_p["Value"] > 1e-5:
                ag = network.find_agent_by_name(ag_network, o_p['Agent'])
                ag.state.update_over_prod("production", o_p['Product'], o_p["Value"])


    return flows, productions, agent_with_productions

def re_initilize_network(ag_network, file_name):
    for ag_type in ag_network.agent_list.keys():
        for ag in ag_network.agent_list[ag_type]:
            ag.down = False
            ag.explore = False
            ag.used = False
            ag.state.clear_state()
            # ag.communication_manager.clear_message()
            if ag.name == "Transportation":
                ag.flow.clear()
                ag.over_flow.clear()
            if "Customer" not in ag.name:
                ag.demand.clear()
    ag_network.occurred_communication = 0
    initial_flows, initial_productions, agent_with_productions = assign_initial_flow(ag_network, file_name)

