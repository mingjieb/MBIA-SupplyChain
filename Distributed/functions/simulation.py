#!/usr/bin/python3

import numpy as np
import pandas as pd
import json
from scipy.stats import truncnorm




def simulate_arrival(agent_network, ag_name, res, sample_num, disruption):
    customer_lateness = []
    for i in range(sample_num):
        arrival_times = simulate_flows(agent_network, ag_name, res, disruption)
        # customer_lateness.append({"Scenario_id": i, "Result": []})
        customer_lateness.append([])
        for idx in arrival_times.index:
            if int(arrival_times.at[idx, "lateness"]) > 0:
                late = {"Agent": arrival_times.at[idx, "j"],
                        "Product" : arrival_times.at[idx, "k"],
                        "Lateness": int(arrival_times.at[idx, "lateness"]),
                        "From": arrival_times.at[idx, "i"],
                        "Prod_amount": arrival_times.at[idx, "flow"]}
                customer_lateness[i].append(late)

    return customer_lateness


def simulate_flows(agent_network, ag_name, res, disruption):
    with open("initialization/InitialPlans-New.json") as f:
        initial_plan = json.load(f)
    SC = pd.read_excel('initialization/TASE_Setup.xlsx', sheet_name='Link')[['Source', 'Destination']]
    V = list(set(list(SC.Source.unique()) + list(SC.Destination.unique())))
    V_type = TASE_adapt(SC, V)
    conversion = pd.read_excel('initialization/TASE_Setup.xlsx', sheet_name='ProductStructure', index_col=[1, 0])
    conversion = conversion.reset_index()
    conversion = conversion.to_dict()
    prod_conv = pd.DataFrame(conversion)

    flows = res["flow"].copy()
    prods = res["prod"].copy()
    # Out of sample testing
    active_flows = {}
    for key, val in flows.items():
        if val > 0:
            if key not in list(active_flows.keys()):
                active_flows[key] = {}
            active_flows[key]['flow'] = val
            ag = agent_network.find_agent_by_name(agent_network, key[0])

            # sample lead time
            mean_value = ag.capability.characteristics["Production"][key[2]]["LeadTime"]
            std_value = ag.capability.characteristics["Production"][key[2]]["Sigma"]
            if ag.name == ag_name:
                active_flows[key]['lead_time'] = truncated_normal_distribution(mean_value*disruption, std_value, 1)
            else:
                active_flows[key]['lead_time'] = truncated_normal_distribution(mean_value, std_value, 1)

    active_flows = pd.DataFrame(active_flows).T.reset_index()
    active_flows.columns = ['i', 'j', 'k', 'flow', 'lead_time']
    in_flows = {}
    out_flows = {}
    # simulating flows
    for i in range(len(active_flows)):
        origin = active_flows.iloc[i]['i']
        dest = active_flows.iloc[i]['j']
        prod = active_flows.iloc[i]['k']
        flow = active_flows.iloc[i]['flow']
        l_time = active_flows.iloc[i]['lead_time']

        # Setting up in flow dictionary

        if dest not in list(in_flows.keys()):
            in_flows[dest] = {}
        if origin not in list(in_flows[dest].keys()):
            in_flows[dest][origin] = {}
        in_flows[dest][origin][prod] = {}
        in_flows[dest][origin][prod]['flow'] = flow
        in_flows[dest][origin][prod]['lead_time'] = l_time

        # Setting up out flow dictionary
        if origin not in list(out_flows.keys()):
            out_flows[origin] = {}
        if dest not in list(out_flows[origin].keys()):
            out_flows[origin][dest] = {}
        out_flows[origin][dest][prod] = {}
        out_flows[origin][dest][prod]['flow'] = flow
        out_flows[origin][dest][prod]['lead_time'] = l_time

        # print('Moving ',flow,' of ',prod,' from: ',origin,' to ',dest, ' with lead time of ',time)
    tier_members = {}
    tiers = ['Part', 0, 1, 2, 'Retail']
    for tier in tiers:
        tier_members[tier] = []
    for v, type in V_type.items():
        tier_members[type].append(v)
    o = {}
    a = {}
    for j, items in in_flows.items():
        for i, info in items.items():
            for k, data in info.items():
                # if (j,k) not in list(time_computation.keys()):
                #        time_computation[(j,k)]  = {}
                a[(i, j, k)] = data['lead_time']

    # Setting incumbent solution
    active_prods = {}
    for i, k in prods.items():
        try:
            active_prods[i[0]].append(i[1])
        except:
            active_prods[i[0]] = [i[1]]

    for v in V:
        if v not in active_prods.keys():
            active_prods[v] = []

    for part in tier_members['Part']:
        try:
            ks = active_prods[part]
            for k in ks:
                o[(part, k)] = 0
        except: pass

    planned_o = {}
    for productions in initial_plan["Productions"]:
        planned_o[productions["Agent"], productions["Product"]] = productions["Prod_time"]


    deadline = {}
    sequence = [0, 1, 2, 'Retail']  # We just need to consider those that take flow
    transformers = [0, 1, 2]  # Considering those vertices that transform
    active_vertices = in_flows.keys()
    for tier in sequence:
        if tier in transformers:
            for j in tier_members[tier]:
                if j in active_vertices:
                    for i, info in in_flows[j].items():
                        for k, data in info.items():
                            # if (j,k) not in list(time_computation.keys()):
                            #        time_computation[(j,k)]  = {}
                            # if i == "button_sup_5":
                            #     print("d")
                            # a[(i, j, k)] = np.ceil(data['lead_time']) + np.ceil(o[(i, k)])
                            a[(i, j, k)] = np.round(data['lead_time'], 0) + np.round(o[(i, k)], 0)
                    for k in active_prods[j]:
                        # print('---------')
                        # print(j,k)
                        # print('---------')
                        subproduct_flow_time = []
                        subproduct_flow_id = []
                        subproduct_received = []
                        sub_prods = prod_conv[prod_conv['Product'] == k]['Needed'].values
                        # print(k,sub_prods)
                        for i, info in in_flows[j].items():
                            for prod, data in info.items():
                                if prod in sub_prods:
                                    subproduct_flow_time.append(a[(i, j, prod)])
                                    subproduct_flow_id.append((i, j, prod))
                                    subproduct_received.append(prod)
                                    try:
                                        deadline[(i, j, prod)] = planned_o[j, k]
                                    except:
                                        temp_agent = agent_network.find_agent_by_name(agent_network, j)
                                        deadline[(i, j, prod)] = temp_agent.capability.characteristics["Production"][k]["NominalTime"]
                                    # print(i,j,prod)

                        if set(sub_prods).issubset(subproduct_received) == True:
                            # print(j,k,subproduct_flow_time,subproduct_flow_id)
                            try:
                                temp = max(max(subproduct_flow_time), planned_o[j, k])
                            except:
                                temp = max(subproduct_flow_time)
                            # max_id = np.argmax(subproduct_flow_time)
                            # print(temp,subproduct_flow_id[max_id])
                            o[(j, k)] = temp
        else:
            for j in tier_members[tier]:
                if j in active_vertices:
                    # print('========')
                    # print(j)
                    # print(in_flows[j])
                    # print('========')
                    for i, info in in_flows[j].items():
                        for k, data in info.items():
                            # if (j,k) not in list(time_computation.keys()):
                            #        time_computation[(j,k)]  = {}
                            # a[(i, j, k)] = np.ceil(data['lead_time']) + np.ceil(o[(i, k)])
                            a[(i, j, k)] = np.round(data['lead_time'], 0) + np.round(o[(i, k)], 0)
                            # print(i,j,k,a[i,j,k])
                    for k in active_prods[j]:
                        # print(j,k)
                        product_flow_time = []
                        product_flow_id = []
                        product_received = []
                        for i, info in in_flows[j].items():
                            for prod, data in info.items():
                                if prod == k:
                                    product_flow_time.append(a[(i, j, prod)])
                                    product_flow_id.append((i, j, prod))
                                    product_received.append(prod)
                                    # print(i,j,prod)
                        # print(product_flow_id)
                        if len(product_flow_time) > 0:
                            for prod, data in info.items():
                                try:
                                    temp = max(max(subproduct_flow_time), planned_o[j, k])
                                except:
                                    temp = max(subproduct_flow_time)
                                # max_id = np.argmax(product_flow_time)
                                # print(temp,subproduct_flow_id[max_id])
                                # print('o',j,prod,'agregado!')
                                o[(j, k)] = temp
        arrival_times = pd.DataFrame({'a': a, 'flows': flows, 'Link capacity': 1000}).reset_index()
        arrival_times = arrival_times[arrival_times['flows'] > 1e-10]
    arrival_times.columns = ['i', 'j', 'k', 'time', 'flow', 'Link capacity']

    vertex_cap = []
    due_dates = []
    for r in range(len(arrival_times)):
        row = arrival_times.iloc[r]
        i = row['i']
        j = row['j']
        k = row['k']
        # vertex_cap.append(self.m._p_bar[i])
        try:
            due_dates.append(deadline[(i, j, k)])
        except:
            due_dates.append(12)

    # arrival_times['Link utilization'] = arrival_times['flow'] / arrival_times['Link capacity']
    # arrival_times['Link utilization'] = round(arrival_times['Link utilization'], 2)
    # arrival_times['Vertex capacity'] = vertex_cap
    # arrival_times['Vertex utilization'] = arrival_times['flow'] / arrival_times['Vertex capacity']
    # arrival_times['Vertex utilization'] = round(arrival_times['Vertex utilization'], 2)

    arrival_times = arrival_times[['i', 'j', 'k', 'time', 'flow']]

    arrival_times['due_date'] = due_dates
    arrival_times['lateness'] = arrival_times['time'] - arrival_times['due_date']
    arrival_times.loc[arrival_times['lateness'] < 0, 'lateness'] = 0
    # arrival_times['Fixed Penalty'] = 0
    # arrival_times.loc[arrival_times['lateness'] > 1e-10, 'Fixed Penalty'] = arrival_times[
    #                                                                             'flow'] * self.m._LatePenaltyInitial
    arrival_times['lateness'] = np.ceil(arrival_times['lateness']).astype(int)
    # arrival_times['Linear Penalty'] = arrival_times['lateness'] * arrival_times['flow'] * self.m._LatePenaltySlope
    # arrival_times['Linear Penalty'] = arrival_times['Linear Penalty'].astype(int)
    # arrival_times['Total Penalty'] = arrival_times['Fixed Penalty'] + arrival_times['Linear Penalty']
    arrival_times = arrival_times[
        ['i', 'j', 'k', 'time', 'flow', 'lateness']]
    arrival_times = arrival_times.sort_values(by=['time', 'i', 'j'])
    if id != None:
        arrival_times['id'] = id
    return arrival_times


def TASE_adapt(SC, V):
    V_type = {}
    # Checking for entities that are Part vs Manuf (Considering that we have no distributors in this instance)
    downstream = {}
    upstream = {}
    for v in V:
        downstream[v] = []
        upstream[v] = []
    for _, r in SC.iterrows():
        source = r['Source']
        destination = r['Destination']
        downstream[source].append(destination)
        upstream[destination].append(source)
    AgentType = {}
    parts = []  # Agents that qualify as parts (they start the SC)
    for idx, upstream_ents in upstream.items():
        if len(upstream_ents) == 0:
            parts.append(idx)
    for v in V:
        if v in parts:
            AgentType[v] = 'Part'
            V_type[v] = 'Part'
        elif len(downstream[v]) == 0:
            AgentType[v] = 'Retail'
            V_type[v] = 'Retail'
        else:
            AgentType[v] = 'Manuf'
    # Market = pd.read_excel('TASE_Setup.xlsx',sheet_name='Agent')
    # Market['AgentType'] = Market['AgentName'].map(AgentType)
    downstream = {}
    upstream = {}
    for v in V:
        downstream[v] = []
        upstream[v] = []
    for _, r in SC.iterrows():
        source = r['Source']
        destination = r['Destination']
        downstream[source].append(destination)
        upstream[destination].append(source)
    manufs = []
    manuf_set = []
    for v in V:
        if AgentType[v] == 'Manuf':
            manufs.append(v)
            manuf_set.append(v)
    manuf_tier = {}
    for manuf in manufs:
        manuf_tier[manuf] = None
    manuf_groups = {}

    # seed

    tier = 0
    manuf_groups[0] = []
    for j in manufs:
        upstream_manufs = 0
        for i in upstream[j]:
            if i in manufs:
                upstream_manufs += 1
        if upstream_manufs == 0:
            manuf_tier[j] = 0
            manuf_groups[0].append(j)
    while len(manuf_set) > 0:
        for i in manuf_groups[tier]:
            for j in downstream[i]:
                if j in manufs:
                    if tier + 1 not in manuf_groups.keys():
                        manuf_groups[tier + 1] = []
                    manuf_tier[j] = tier + 1
                    manuf_groups[tier + 1].append(j)
            if i in manuf_set:
                manuf_set.remove(i)
        if tier + 1 in manuf_groups.keys():
            manuf_groups[tier + 1] = list(set(manuf_groups[tier + 1]))
        tier += 1
    for manuf, tier in manuf_tier.items():
        V_type[manuf] = tier

    return V_type


def truncated_normal_distribution(mean_value, std_value, sample_num):
    # samples are truncated from 0 to mean+3std
    a = (0 - mean_value) / std_value
    b = (mean_value + 3 * std_value - mean_value) / std_value
    samples = truncnorm.rvs(a, b, loc=mean_value, scale=std_value, size=sample_num)
    # samples = samples.round().astype(int)

    return samples[0]
