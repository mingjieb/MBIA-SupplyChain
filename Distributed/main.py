#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

from functions.assign_initial_plan import assign_initial_flow, re_initilize_network
from functions.agent_attributes import calculate_attributes
from functions.disruption_response import disruption_adaptation
from functions.metrics_output import calculate_metrics, calculate_cost

from initialization import network
import time
import json
from colorama import init
from termcolor import colored
import matplotlib.pyplot as plt




if __name__ == '__main__':

    # Initialize the agent network and flows
    agent_network = network.initialize_agent_network(network)
    initial_file_name = 'initialization/InitialPlans.json'
    initial_flows, initial_productions, agent_with_productions = assign_initial_flow(agent_network, initial_file_name)
    initial_flow_cost, initial_production_cost = calculate_cost(agent_network, initial_flows, initial_productions)
    # ag_name = 'screen_sup_4'
    # disruption_adaptation(agent_network, ag_name)
    satisfied = 0
    unsatisfied = 0
    data_summary = {}
    for ag_name in agent_with_productions:
        # if ag_name == 'plastic_sup_1':
        #     print('debug')
        attributes = calculate_attributes(agent_network, ag_name, initial_flows, initial_productions)
        # Disruption scenario
        start_time = time.time()
        found_solution = disruption_adaptation(agent_network, ag_name)
        end_time = time.time()
        run_time = end_time-start_time
        results = calculate_metrics(ag_name, agent_network, initial_flows, initial_productions,
                                    run_time, initial_flow_cost, initial_production_cost)
        if found_solution:
            print("Satisfied solution is found when losing", ag_name)
            satisfied += 1
        else:
            print("Unsatisfied solution is found when losing", ag_name)
            unsatisfied += 1
        data_summary[ag_name] = {"attributes": attributes, "results": results}
        re_initilize_network(agent_network, initial_file_name)

    with open('results/Distributed_results.json', 'w', encoding='utf-8') as f:
        json.dump(data_summary, f, ensure_ascii=False, indent=4)

    # read
    print("Total:", len(agent_with_productions))
    print("Success:", satisfied)
    print("Failure:", unsatisfied)

    centralized_data = {}
    centralized_communication = {}
    agent_amount = sum(len(agent_network.agent_list[key]) for key in agent_network.agent_list.keys())
    for case_name in agent_with_productions:
        re_initilize_network(agent_network, '../CentralizedResults/%s.json' % case_name)
        results = calculate_metrics(ag_name, agent_network, initial_flows, initial_productions,
                                    0, initial_flow_cost, initial_production_cost)
        centralized_data[case_name] = {"results": results}
        centralized_communication[case_name] = agent_amount + results['N_p'] + results['H_p']

    with open("../CentralizedResults/communication.json", 'w', encoding='utf-8') as f:
        json.dump(centralized_communication, f, ensure_ascii=False, indent=4)

    with open('../CentralizedResults/Centralized_results.json', 'w', encoding='utf-8') as f:
        json.dump(centralized_data, f, ensure_ascii=False, indent=4)