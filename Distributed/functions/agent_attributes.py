#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""
import matplotlib.pyplot as plt
from Distributed.initialization import network
import gurobipy as gp
from gurobipy import GRB

def calculate_attributes(agent_network, agent_name, initial_flows, initial_productions, contribution, l, n):
    ag = network.find_agent_by_name(agent_network, agent_name)
    in_degree, out_degree, com_degree = calculate_degrees(ag)
    capability_redundancy, capacity_proportion, capacity_utility = calculate_capability_capacity(ag)
    flow_contribution = calculate_flow_contributions(ag, initial_productions)
    # l, n = get_production_steps(agent_network, ag)

    attributes = attributes_summary(in_degree, out_degree, com_degree, capability_redundancy, capacity_proportion,
<<<<<<< Updated upstream
                                    capacity_utility, flow_contribution, l, n)
=======
                                    capacity_utility, flow_contribution, float(ag.depth), contribution, len(ag.state.production.keys()), l, n)
>>>>>>> Stashed changes
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
    capacity_utility = {}
    for product in agent.capability.knowledge["Production"]:
        try:
            capability_redundancy[product] = len(agent.environment.clustering_agent[product])
            total_cap = 0
            total_remain = 0
            for ag in agent.environment.clustering_agent[product]:
                total_cap += ag.capability.get_capacity()
                total_remain += ag.get_remaining_capacity()
            capacity_proportion[product] = agent.capability.get_capacity() / (agent.capability.get_capacity() + total_cap)
            try:
                capacity_utility[product] = agent.state.production[product] / total_remain
            except:
                capacity_utility[product] = 0
        except:
            capability_redundancy[product] = 0
            capacity_proportion[product] = 1
            capacity_utility[product] = 0
            # try:
            #     capacity_utility[product] = agent.state.production[product] / agent.get_remaining_capacity()
            # except:
            #     capacity_utility[product] = 0
    return capability_redundancy, capacity_proportion, capacity_utility

def calculate_flow_contributions(agent, initial_productions):
    product_set = set([p[1] for p in initial_productions.keys()])
    network_production = {key: 0 for key in product_set}
    for key in initial_productions.keys():
        network_production[key[1]] += initial_productions[key]

    agent_production = 0
    total_production = 0
    for prod in agent.state.production.keys():
        agent_production += agent.state.production[prod]
        total_production += network_production[prod]
        # flow_contribution[prod] = agent.state.production[prod]/network_production[prod]
    flow_contribution = agent_production/total_production
    return flow_contribution

def get_production_steps(agent_network, agent):
    production_hierarchy = {}
    production_steps = {}
    for product in set(agent_network.product_structure_2.index):
        try:
            production_hierarchy[product] = list(agent_network.product_structure_2.loc[product, "Needed"].values)
        except:
            production_hierarchy[product] = [agent_network.product_structure_2.loc[product, "Needed"]]
        production_steps[product] = set()

    # production_steps = {key: set() for key in set(agent_network.product_structure.index)}
    for key in production_steps:
        component = production_hierarchy[key].copy()
        while len(component) != 0:
            p = component.pop()
            production_steps[key].add(p)
            try:
                component += production_hierarchy[p]
            except: pass

    final_products = [p for p in production_hierarchy.keys() if "cockpit" in p]

    contributed_final_products, l = {}, {}
    needed_component, n = {}, {}
    for prod in agent.capability.knowledge["Production"]:
        try:
            needed_component[prod] = production_steps[prod]
        except:
            needed_component[prod] = set()
        contributed_final_products[prod] = set()
        for final_prod in final_products:
            if prod in production_steps[final_prod] or final_prod in agent.capability.knowledge["Production"]:
                contributed_final_products[prod].add(final_prod)
        l[prod] = len(needed_component[prod])
        n[prod] = len(contributed_final_products[prod])

    # max_steps = max(len(production_steps[final_prod]) for final_prod in contributed_final_products)
    # return max_steps
    return l, n

def calculate_impact(agent_network, agent_with_productions):

    product_set = set(agent_network.product_structure.index[i][0] for i in range(len(agent_network.product_structure.index)))
    production_hierarchy = {key: {} for key in product_set}
    production_steps = {key: {} for key in product_set}
    for prod_mat in agent_network.product_structure.index:
        production_hierarchy[prod_mat[0]][prod_mat[1]] = agent_network.product_structure.loc[prod_mat, "Amount"]

    # production_steps = {key: set() for key in set(agent_network.product_structure.index)}
    for key in production_steps:
        production_steps[key] = production_hierarchy[key]
        component = set(production_hierarchy[key].keys()).copy()
        while len(component) != 0:
            p = component.pop()
            if p in product_set:
                for m in production_hierarchy[p].keys():
                    try:
                        production_steps[key][m] += production_hierarchy[key][p] * production_hierarchy[p][m]
                    except:
                        production_steps[key][m] = production_hierarchy[key][p] * production_hierarchy[p][m]
            try:
                component += set(production_hierarchy[p].keys())
            except:
                pass
    K_f = {ag.name: set() for ag in agent_network.agent_list["Assembly"]}
    limit = {}
    agent_by_depth = {i: [] for i in range(4)}
    impact = {ag_name: 0 for ag_name in agent_with_productions}
    for ag in agent_network.agent_list["Assembly"]:
        if ag.name in agent_with_productions:
            agent_by_depth[0].append(ag)
            for prod in ag.state.production.keys():
                impact[ag.name] += ag.state.production[prod]
                K_f[ag.name].add(prod)
                limit[prod] = ag.state.production[prod]
    for ag in agent_network.agent_list["TierSupplier"]:
        if ag.depth == 1 and ag.name in agent_with_productions:
            agent_by_depth[1].append(ag)
        if ag.depth == 2 and ag.name in agent_with_productions:
            agent_by_depth[2].append(ag)
        if ag.depth == 3 and ag.name in agent_with_productions:
            agent_by_depth[3].append(ag)

    linked_assy = {ag.name: set() for ag in agent_network.agent_list["TierSupplier"] if ag.name in agent_with_productions}
    needed_materials = {k_f: {} for k_f in set(agent_network.product_structure.index) if "cockpit" in k_f}
    for ag in agent_by_depth[1]:
        for f in ag.state.outflow.items():
            for k in K_f[f[0][0]]:
                linked_assy[ag.name].add(k)

    for ag in agent_by_depth[2]:
        for f in ag.state.outflow.items():
            for s in linked_assy[f[0][0]]:
                linked_assy[ag.name].add(s)

    for ag in agent_by_depth[3]:
        for f in ag.state.outflow.items():
            for s in linked_assy[f[0][0]]:
                linked_assy[ag.name].add(s)

    contributed_types = {key: {} for key in linked_assy.keys()}
    for ag in contributed_types.keys():
        agt = network.find_agent_by_name(agent_network, ag)
        for kf in linked_assy[ag]:
            for prod in agt.state.production.keys():
                if prod in production_steps[kf].keys():
                    try:
                        contributed_types[ag][kf].add(prod)
                    except:
                        contributed_types[ag][kf] = set([prod])

    n = {key: 0 for key in linked_assy.keys()}
    for key in linked_assy.keys():
        n[key] = len(linked_assy[key])
    n["cockpit_assy_1"] = 1
    n["cockpit_assy_2"] = 2
    n["cockpit_assy_3"] = 3

    l = {key: 0 for key in linked_assy.keys()}
    for key in linked_assy.keys():
        agt = network.find_agent_by_name(agent_network, key)
        for p in agt.state.production.keys():
            if p in product_set:
                l[key] += len(list(production_steps[p].keys()))
    l["cockpit_assy_1"] = len(list(production_steps["cockpit_1"].keys()))
    l["cockpit_assy_2"] = len(set(list(production_steps["cockpit_2A"].keys())+list(production_steps["cockpit_2B"].keys())))
    l["cockpit_assy_3"] = len(set(list(production_steps["cockpit_3A"].keys())+list(production_steps["cockpit_3B"].keys())+list(production_steps["cockpit_3C"].keys())))

    res = {key: {kf: None for kf in contributed_types[key].keys()} for key in linked_assy.keys()}
    for ag in agent_network.agent_list["TierSupplier"]:
        if ag.name in agent_with_productions:
            model = gp.Model('contribution')
            model.Params.LogToConsole = 0
            contribution = contributed_types[ag.name]
            pairs = [(k, m) for k in contribution.keys() for m in contribution[k]]
            m_to_k = {m: set() for m in ag.state.production.keys()}
            for m in ag.state.production.keys():
                for kf in contribution.keys():
                    if m in contribution[kf]: m_to_k[m].add(kf)
            y = model.addVars(list(contribution.keys()), vtype=GRB.INTEGER, name="contri")

            obj = model.setObjective(gp.quicksum(y[k] for k in contribution.keys()), GRB.MAXIMIZE)

            pd_constrs = model.addConstrs((gp.quicksum(y[k] * production_steps[k][m] for k in m_to_k[m])
                                         <= ag.state.production[m] for m in ag.state.production.keys()), name="pd_limit")
            demand_constrs = model.addConstrs((y[k] <= limit[k] for k in contribution.keys()),
                                              name="demand_limit")

            model.optimize()
            xsol = model.getAttr('x', y)
            for k in contribution.keys():
                res[ag.name][k] = xsol[k]
    for ag_name in res.keys():
        for kf in res[ag_name].keys():
            impact[ag_name] += res[ag_name][kf]

    return impact, l, n

def attributes_summary(in_degree, out_degree, com_degree, capability_redundancy, capacity_proportion,
<<<<<<< Updated upstream
                                    capacity_utility, flow_contribution, l, n):
=======
                                    capacity_utility, flow_contribution, depth, contribution, variety, l, n):
>>>>>>> Stashed changes
    attributes = {
        'g_in': in_degree,
        'g_out': out_degree,
        'g_com': com_degree,
        'P': capability_redundancy,
        'U': capacity_proportion,
        'Q': capacity_utility,
        'F': flow_contribution,
        "depth": depth,
        'kf': contribution,
        'v': variety,
        'l': l,
        'n': n
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



