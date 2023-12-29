#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

from functions.assign_initial_plan import assign_initial_flow, re_initilize_network
from functions.agent_attributes import calculate_attributes, calculate_impact
from functions.disruption_response import lead_time_disruption
from functions.metrics_output import calculate_metrics, calculate_cost, reformat

from initialization import network
from functions.simulation import simulate_flows, simulate_arrival
import time
import json
import datetime

if __name__ == '__main__':

    # Initialize the agent network and flows
    agent_network = network.initialize_agent_network(network)
    agent_network.occurred_communication = 0
<<<<<<< Updated upstream
    initial_file_name = 'initialization/InitialPlans.json'
=======

    # initial_flows, initial_productions, agent_with_productions = assign_initial_flow(agent_network, '../CentralizedResults/initial.json')
    # initial_flow_cost, initial_production_cost = calculate_cost(agent_network, initial_flows, initial_productions)
    # re_initilize_network(agent_network, '../CentralizedResults/button_sup_4.json')
    # results = calculate_metrics(agent_network, initial_flows, initial_productions,
    #                             0, initial_flow_cost, initial_production_cost)


    # info = pd.read_excel('initialization/Conference Case - New_juanest.xlsx', sheet_name=None)
    # prod = info["Productions"].set_index(['Prod_v', 'Prod_k'])
    # tranp = info["Flows"].set_index(['Flows_i', 'Flows_j', 'Flows_k'])
    # new_initial = {'Productions': [], 'Flows': []}
    # for p in prod.index:
    #     new_initial['Productions'].append({'Agent': p[0], "Product": p[1], "Value": float(prod.loc[p, "Prod_val"]), "Time": float(prod.loc[p, "Prod_time"])})
    # for t in tranp.index:
    #     new_initial['Flows'].append({'Source': t[0], "Dest": t[1], "Product": t[2], "Value": float(tranp.loc[t, "Flows_val"]), "Time": float(tranp.loc[t, "Flows_time"])})
    #
    # with open("initialization/new_initial.json", 'w', encoding='utf-8') as f:
    #     json.dump(new_initial, f, ensure_ascii=False, indent=4)

    # initial_file_name = 'initialization/InitialPlansRAL.json'
    initial_file_name = 'initialization/InitialPlans-New.json'
    # initial_file_name = 'initialization/new_initial.json'
>>>>>>> Stashed changes
    initial_flows, initial_productions, agent_with_productions = assign_initial_flow(agent_network, initial_file_name)
    initial_flow_cost, initial_production_cost = calculate_cost(agent_network, initial_flows, initial_productions)
    production_impact, l, n = calculate_impact(agent_network, agent_with_productions)
    # lead time disruption
    # for ag_name in agent_with_productions:
    #     # if ag_name == 'cluster_sup_3':
    #
    #     if "assy" not in ag_name and "HVAC_sup_2" not in ag_name:
    #         try:
    #             found_solution = lead_time_disruption(agent_network, ag_name)
    #             results = calculate_metrics(agent_network, initial_flows, initial_productions,
    #                                         0, initial_flow_cost, initial_production_cost)
    #             print("SOLUTION FOUNDED FOR DISRUPTION OF ", ag_name)
    #         except:
    #             print("NO SOLUTION FOUNDED FOR DISRUPTION OF ", ag_name)
    # filename = 'results/nominal_plan.json'
    # input_plan = reformat(filename)
    # TEMP = simulate_arrival(agent_network, "wiring_sup_3", input_plan["bezel_sup_5"], 1, 1.5)
    #
    # disruption = [round(1.2 + 0.2 * i, 2) for i in range(5)]
    # for d in disruption:
    #     filename = 'results/new/neutral_plan' + str(d) + '.json'
    #     input_plan = reformat(filename)
    #     customer_lateness = {}
    #     for ag in input_plan.keys():
    #         customer_lateness[ag] = simulate_arrival(agent_network, ag, input_plan[ag], 300, d)
    #         print("Finish neutral simulation for ", ag)
    #     res_name = 'results/new/result/neutral_result' + str(d) + '.json'
    #     with open(res_name, 'w', encoding='utf-8') as f:
    #         json.dump(customer_lateness, f, ensure_ascii=False, indent=4)
    #     print("Finish ALL neutral simulation ", d)
    #
    #     filename = 'results/new/averse_plan' + str(d) + '.json'
    #     input_plan = reformat(filename)
    #     customer_lateness = {}
    #     for ag in input_plan.keys():
    #         customer_lateness[ag] = simulate_arrival(agent_network, ag, input_plan[ag], 300, d)
    #         print("Finish averse simulation for ", ag)
    #     res_name = 'results/new/result/averse_result' + str(d) + '.json'
    #     with open(res_name, 'w', encoding='utf-8') as f:
    #         json.dump(customer_lateness, f, ensure_ascii=False, indent=4)
    #
    #     print("Finish ALL averse simulation ", d)
    #
    #     filename = 'results/new/nominal_plan.json'
    #     input_plan = reformat(filename)
    #     customer_lateness = {}
    #     for ag in input_plan.keys():
    #         customer_lateness[ag] = simulate_arrival(agent_network, ag, input_plan[ag], 300, d)
    #         print("Finish nominal simulation for ", ag)
    #     res_name = 'results/new/result/nominal_result' + str(d) + '.json'
    #     with open(res_name, 'w', encoding='utf-8') as f:
    #         json.dump(customer_lateness, f, ensure_ascii=False, indent=4)
    #
    #     print("Finish ALL nominal simulation ", d)
    #
    # for risk in ["TrueTrueTrue", "TrueTrueFalse", "TrueFalseTrue", "TrueFalseFalse",
    #              "FalseTrueTrue", "FalseTrueFalse", "FalseFalseTrue", "FalseFalseFalse"]:
    # for risk in ["TrueFalseTrue"]:
    #     filename = 'results/new/' + risk + '.json'
    #     input_plan = reformat(filename)
    #     customer_lateness = {}
    #     for ag in input_plan.keys():
    #         customer_lateness[ag] = simulate_arrival(agent_network, ag, input_plan[ag], 300, 1.6)
    #         print("Finish risk simulation for ", risk)
    #     res_name = 'results/new/result/' + risk + 'result.json'
    #     with open(res_name, 'w', encoding='utf-8') as f:
    #         json.dump(customer_lateness, f, ensure_ascii=False, indent=4)

    # filename = 'results/new/nominal_plan.json'
    # input_plan = reformat(filename)
    # customer_lateness = {}
    # for ag in input_plan.keys():
    #     customer_lateness[ag] = simulate_arrival(agent_network, ag, input_plan[ag], 300, 1)
    # res_name = 'results/new/result/initial_plan_result.json'
    # with open(res_name, 'w', encoding='utf-8') as f:
    #     json.dump(customer_lateness, f, ensure_ascii=False, indent=4)
    #
    # print("Finish ALL nominal simulation")


    satisfied = 0
    unsatisfied = 0
    data_summary = {}
<<<<<<< Updated upstream
    for ag_name in agent_with_productions:
        # # Used for debug
        # if ag_name == 'plastic_sup_4':
        #     print('debug')
        attributes = calculate_attributes(agent_network, ag_name, initial_flows, initial_productions)
        # Disruption scenario
        start_time = time.time()
        found_solution = disruption_adaptation(agent_network, ag_name)
        end_time = time.time()
=======
    customer_lateness = {}
    json_data = {}
>>>>>>> Stashed changes

    risk_combination = [{"cockpit_assy_1": True, "cockpit_assy_2": True, "cockpit_assy_3": True},
                        {"cockpit_assy_1": True, "cockpit_assy_2": True, "cockpit_assy_3": False},
                        {"cockpit_assy_1": True, "cockpit_assy_2": False, "cockpit_assy_3": True},
                        {"cockpit_assy_1": True, "cockpit_assy_2": False, "cockpit_assy_3": False},
                        {"cockpit_assy_1": False, "cockpit_assy_2": True, "cockpit_assy_3": True},
                        {"cockpit_assy_1": False, "cockpit_assy_2": True, "cockpit_assy_3": False},
                        {"cockpit_assy_1": False, "cockpit_assy_2": False, "cockpit_assy_3": True},
                        {"cockpit_assy_1": False, "cockpit_assy_2": False, "cockpit_assy_3": False}]
    # for sce in risk_combination:
    # for d in disruption:
    for sce in [risk_combination[0]]:
        for ag_name in agent_with_productions:
            # Update the network back to initial plan
            re_initilize_network(agent_network, initial_file_name)
            if "assy" not in ag_name and ag_name in ["cluster_sup_3"]:
            # # Used for debug
            # if ag_name == 'HVAC_sup_2':
            #     print('debug')
            #     for ag in agent_network.agent_list["TierSupplier"]:
            #         if ag.name == "controlunit_sup_2":
            #             print(ag.used)
                attributes = calculate_attributes(agent_network, ag_name, initial_flows, initial_productions, production_impact[ag_name], l[ag_name], n[ag_name])
                # Disruption scenario
                start_time = time.time()
                # found_solution = disruption_adaptation(agent_network, ag_name)
                # if ag_name == "HVAC_sup_2":
                #     print("debug")
                disrupted_node = agent_network.find_agent_by_name(agent_network, ag_name)
                temp_leadtime = {product: disrupted_node.capability.characteristics["Production"][product]["LeadTime"] for product in disrupted_node.capability.characteristics["Production"].keys()}
                for key in sce.keys():
                    downstream_agent = agent_network.find_agent_by_name(agent_network, key)
                    downstream_agent.risk_averse = sce[key]

                increase = 1.6
                found_solution = lead_time_disruption(agent_network, ag_name, increase)
                end_time = time.time()
                run_time = end_time - start_time
                results = calculate_metrics(agent_network, initial_flows, initial_productions,
                                            run_time, initial_flow_cost, initial_production_cost)
                if found_solution:
                    print("Satisfied solution is found when losing", ag_name)
                    satisfied += 1
                    data_summary[ag_name] = results.copy()
                    json_data[ag_name] = {"flows": {}, "prods": {}, "res": data_summary[ag_name]["res"]}

                    customer_lateness[ag_name] = simulate_arrival(agent_network, ag_name, data_summary[ag_name], 1, increase)
                    # disrupted_node = agent_network.find_agent_by_name(agent_network, ag_name)
                    # for product in disrupted_node.capability.characteristics["Production"].keys():
                    #     disrupted_node.capability.characteristics["Production"][product]["LeadTime"] /= 1.5
                    #     disrupted_node.capability.characteristics["Production"][product]["LeadTime"].astype(int)
                else:
                    print("Unsatisfied solution is found when losing", ag_name)
                    unsatisfied += 1
                    last_file = 'results/neutral_plan' + str(round(increase-0.1, 2)) + '.json'
                    with open(last_file) as f:
                        last_plan = json.load(f)
                    json_data[ag_name] = last_plan[ag_name]

                # change the lead time back
                for product in disrupted_node.capability.characteristics["Production"].keys():
                    disrupted_node.capability.characteristics["Production"][product]["LeadTime"] = temp_leadtime[product]
                # data_summary[ag_name] = {"attributes": attributes, "results": results}

        for ag in json_data.keys():
            json_data[ag]["flows"] = []
            json_data[ag]["prods"] = []
            for f in data_summary[ag]["flow"].keys():
                json_data[ag]["flows"].append({"Source": f[0], "Dest": f[1], "Product": f[2], "Value": data_summary[ag]["flow"][f]})
            for p in data_summary[ag]["prod"].keys():
                json_data[ag]["prods"].append(
                    {"Agent": p[0], "Product": p[1], "Value": data_summary[ag]["prod"][p]})
        # result_name = 'results/new/nominal_plan.json'
        # result_name = 'results/new/averse_plan' + str(increase) + '.json'
        risk = ''
        for v in sce.values():
            risk += str(v)
        result_name = 'results/update/' + risk + '.json'
        with open(result_name, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        # Update the network back to initial plan
        re_initilize_network(agent_network, initial_file_name)




    # with open('results/Distributed_results.json', 'w', encoding='utf-8') as f:
    #     json.dump(data_summary, f, ensure_ascii=False, indent=4)

    print("Total:", len(agent_with_productions))
    print("Demand satisfied:", satisfied)
    print("Demand unsatisfied:", unsatisfied)

    # Read centralized results and re-write them to a single file
    centralized_data = {}
    centralized_communication = {}
    agent_amount = sum(len(agent_network.agent_list[key]) for key in agent_network.agent_list.keys())
    for case_name in agent_with_productions:
        re_initilize_network(agent_network, '../CentralizedResults/%s.json' % case_name)
        results = calculate_metrics(agent_network, initial_flows, initial_productions,
                                    0, initial_flow_cost, initial_production_cost)
        centralized_data[case_name] = {"results": results}
        centralized_communication[case_name] = agent_amount*2 + results['N_p'] + results['H_p']

    with open("../CentralizedResults/communication.json", 'w', encoding='utf-8') as f:
        json.dump(centralized_communication, f, ensure_ascii=False, indent=4)

    with open('../CentralizedResults/Centralized_results.json', 'w', encoding='utf-8') as f:
        json.dump(centralized_data, f, ensure_ascii=False, indent=4)