#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

from Distributed.initialization import network
from termcolor import colored


def disruption_adaptation(agent_network, disrupted_agent):
    find_solution = True
    # identify disruption
    disrupted_node = network.find_agent_by_name(agent_network, disrupted_agent)
    disrupted_node.down = True
    lost_production = [disrupted_node.state.production.copy()]
    lost_flow = []
    transportation = network.find_agent_by_name(agent_network, "Transportation")
    for item in transportation.flow.items():
        if disrupted_node.name in item[0]:
            lost_flow.append(item)

    # clear the production and flows of the disrupted agent
    disrupted_node.state.clear_state()

    # update the production and flows of the upstream and downstream agents
    related_agent = []
    propagation_agent = set()
    for f in lost_flow:  # f = ((source, destination, product), amount)
        transportation.flow.pop(f[0])
        if disrupted_node.name == f[0][1]:  # inflow to lost agent
            up_agent = network.find_agent_by_name(agent_network, f[0][0])
            if up_agent.name not in related_agent: related_agent.append(up_agent.name)
            up_agent.state.update_prod_inv("production", f[0][2], -f[1])
            up_agent.state.outflow.pop((f[0][1], f[0][2]))
            if len(up_agent.state.inflow.keys()) != 0:
                propagation_agent.add(up_agent)

        if disrupted_node.name == f[0][0]:  # outflow from lost agent
            down_agent = network.find_agent_by_name(agent_network, f[0][1])
            down_agent.state.inflow.pop((f[0][0], f[0][2]))
            if down_agent.name not in related_agent: related_agent.append(down_agent.name)

    for ag in propagation_agent:
        ag.cancel_upstream_production(agent_network)

    # print the disruption
    print(colored("Disrupted agent:", 'magenta'), disrupted_node.name)
    # print(colored("Lost production:", 'magenta'))
    # for p in lost_production:
    #     print(p)
    # print(colored("Lost flow:", 'magenta'))
    # for f in lost_flow:
    #     print(f)

    # identify demand agents
    demand_agents = disrupted_node.find_demand_agents(agent_network, lost_production, lost_flow)
    agent_network.occurred_communication = len(demand_agents) + len(related_agent)

    # generate new flows by agent communication
    final_new_flows = {}
    final_new_productions = {}
    while len(demand_agents) != 0:
        new_production, new_flows, find_solution = supplier_reselection(agent_network, demand_agents, transportation,
                                                                        find_solution)
        final_new_flows.update(new_flows)
        final_new_productions.update(new_production)
        # propagate communication if needed
        for sup_name in new_production:
            ag_sup = network.find_agent_by_name(agent_network, sup_name)
            # Here we assume no inventory, so each supplier agent will require materials if they need
            if ag_sup.capability.does_need_materials():
                ag_sup.demand = ag_sup.find_needed_materials(new_production[sup_name])
                demand_agents.append(ag_sup)

    check_unbalanced_agent(agent_network)
    # print(final_new_flows)
    # print(final_new_productions)
    return find_solution


def supplier_reselection(agent_network, demand_agents, transportation, find_solution):
    new_flows = {}
    new_productions = {}
    while len(demand_agents) != 0:
        total_supplier_agents = {}
        # all the demand_agents send request
        for ag_dm in demand_agents:
            supplier_agents = ag_dm.exploration(agent_network)
            total_supplier_agents[ag_dm.name] = supplier_agents
            ag_dm.send_request(supplier_agents)
            agent_network.occurred_communication += len(ag_dm.communication_manager.delivered_request.keys())

        # all the supplier_agents determine response
        supplier_agents_considered = []  # used for avoiding same supplier agents make decisions more than 1 time
        for ag_dm in demand_agents:
            for product in total_supplier_agents[ag_dm.name].keys():
                for ag_sup in total_supplier_agents[ag_dm.name][product]:
                    if ag_sup.name not in supplier_agents_considered:
                        try:
                            response_decision = ag_sup.response_optimizer(transportation)
                        except:
                            print(ag_sup.name, "cannot find response to", ag_dm.name)
                            find_solution = False
                        ag_sup.send_response(response_decision)
                        supplier_agents_considered.append(ag_sup.name)
                        agent_network.occurred_communication += len(
                            ag_sup.communication_manager.delivered_response.keys())

        # all the demand_agents select the suppliers
        for ag_dm in demand_agents:
            try:
                ag_dm_decision, ag_dm_flows = ag_dm.supplier_selector()
            except:
                print(ag_dm.name, "cannot find enough suppliers")
                find_solution = False
            new_flows.update(ag_dm_flows)
            agent_network.occurred_communication += len(ag_dm_decision.keys())
            for ag_sup in ag_dm_decision.keys():
                ag = network.find_agent_by_name(agent_network, ag_sup)
                for product in ag_dm_decision[ag_sup].keys():
                    ag.state.update_prod_inv("production", product, ag_dm_decision[ag_sup][product])
                try:
                    for product in ag_dm_decision[ag_sup].keys():
                        try:
                            new_productions[ag_sup][product] += ag_dm_decision[ag_sup][product]
                        except:
                            new_productions[ag_sup].update({product: ag_dm_decision[ag_sup][product]})
                except:
                    new_productions[ag_sup] = ag_dm_decision[ag_sup]
            for flow in ag_dm_flows.keys():
                transportation.update_flow(flow, ag_dm_flows[flow])
                source_ag = network.find_agent_by_name(agent_network, flow[0])
                dest_ag = network.find_agent_by_name(agent_network, flow[1])
                source_ag.state.update_flow("outflow", flow[1], flow[2], new_flows[flow])
                dest_ag.state.update_flow("inflow", flow[0], flow[2], new_flows[flow])
                # source_ag.communication_manager.clear_message()
                # dest_ag.communication_manager.clear_message()
            ag_dm.communication_manager.clear_message()
            for prod in total_supplier_agents[ag_dm.name]:
                for ag in total_supplier_agents[ag_dm.name][prod]:
                    ag.communication_manager.clear_message()
        # demand_agents = [ag_dm for ag_dm in demand_agents if not ag_dm.check_demand(ag_dm_flows)]

        for ag_dm in demand_agents[:]:
            if ag_dm.check_demand(new_flows):
                demand_agents.remove(ag_dm)
            elif not ag_dm.check_possible_iteration(agent_network):
                demand_agents.remove(ag_dm)
                print(ag_dm.name, "cannot get", ag_dm.demand)
                find_solution = False
                # ag_dm.notify_failure()

    # update agent state based on decisions
    # for ag_name in new_productions.keys():
    #     ag = network.find_agent_by_name(agent_network, ag_name)
    #     for product in new_productions[ag_name].keys():
    #         ag.state.update_prod_inv("production", product, new_productions[ag_name][product])
    # for flow in new_flows.keys():
    #     try:
    #         transportation.flow[flow] += new_flows[flow]
    #     except:
    #         transportation.flow[flow] = new_flows[flow]
    #     source_ag = network.find_agent_by_name(agent_network, flow[0])
    #     dest_ag = network.find_agent_by_name(agent_network, flow[1])
    #     source_ag.state.update_flow("outflow", flow[1], flow[2], new_flows[flow])
    #     dest_ag.state.update_flow("inflow", flow[0], flow[2], new_flows[flow])
    #     source_ag.communication_manager.clear_message()
    #     dest_ag.communication_manager.clear_message()

    return new_productions, new_flows, find_solution


def check_unbalanced_agent(agent_network):
    unmet_agent = []
    # over_input_agent = []
    for ag in agent_network.agent_list["Assembly"] + agent_network.agent_list["TierSupplier"]:
        if len(ag.demand.keys()) != 0:
            unmet_agent.append(ag)
        # flag = 0
        # for product in ag.capability.characteristics["Production"].keys():
        #     if len(ag.capability.characteristics["Production"][product]["Material"].keys()) != 0:
        #         flag = 1
        # if flag == 1: over_input_agent.append(ag)
    transportation = network.find_agent_by_name(agent_network, "Transportation")
    for ag in unmet_agent:
        ag.cancel_downstream_production(agent_network)
        # reduced_production, reduced_outflow = ag.cancel_downstream_production()
        # for prod in reduced_production:
        #     ag.state.update_prod_inv("production", prod, -reduced_production[prod])
        # for flow in reduced_outflow.keys():
        #     ag.state.update_flow("outflow", flow[0], flow[1], -reduced_outflow[flow])
        #     downstream_agent = network.find_agent_by_name(agent_network, flow[0])
        #     downstream_agent.state.update_flow("inflow", ag.name, flow[1], -reduced_outflow[flow])
        #     transportation.update_flow((ag.name, flow[0], flow[1]), -reduced_outflow[flow])
        #     agent_network.occurred_communication += 1
        #     if "Customer" not in downstream_agent.name:
        #         downstream_agent.demand[flow[1]] = reduced_outflow[flow]
        #         downstream_agent.cancel_downstream_production()
        ag.cancel_upstream_production(agent_network)
        # print("debugging")
    # for ag in over_input_agent:
    #     ag.cancel_upstream_production()
