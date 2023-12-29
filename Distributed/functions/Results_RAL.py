#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

import pandas as pd
import numpy as np
import seaborn as sns
from simulation import TASE_adapt
from statistics import mean, stdev
import json
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from scipy.stats import truncnorm


def truncated_normal_distribution(mean_value, std_value, sample_num):
    # samples are truncated from 0 to mean+3std
    if std_value == 0:
        return [mean_value] * sample_num

    a = (0 - mean_value) / std_value
    b = (mean_value + 3 * std_value - mean_value) / std_value
    samples = truncnorm.rvs(a, b, loc=mean_value, scale=std_value, size=sample_num)
    samples = samples.round().astype(int)

    return samples
def group_scenario_by_tier():
    SC = pd.read_excel('../initialization/TASE_Setup.xlsx', sheet_name='Link')[['Source', 'Destination']]
    V = list(set(list(SC.Source.unique()) + list(SC.Destination.unique())))
    V_type = TASE_adapt(SC, V)
    tier_members = {}
    tiers = ['Part', 0, 1, 2, 'Retail']
    for tier in tiers:
        tier_members[tier] = []
    for v, type in V_type.items():
        tier_members[type].append(v)
    return tier_members

def find_flow_to_check(ag_name, d, attitude):
    with open("../initialization/InitialPlans-New.json") as f:
        initial_plan = json.load(f)

    downstream = set()
    product = set()
    disrupted_flow = {}
    total_prod_need = 0
    for flow in initial_plan["Flows"]:
        if flow["Source"] == ag_name:
            downstream.add(flow["Dest"])
            product.add(flow["Product"])
            disrupted_flow[(flow["Source"], flow["Dest"], flow["Product"])] = flow["Value"]
            total_prod_need += flow["Value"]

    if attitude in ["averse", "neutral"]:
        filename = '../results/new/' + attitude + '_plan' + str(d) + '.json'
    elif attitude == "nominal":
        filename = '../results/new/' + attitude + '_plan.json'
    else:
        filename = '../results/new/' + attitude + '.json'
    with open(filename) as f:
        new_plan = json.load(f)

    changed_flow = {}
    for new_flow in new_plan[ag_name]["flows"]:
        if new_flow["Dest"] in downstream and new_flow["Product"] in product:
            changed_flow[(new_flow["Source"], new_flow["Dest"], new_flow["Product"])] = new_flow["Value"]

    initial_flows = {(flow["Source"], flow["Dest"], flow["Product"]): flow["Value"] for flow in initial_plan["Flows"]}
    current_flows = {(flow["Source"], flow["Dest"], flow["Product"]): flow["Value"] for flow in
                     new_plan[ag_name]["flows"]}

    flow_to_check = {}
    for f in changed_flow.keys():
        if f in initial_flows.keys() and f[0] != ag_name:
            flow_to_check[f] = changed_flow[f] - initial_flows[f]
        else:
            flow_to_check[f] = changed_flow[f]
    return flow_to_check

def calculate_total_lateness(lateness, final, ag_name, d, attitude):
    flow_to_check = find_flow_to_check(lateness, final, ag_name, d, attitude)
    # if attitude != "nominal":
    #     filename = '../results/' + attitude + '_plan' + str(d) + '.json'
    #     with open(filename) as f:
    #         new_plan = json.load(f)



    total_lateness = []
    total_late_prod = []
    for sample in lateness:
        if final:
            late = sum([res["Lateness"] for res in sample if "Customer" in res["Agent"]])
            prod = sum([res["Prod_amount"] for res in sample if "Customer" in res["Agent"]])
        else:
            # late = sum([res["Lateness"] for res in sample if res["Agent"] in downstream and res["Product"] in product])
            # prod = sum([res["Prod_amount"] for res in sample if res["Agent"] in downstream and res["Product"] in product])
            late = sum([res["Lateness"] for res in sample if (res["From"], res["Agent"], res["Product"]) in flow_to_check.keys()])
            prod = sum([res["Prod_amount"] for res in sample if (res["From"], res["Agent"], res["Product"]) in flow_to_check.keys()])
        total_lateness.append(late)
        total_late_prod.append(prod)
    # result = {"mean": mean(total_lateness), "std": stdev(total_lateness)}
    result = {"lateness": total_lateness, "late_prod": total_late_prod}
    return result

def calculate_lateness_distribution(lateness, final, ag_name, d, attitude):
    with open("../initialization/InitialPlans-New.json") as f:
        initial_plan = json.load(f)

    downstream = set()
    product = set()
    disrupted_flow = {}
    total_prod_need = 0
    for flow in initial_plan["Flows"]:
        if flow["Source"] == ag_name:
            downstream.add(flow["Dest"])
            product.add(flow["Product"])
            disrupted_flow[(flow["Source"], flow["Dest"], flow["Product"])] = flow["Value"]
            total_prod_need += flow["Value"]

    if attitude in ["averse", "neutral"]:
        filename = '../results/new/' + attitude + '_plan' + str(d) + '.json'
    elif attitude == "nominal":
        filename = '../results/new/' + attitude + '_plan.json'
    else:
        filename = '../results/new/' + attitude + '.json'
    with open(filename) as f:
        new_plan = json.load(f)

    changed_flow = {}
    for new_flow in new_plan[ag_name]["flows"]:
        if new_flow["Dest"] in downstream and new_flow["Product"] in product:
            changed_flow[(new_flow["Source"], new_flow["Dest"], new_flow["Product"])] = new_flow["Value"]

    initial_flows = {(flow["Source"], flow["Dest"], flow["Product"]): flow["Value"] for flow in initial_plan["Flows"]}
    current_flows = {(flow["Source"], flow["Dest"], flow["Product"]): flow["Value"] for flow in
                     new_plan[ag_name]["flows"]}

    flow_to_check = {}
    for f in changed_flow.keys():
        if f in initial_flows.keys() and f[0] != ag_name:
            flow_to_check[f] = changed_flow[f] - initial_flows[f]
        else:
            flow_to_check[f] = changed_flow[f]

    late_flow_to_check = []
    total_late_prod = []
    for sample in lateness:
        if final:
            pass
        else:
            late = [res for res in sample if (res["From"], res["Agent"], res["Product"]) in flow_to_check.keys()]
        late_flow_to_check.append(late)
    
    late_with_prod = []
    for sample_flow in late_flow_to_check:
        sample_res = {}
        caculated_prod = 0
        for res in sample_flow:
            try:
                sample_res[res["Lateness"]] += res["Prod_amount"]
            except:
                sample_res[res["Lateness"]] = res["Prod_amount"]
            caculated_prod += res["Prod_amount"]
        sample_res[0] = total_prod_need - caculated_prod
        late_with_prod.append(sample_res)
    # result = {"mean": mean(total_lateness), "std": stdev(total_lateness)}
    time_idx = set()
    for res in late_with_prod:
        for time in res.keys():
            time_idx.add(time)
    for res in late_with_prod:
        for time in time_idx:
            if time not in res.keys():
                res[time] = 0
    result = {time: 0 for time in time_idx}
    for time in time_idx:
        result[time] = {"mean": mean([res[time] for res in late_with_prod if time in res.keys()])/ total_prod_need,
                        "stdev": stdev([res[time] for res in late_with_prod if time in res.keys()])/ total_prod_need}
        # result[time] = [res[time]/ total_prod_need * 100 for res in late_with_prod if time in res.keys()]
    return result

def plot_lateness(result_diff_disrup_distribution, disruption):
    ag = "plastic_sup_4"
    attitude = ["nominal", "neutral", "averse"]
    res = {key: {} for key in disruption}
    for d in disruption:
        res[d] = {key: [] for key in ["time", "attitude", "value"]}
        for att in attitude:
            size = 0
            for t in result_diff_disrup_distribution[str(d)][ag][att].keys():
                res[d]["time"] += [t] * len(result_diff_disrup_distribution[str(d)][ag][att][t])
                size += len(result_diff_disrup_distribution[str(d)][ag][att][t])
                res[d]["value"] += result_diff_disrup_distribution[str(d)][ag][att][t]
            res[d]["attitude"] += [att] * size

    fig, axes = plt.subplots(2, 3, figsize=(30, 12))
    for d, ax in zip(disruption, axes.flat):

        df = pd.DataFrame(data=res[d])
        sns.violinplot(ax=ax, data=df, x="time", y="value", hue="attitude", palette="Pastel1", linewidth=1, width=0.5,
                       showmeans=True)
        time_names = [str(t) for t in result_diff_disrup_distribution[str(d)][ag]["nominal"].keys()]
        ax.set_xticklabels(time_names, fontsize=15)
        ax.set_ylim(0, None)
        ax.set_xlabel('Lateness', fontsize=15)
        ax.set_ylabel('Percentage of Late Products', fontsize=15)
        percent = int(round(d - 1, 1) * 100)
        title = 'Disrupted ' + ag + ' with ' + str(percent) + '% increased lead time'
        ax.set_title(title)

        # Add a legend
        ax.legend()

    plt.show()

    print("d")
    # simple_res = {key: [] for key in ["category", "attitude", "value"]}
    # simple_res["category"] = ["Level 0"] * len(tier_results["neutral"]["Part"]) + \
    #                         ["Level 1"] * len(tier_results["neutral"][0]) +\
    #                         ["Level 2"] * len(tier_results["neutral"][1]) +\
    #                         ["Level 0"] * len(tier_results["averse"]["Part"]) + \
    #                         ["Level 1"] * len(tier_results["averse"][0]) +\
    #                         ["Level 2"] * len(tier_results["averse"][1])
    # simple_res["attitude"] = ["Neutral"] * sum(len(tier_results["neutral"][tier]) for tier in final_result.keys()) + \
    #                          ["Averse"] * sum(len(tier_results["averse"][tier]) for tier in final_result.keys())
    #
    # for i in ["neutral", "averse"]:
    #     for tier in final_result.keys():
    #         simple_res["value"] +=  tier_results[i][tier]
    #
    # fig, ax = plt.subplots(figsize=(4, 4.5))
    # df = pd.DataFrame(data=simple_res)
    # sns.violinplot(ax=ax, data=df, x="category", y="value", hue="attitude", palette="Pastel1", linewidth=1, width=0.5, showmeans=True)
    # plt.show()
    # ax.set_xticklabels(['Level 0', 'Level 1', 'Level 2'], fontsize=15)
    # ax.set(xlabel=None, ylabel=None)
    # ax.set_title("title[met]", fontsize=15)
    # ax.set_ylabel("y_label[met]", fontsize=15)
    #
    # plt.show()

def plot_mixed_risk(final_result, tier_results):
    fig, ax = plt.subplots(figsize=(4, 4.5))

    sce = 10
    for tier in final_result.keys():
        mean_value = [final_result[tier]["nominal"]["mean"]] * sce
        stdev_value = [final_result[tier]["nominal"]["stdev"]] * sce
        plt.plot(range(sce), mean_value)
        np1 = np.array(mean_value)
        np2 = np.array(stdev_value)
        plt.fill_between(range(sce), np1+np2, np1-np2, alpha=0.3, zorder = 3)
    plt.show()
    print("d")

def plot_agent_lateness(results, ag_name):

    fig, axes = plt.subplots(1, 2, figsize=(4, 4.5))

    metrics = ["lateness", "late_prod"]
    category = ["nominal", "neutral", "averse"]
    for met, ax in zip(metrics, axes.flat):
        data = [results[cat][met] for cat in category]
        simple_res = {key: [] for key in ["category", "value"]}
        simple_res["category"] = [cat for cat in category for _ in range(len(data[0]))]
        simple_res["value"] = [val for sublist in data for val in sublist]
        df = pd.DataFrame(data=simple_res)
        sns.violinplot(ax=ax, data=df, x="category", y="value", palette="Pastel1", linewidth=1, width=0.5, showmeans=True)
        ax.set_xticklabels(category, fontsize=15)
        ax.set(xlabel=None, ylabel=None)
        ax.set_title(ag_name, fontsize=15)
        ax.set_ylabel(met, fontsize=15)
    # ax.get_legend().remove()
    # handles, labels = ax.get_legend_handles_labels()
    # for line in ax.get_lines()[5::14]:
    #     line.set_marker("^")
    #     line.set_markerfacecolor('#E88482')
    #     line.set_markeredgecolor("black")
    #     line.set_markersize("10")
    # for line in ax.get_lines()[12::14]:
    #     line.set_marker("s")
    #     line.set_markerfacecolor('#6699CC')
    #     line.set_markeredgecolor("black")
    #     line.set_markersize("10")
    # handles += [
    #     Line2D([0], [0], marker='^', color='w', markeredgecolor='black', markerfacecolor='#E88482', markersize=10),
    #     Line2D([0], [0], marker='s', color='w', markeredgecolor='black', markerfacecolor='#6699CC', markersize=10)]
    # labels += ["Mean Value (Centralized)", "Mean Value (Distributed)"]

    # ax.legend(handles, labels, fontsize=12)
    plt.show()


def plot_diff_disruption(result_diff_disrup, disruption):

    data = {}
    for d in disruption:
        res = result_diff_disrup[str(d)]
        data[d] = {}
        for ag in res.keys():
            data[d][ag] = {}
            for attitude in ["nominal", "neutral", "averse"]:
                data[d][ag][attitude] = {}
                for met in ["lateness", "late_prod"]:
                    data[d][ag][attitude][met] = {"mean": mean(res[ag][attitude][met]), "stdev": stdev(res[ag][attitude][met])}

    fig, axes = plt.subplots(1, 3, figsize=(20, 8))
    for agent, ax in zip(data[d].keys(), axes.flat):
        for attitude in ["nominal", "neutral", "averse"]:
            time = np.array([data[d][agent][attitude]["lateness"]["mean"] for d in disruption])
            time_err = np.array([data[d][agent][attitude]["lateness"]["stdev"] for d in disruption])
            prod = np.array([data[d][agent][attitude]["late_prod"]["mean"] for d in disruption])
            prod_err = np.array([data[d][agent][attitude]["late_prod"]["stdev"] for d in disruption])
            marker_sizes = np.array([100*(d-1) for d in disruption])
            ax.errorbar(time, prod, xerr=time_err, yerr=prod_err, fmt='o', capsize=3, label=attitude, markersize=0)
            ax.scatter(time, prod, s=marker_sizes)
        # Set the axis labels and title
        ax.set_xlabel('Lateness', fontsize=15)
        ax.set_ylabel('Number of Late Products', fontsize=15)
        title = 'Disruption: ' + agent + '\nMean and Standard Deviation of the Metrics'
        ax.set_title(title)

        # Add a legend
        ax.legend()

    # Display the plot
    plt.show()
    print("finish")


def plot_distribution(result, disruption):
    data = {}
    for d in disruption:
        res = result[str(d)]
        data[d] = {}
        for ag in res.keys():
            data[d][ag] = {}
            for attitude in ["nominal", "neutral", "averse"]:
                data[d][ag][attitude] = {"time": [key for key in res[ag][attitude].keys()],
                                         "percentage": [res[ag][attitude][key] for key in res[ag][attitude].keys()]}

    # fig, axes = plt.subplots(1, 4, figsize=(20, 5), gridspec_kw={'width_ratios': [2, 5, 7, 10]})
    fig, axes = plt.subplots(2, 2, figsize=(12, 15))

    agent = "cluster_sup_3"
    for d, ax in zip([1.0, 1.2, 1.6, 2.0], axes.flat):
        if d == 1.0:
            max_time = max([key for key in result[str(d)][agent]["nominal"].keys()])
            time_names = [i for i in range(max_time + 1)]
            # x = np.arange(len(time_names))
            x = np.arange(8)
            data_1, data_1e = [], []
            # for i in time_names:
            #     if i in result[str(d)][agent]["nominal"].keys():
            for i in range(8):
                if i in time_names and i in result[str(d)][agent]["nominal"].keys():
                    data_1.append(result[str(d)][agent]["nominal"][i]["mean"] * 100)
                    data_1e.append(result[str(d)][agent]["nominal"][i]["stdev"] * 100)
                else:
                    data_1.append(0)
                    data_1e.append(0)

            # Set the width of the bars
            bar_width = 0.25
            # Create the bar plot
            ax.bar(x, data_1, yerr=data_1e, width=bar_width, label="Initial Plan", color="#CCCCCC",
                   ecolor='grey', capsize=5)
            ax.set_title("Initial Plan", fontsize=15)


        else:
            max_time = max(max([key for key in result[str(d)][agent][attitude].keys()]) for attitude in ["nominal", "neutral", "averse"])
            time_names = [i for i in range(max_time+1)]
            # x = np.arange(len(time_names))
            x = np.arange(8)
            data_1, data_2, data_3 = [], [], []
            data_1e, data_2e, data_3e = [], [], []
            # for i in time_names:
            for i in range(8):
                # if i in result[str(d)][agent]["nominal"].keys():
                if i in time_names and i in result[str(d)][agent]["nominal"].keys():
                    data_1.append(result[str(d)][agent]["nominal"][i]["mean"]*100)
                    data_1e.append(result[str(d)][agent]["nominal"][i]["stdev"] * 100)
                else:
                    data_1.append(0)
                    data_1e.append(0)
                # if i in result[str(d)][agent]["neutral"].keys():
                if i in time_names and i in result[str(d)][agent]["neutral"].keys():
                    data_2.append(result[str(d)][agent]["neutral"][i]["mean"]*100)
                    data_2e.append(result[str(d)][agent]["neutral"][i]["stdev"] * 100)
                else:
                    data_2.append(0)
                    data_2e.append(0)
                # if i in result[str(d)][agent]["averse"].keys():
                if i in time_names and i in result[str(d)][agent]["averse"].keys():
                    data_3.append(result[str(d)][agent]["averse"][i]["mean"]*100)
                    data_3e.append(result[str(d)][agent]["averse"][i]["stdev"] * 100)
                else:
                    data_3.append(0)
                    data_3e.append(0)

            # Set the width of the bars
            bar_width = 0.25
            # Create the bar plot
            ax.bar(x - bar_width, data_1, yerr=data_1e, width=bar_width, label="Initial Plan", color="#CCCCCC", ecolor='grey', capsize=5)
            ax.bar(x, data_2, yerr=data_2e, width=bar_width, label="New Plan with Risk-neutral", color="#74AED4", ecolor='grey',capsize=5)
            ax.bar(x + bar_width, data_3, yerr=data_3e, width=bar_width, label="New Plan with Risk-averse", color="#ECA8A9", ecolor='grey', capsize=5)

            percent = int(round(d - 1, 1) * 100)
            title = 'Lead time of ' + agent + ' increases by ' + str(percent) + '%'
            # if d == 1.2:
            #     title = 'New Plan: ' + agent + ' with ' + str(percent) + '% \nincreased lead time'
            ax.set_title(title, fontsize=15)
            if d == 1.2: ax.legend(fontsize=12)

        # Set the x-axis tick labels
        ax.set_xticks(x)
        # ax.set_xticklabels(time_names)
        ax.set_xticklabels([i for i in range(8)])
        ax.set_ylim(0, 110)
        ax.set_ylabel('Percentage of Products', fontsize=15)
        # Set the axis labels and title
        ax.set_xlabel('Lateness', fontsize=15)



        # Add a legend


    # Display the plot
    plt.subplots_adjust(hspace=0.3)
    plt.show()
    print("finish")


def plot_distribution_diff_risk(result, risk_attitude):
    data = {}
    for d in [1.6]:
        res = result[str(d)]
        data[d] = {}
        for ag in res.keys():
            data[d][ag] = {}
            for attitude in risk_attitude:
                data[d][ag][attitude] = {"time": [key for key in res[ag][attitude].keys()], "percentage": [res[ag][attitude][key] for key in res[ag][attitude].keys()]}

    fig, axes = plt.subplots(2, 4, figsize=(25, 12))
    # agent = "plastic_sup_4"
    agent = "cluster_sup_3"
    for r, ax in zip(risk_attitude, axes.flat):
        max_time = max([key for key in result[str(d)][agent][r].keys()])
        time_names = [i for i in range(max_time+1)]
        x = np.arange(len(time_names))
        data_1, data_1e = [], []
        for i in time_names:
            if i in result[str(d)][agent][r].keys():
                data_1.append(result[str(d)][agent][r][i]["mean"]*100)
                data_1e.append(result[str(d)][agent][r][i]["stdev"] * 100)
            else:
                data_1.append(0)
                data_1e.append(0)

        # Set the width of the bars
        bar_width = 0.25
        # Create the bar plot
        # ax.bar(x - bar_width, data_1, width=bar_width, label="Initial Plan")
        ax.bar(x, data_1, yerr = data_1e, width=bar_width, label = r)
        # ax.bar(x + bar_width, data_3, width=bar_width, label="New Plan with Risk-averse")

        # Set the x-axis tick labels
        ax.set_xticks(x)
        ax.set_xticklabels(time_names)
        ax.set_ylim(0, 100)
        # Set the axis labels and title
        ax.set_xlabel('Lateness', fontsize=15)
        ax.set_ylabel('Percentage of Late Products', fontsize=15)
        title = 'Disrupted ' + agent + ' with ' + r
        ax.set_title(title)

        # Add a legend
        ax.legend()

    # Display the plot
    plt.show()
    print("finish")

def plot_distribution_group_risk(result, risk_attitude):
    # data = {}
    # for d in [1.6]:
    #     res = result[str(d)]
    #     data[d] = {}
    #     for ag in res.keys():
    #         data[d][ag] = {}
    #         for attitude in risk_attitude:
    #             data[d][ag][attitude] = {"time": [key for key in res[ag][attitude].keys()], "percentage": [res[ag][attitude][key] for key in res[ag][attitude].keys()]}

    # agent = "plastic_sup_4"
    agent = "cluster_sup_3"
    total = 360
    max_time = max(max([key for key in result["1.6"][agent][r].keys()]) for r in risk_attitude)-2
    time_names = [i for i in range(max_time+1)]
    x = np.arange(len(time_names))
    data, data_e = {}, {}
    for r in risk_attitude:
        data[r] = []
        data_e[r] = []
        for i in time_names:
            if i in result["1.6"][agent][r].keys():
                data[r].append(result["1.6"][agent][r][i]["mean"] * total)
                data_e[r].append(result["1.6"][agent][r][i]["stdev"] * total)
            else:
                data[r].append(0)
                data_e[r].append(0)
    group_names = ["0/3 Risk-averse Agents", "1/3 Risk-averse Agents", "2/3 Risk-averse Agents", "3/3 Risk-averse Agents"]
    group_data = {key: [] for key in group_names}
    for idx in range(len(time_names)):
        group_data["0/3 Risk-averse Agents"].append(data["FalseFalseFalse"][idx]/total*100)
        group_data["1/3 Risk-averse Agents"].append(mean([data[att][idx] for att in ["TrueFalseFalse", "FalseTrueFalse", "FalseFalseTrue"]])/total*100)
        group_data["2/3 Risk-averse Agents"].append(mean([data[att][idx] for att in ["TrueTrueFalse", "FalseTrueTrue", "TrueFalseTrue"]])/total*100)
        group_data["3/3 Risk-averse Agents"].append(data["TrueTrueTrue"][idx]/total*100)

    group_data_e = {key: [] for key in group_names}
    for idx in range(len(time_names)):
        group_data_e["0/3 Risk-averse Agents"].append(data_e["FalseFalseFalse"][idx] / total * 100)
        group_data_e["1/3 Risk-averse Agents"].append(
            mean([data_e[att][idx] for att in ["TrueFalseFalse", "FalseTrueFalse", "FalseFalseTrue"]]) / total * 100)
        group_data_e["2/3 Risk-averse Agents"].append(
            mean([data_e[att][idx] for att in ["TrueTrueFalse", "FalseTrueTrue", "TrueFalseTrue"]]) / total * 100)
        group_data_e["3/3 Risk-averse Agents"].append(data_e["TrueTrueTrue"][idx] / total * 100)

    fig, ax = plt.subplots(figsize=(15, 6))
    # Set the width of the bars
    bar_width = 0.2

    # Create the bar plot
    position = {"0/3 Risk-averse Agents": -1.5, "1/3 Risk-averse Agents": -0.5, "2/3 Risk-averse Agents": 0.5, "3/3 Risk-averse Agents": 1.5}
    color_decay = {"0/3 Risk-averse Agents": 0.25, "1/3 Risk-averse Agents": 0.5, "2/3 Risk-averse Agents": 0.75,
                "3/3 Risk-averse Agents": 1}
    for case in group_names:
        ax.bar(x + position[case]*bar_width, group_data[case], yerr=group_data_e[case], width=bar_width, label=case, color='#74AED4', alpha=color_decay[case], ecolor='grey', capsize=5)

    # Set the x-axis tick labels
    ax.set_xticks(x)
    ax.set_xticklabels(time_names)
    ax.set_ylim(0, 100)
    # Set the axis labels and title
    ax.set_xlabel('Lateness', fontsize=15)
    ax.set_ylabel('Percentage of Late Products', fontsize=15)
    title = 'Disrupted ' + agent + ' with different risk attitudes'
    ax.set_title(title)

    # Add a legend
    ax.legend()

    # Display the plot
    plt.show()
    print("finish")

def plot_diff_risk_violin(result_diff_disrup_distribution, risk_attitude):
    ag = "cluster_sup_3"
    risk_groupname = ["0/3 Risk-averse Agents", "1/3 Risk-averse Agents", "2/3 Risk-averse Agents", "3/3 Risk-averse Agents"]
    risk_group = {"0/3 Risk-averse Agents": ["FalseFalseFalse"],
                  "1/3 Risk-averse Agents": ["TrueFalseFalse", "FalseTrueFalse", "FalseFalseTrue"],
                  "2/3 Risk-averse Agents": ["FalseTrueTrue", "TrueFalseTrue", "TrueTrueFalse"],
                  "3/3 Risk-averse Agents": ["TrueTrueTrue"]}
    data = {key: [] for key in ["time", "risk", "value"]}
    res = result_diff_disrup_distribution["1.6"][ag]
    for risk in risk_groupname:
        size = 0
        for r in risk_group[risk]:
            for t in res[r].keys():
                data["time"] += [t] * len(res[r][t])
                size += len(res[r][t])
                data["value"] += res[r][t]
        data["risk"] += [risk] * size

    fig, ax = plt.subplots(figsize=(15, 4.5))

    df = pd.DataFrame(data=data)
    sns.boxplot(ax=ax, data=df, x="time", y="value", hue="risk", palette="Pastel1", linewidth=1, width=0.5,
                   showmeans=True)
    time_names = [str(t) for t in res["TrueFalseTrue"].keys()]
    ax.set_xticklabels(time_names, fontsize=15)
    # ax.set_ylim(0, None)
    ax.set_xlabel('Lateness', fontsize=15)
    ax.set_ylabel('Percentage of Late Products', fontsize=15)
    title = 'Disrupted ' + ag + ' with different risk attitude'
    ax.set_title(title)

    # Add a legend
    ax.legend()

    plt.show()

    print("d")

def calculate_cost(ag_name, d, attitude):
    filename = '../initialization/TASE_Setup.xlsx'
    info = pd.read_excel(filename, sheet_name=None)
    agent_product = info["Agent"].set_index(['AgentName', 'ProductType'])
    transport_link = info["Link"].set_index(['Source', 'Destination'])
    flow_to_check = find_flow_to_check(ag_name, d, attitude)
    downstream = set()
    product = set()
    for f in flow_to_check.keys():
        downstream.add(f[1])
        product.add(f[2])
    demand = {"cluster_1": 60, "cluster_2": 140, "cluster_3": 160}
    compensate = {p: demand[p]-sum(flow_to_check[f] for f in flow_to_check.keys() if f[2] == p) for p in product}
    sup = {"cluster_1": "cluster_sup_1", "cluster_2": "cluster_sup_4", "cluster_3": "cluster_sup_4"}
    assy = {"cluster_1": "cockpit_assy_1", "cluster_2": "cockpit_assy_2", "cluster_3": "cockpit_assy_3"}
    for p in compensate.keys():
        if compensate[p] > 0.1:
            flow_to_check[(sup[p], assy[p], p)] += compensate[p]

    result = {ag: {key: 0 for key in ["cost", "penalty"]} for ag in downstream}
    for f in flow_to_check.keys():
        result[f[1]]["cost"] += flow_to_check[f] * (agent_product.loc[(f[0], f[2]), "ProductionCost"] + transport_link.loc[(f[0], f[1]), "TransportCost"])

    # Hard code information
    with open("../initialization/InitialPlans-New.json") as f:
        initial_plan = json.load(f)
    nominal_prod_time = {"cluster_1": 4, "cluster_2": 5, "cluster_3": 4}
    deadline = {"cockpit_assy_1": 11, "cockpit_assy_2": 11, "cockpit_assy_3": 11}
    planned_arrival_time = {}
    sce_num = 50


    response_time = {}
    for f in flow_to_check.keys():
        trust_level = agent_product.loc[(f[0], f[2]), "TrustLevel"]
        if f[0] == "cluster_sup_3":
            # planned_arrival_time[f] = d * agent_product.loc[(f[0], f[2]), "LeadTime"] + nominal_prod_time[f[2]]
            leadtime_est = truncated_normal_distribution(d*agent_product.loc[(f[0], f[2]), "LeadTime"],
                                                                 agent_product.loc[(f[0], f[2]), "Sigma"], sce_num)
        else:
            # planned_arrival_time[f] = agent_product.loc[(f[0], f[2]), "LeadTime"] + nominal_prod_time[f[2]]
            leadtime_est = truncated_normal_distribution(agent_product.loc[(f[0], f[2]), "LeadTime"],
                                                                 agent_product.loc[(f[0], f[2]), "Sigma"], sce_num)

        prodtime_est = truncated_normal_distribution(nominal_prod_time[f[2]], 0.1 * nominal_prod_time[f[2]], sce_num)
        response_time[f] = mean([leadtime_est[i]+prodtime_est[i] for i in range(sce_num)])
        if attitude == "nominal":
            planned_arrival_time[f] = [leadtime_est[i]+prodtime_est[i] for i in range(sce_num)]
        else:
            planned_arrival_time[f] = truncated_normal_distribution(response_time[f], trust_level * response_time[f], sce_num)

    for f in flow_to_check.keys():

        result[f[1]]["penalty"] += mean([max(0, planned_arrival_time[f][i] - deadline[f[1]]) for i in range(sce_num)])


    return result

def draw_new_plan(ag_name, d, risk_attitude):
    filename = '../initialization/TASE_Setup.xlsx'
    info = pd.read_excel(filename, sheet_name=None)
    agent_product = info["Agent"].set_index(['AgentName', 'ProductType'])
    transport_link = info["Link"].set_index(['Source', 'Destination'])
    title_names = {"TrueTrueTrue": "A1: Averse, A2: Averse, A3: Averse", "TrueTrueFalse": "A1: Averse, A2: Averse, A3: Neutral",
                   "TrueFalseTrue": "A1: Averse, A2: Neutral, A3: Averse", "TrueFalseFalse": "A1: Averse, A2: Neutral, A3: Neutral",
                 "FalseTrueTrue": "A1: Neutral, A2: Averse, A3: Averse", "FalseTrueFalse": "A1: Neutral, A2: Averse, A3: Neutral",
                   "FalseFalseTrue": "A1: Neutral, A2: Neutral, A3: Averse", "FalseFalseFalse": "A1: Neutral, A2: Neutral, A3: Neutral",
                   "initial": "The initial plan"}
    risk_color = {"TrueTrueTrue": ["cockpit_assy_1", "cockpit_assy_2", "cockpit_assy_3"],
                   "TrueTrueFalse": ["cockpit_assy_1", "cockpit_assy_2"],
                   "TrueFalseTrue": ["cockpit_assy_1", "cockpit_assy_3"],
                   "TrueFalseFalse": ["cockpit_assy_1"],
                   "FalseTrueTrue": ["cockpit_assy_2", "cockpit_assy_3"],
                   "FalseTrueFalse": ["cockpit_assy_2"],
                   "FalseFalseTrue": ["cockpit_assy_3"],
                   "FalseFalseFalse": [],
                   "initial": ["cockpit_assy_1", "cockpit_assy_2", "cockpit_assy_3"]}
    result_subnetwork = {att: {"G": None, "E_width": {}} for att in risk_attitude}
    ColorMap = {'cluster_1': "#E4A6BD",
                'cluster_2': "#C0BFDF",
                'cluster_3': "#67ADB7",
                0: "#9DC3E6",
                1: "#F4B183",
                2: "#AFACB7"}
    fig, axes = plt.subplots(3, 3, figsize=(15, 30))
    for attitude, ax in zip(risk_attitude, axes.flat):
        V, E = [], []
        if attitude == "initial":
            flow_to_check = {("cluster_sup_3", "cockpit_assy_1", "cluster_1"): 60,
                             ("cluster_sup_3", "cockpit_assy_2", "cluster_2"): 140,
                             ("cluster_sup_3", "cockpit_assy_3", "cluster_3"): 160}
        else:
            flow_to_check = find_flow_to_check(ag_name, d, attitude)
        downstream = set()
        product = set()
        for f in flow_to_check.keys():
            downstream.add(f[1])
            product.add(f[2])
        demand = {"cluster_1": 60, "cluster_2": 140, "cluster_3": 160}
        compensate = {p: demand[p] - sum(flow_to_check[f] for f in flow_to_check.keys() if f[2] == p) for p in product}
        sup = {"cluster_1": "cluster_sup_1", "cluster_2": "cluster_sup_4", "cluster_3": "cluster_sup_4"}
        assy = {"cluster_1": "cockpit_assy_1", "cluster_2": "cockpit_assy_2", "cluster_3": "cockpit_assy_3"}
        for p in compensate.keys():
            if compensate[p] > 0.1:
                flow_to_check[(sup[p], assy[p], p)] += compensate[p]
        value = {}
        prod = {}
        for f in flow_to_check.keys():
            if f[0] not in V: V.append(f[0])
            if f[1] not in V: V.append(f[1])
            if (f[0], f[1]) not in E:
                E.append((f[0], f[1]))
                value[(f[0], f[1])] = flow_to_check[f]
                prod[(f[0], f[1])] = (f[2], flow_to_check[f])
        V = {"cluster_sup_1","cluster_sup_2","cluster_sup_3","cluster_sup_4", "cockpit_assy_1", "cockpit_assy_2", "cockpit_assy_3"}
        level = {}
        color_level = {}
        for v in V:
            if "sup" in v:
                level[v] = 0
                color_level[v] = 0
            if "assy" in v:
                level[v] = 1
                color_level[v] = 1
                if v not in risk_color[attitude]:
                    color_level[v] = 2
        G = nx.DiGraph()
        G.add_nodes_from(V)
        G.add_edges_from(E)
        nx.set_node_attributes(G, color_level, name='type')
        nx.set_node_attributes(G, level, name='subset')
        nx.set_edge_attributes(G, prod, name='prod')
        nx.set_edge_attributes(G, value, name='value')
        result_subnetwork[attitude]["G"] = G
        result_subnetwork[attitude]["E_width"] = value

        node_pose = nx.multipartite_layout(G)
        node_pose["cluster_sup_1"][1] = 1
        node_pose["cluster_sup_2"][1] = 0.333
        node_pose["cluster_sup_3"][1] = -0.333
        node_pose["cluster_sup_4"][1] = -1
        node_pose["cockpit_assy_1"][1] = 1
        node_pose["cockpit_assy_2"][1] = 0
        node_pose["cockpit_assy_3"][1] = -1
        node_colors = [ColorMap[type] for type in nx.get_node_attributes(G, 'type').values()]
        node_label_map = {"cluster_sup_1": "S1", "cluster_sup_2": "S2", "cluster_sup_3": "S3", "cluster_sup_4": "S4", "cockpit_assy_1": "A1", "cockpit_assy_2": "A2", "cockpit_assy_3": "A3"}
        edge_colors = [ColorMap[type[0]] for type in nx.get_edge_attributes(G, 'prod').values()]
        edge_width = [0.05*type[1]+0.2 for type in nx.get_edge_attributes(G, 'prod').values()]
        # nx.draw_networkx(G, node_color=node_colors, linewidths=0.5, edgecolors="black", node_size=1500,
        #                  pos=node_pose, with_labels=True, labels=node_labels,  arrows=True, edge_color=edge_colors,
        #                  ax=ax, width=edge_width, arrowsize=50, arrowstyle="->")
        nx.draw_networkx_nodes(G, node_color=node_colors, linewidths=0.5, node_size=800,  pos=node_pose, ax=ax, alpha=0.8)
        nx.draw_networkx_labels(G, pos=node_pose, labels=node_label_map, ax=ax)
        nx.draw_networkx_edges(G, node_pose, style='dashed', arrows=True, edge_color=edge_colors, width=edge_width, arrowsize=50, arrowstyle="->", ax=ax)
        nx.draw_networkx_edge_labels(G, node_pose, edge_labels=value, ax=ax, label_pos=0.33)
        ax.axis('off')
        ax.set_title(title_names[attitude], fontsize=15)
    handles = [Line2D([0], [0], marker='o', color='w', markeredgecolor=None, markerfacecolor=ColorMap[key], markersize=20) for
        key in [1, 2, 0]] + [Line2D([0, 5], [0, 5], linewidth=5, color=ColorMap[key], linestyle='dashed') for
        key in ["cluster_1", "cluster_2", "cluster_3"]]

    labels = ["risk-averse cockpit_assy_#", "risk-neutral cockpit_assy_#","cluster_sup_#",  "cluster_1", "cluster_2",
              "cluster_3"]
    # fig.supxlabel('Normalized metric values of the difference between centralized and distributed approaches')
    # fig.supylabel('Level of connectivity')
    fig.legend(handles, labels, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0), fontsize=15)
    plt.subplots_adjust(hspace=0.3)
    plt.show()
    print("plot")

print(4>3==3)

risk_attitude = ["initial", "TrueTrueTrue", "FalseFalseFalse",
                 "FalseTrueTrue", "TrueFalseTrue", "TrueTrueFalse",
                 "TrueFalseFalse", "FalseTrueFalse", "FalseFalseTrue"]
draw_new_plan("cluster_sup_3", 1.6, risk_attitude)
disruption = [round(1.2 + 0.2 * i, 2) for i in range(5)]
result_diff_disrup = {}
result_diff_disrup_distribution = {}
cost_result = {}
for d in disruption:
    filename = '../results/new/result/nominal_result' + str(d) + '.json'
    with open(filename) as f:
        nominal_result = json.load(f)

    filename = '../results/new/result/neutral_result' + str(d) + '.json'
    with open(filename) as f:
        neutral_result = json.load(f)

    filename = '../results/new/result/averse_result' + str(d) + '.json'
    with open(filename) as f:
        averse_result = json.load(f)

    final_results = {}
    result_distribution = {}
    for ag in nominal_result.keys():
        # final_results[ag] = {}
        # final_results[ag]["nominal"] = calculate_lateness_distribution(nominal_result[ag], False, ag, d, "nominal")
        # final_results[ag]["neutral"] = calculate_lateness_distribution(neutral_result[ag], False, ag, d, "neutral")
        # final_results[ag]["averse"] = calculate_lateness_distribution(averse_result[ag], False, ag, d, "averse")
        result_distribution[ag] = {}
        result_distribution[ag]["nominal"] = calculate_lateness_distribution(nominal_result[ag], False, ag, d, "nominal")
        result_distribution[ag]["neutral"] = calculate_lateness_distribution(neutral_result[ag], False, ag, d, "neutral")
        result_distribution[ag]["averse"] = calculate_lateness_distribution(averse_result[ag], False, ag, d, "averse")
        # plot_agent_lateness(final_results[ag], ag)
        # print("t")
    result_diff_disrup[str(d)] = final_results
    result_diff_disrup_distribution[str(d)] = result_distribution

    res_by_disruption = {}
    res_by_disruption["nominal"] = calculate_cost("cluster_sup_3", d, "nominal")
    res_by_disruption["neutral"] = calculate_cost("cluster_sup_3", d, "neutral")
    res_by_disruption["averse"] = calculate_cost("cluster_sup_3", d, "averse")

    cost_result[str(d)] = res_by_disruption

table = {}
for key in ["1.0", "1.2", "1.6", "2.0"]:
    table[key] = {}
    if key == "1.0":
        table[key]["nominal"] = {"cost": sum(cost_result["1.2"]["nominal"][ag]["cost"] for ag in cost_result["1.2"]["nominal"].keys()),
                                 "penalty": sum(cost_result["1.2"]["nominal"][ag]["penalty"] for ag in cost_result["1.2"]["nominal"].keys())}
        table[key]["nominal"]["total"] = table[key]["nominal"]["cost"] + 1e5 * table[key]["nominal"]["penalty"]
    else:
        for at in ["neutral", "averse"]:
            table[key][at] = {
                "cost": sum(cost_result[key][at][ag]["cost"] for ag in cost_result["1.2"]["nominal"].keys()),
                "penalty": sum(
                    cost_result[key][at][ag]["penalty"] for ag in cost_result["1.2"]["nominal"].keys())}
            table[key][at]["total"] = table[key][at]["cost"] + 1e5 * table[key][at]["penalty"]

filename = '../results/new/result/initial_plan_result.json'
with open(filename) as f:
    initial_result = json.load(f)
result_distribution = {}
d = 1.0
for ag in initial_result.keys():
    result_distribution[ag] = {}
    result_distribution[ag]["nominal"] = calculate_lateness_distribution(initial_result[ag], False, ag, d, "nominal")
result_diff_disrup_distribution[str(d)] = result_distribution
# plot_lateness(result_diff_disrup_distribution, disruption)

plot_distribution(result_diff_disrup_distribution, disruption)

result_diff_attitude_distribution = {}
risk_attitude = ["TrueTrueTrue", "TrueTrueFalse", "TrueFalseTrue", "TrueFalseFalse",
                 "FalseTrueTrue", "FalseTrueFalse", "FalseFalseTrue", "FalseFalseFalse"]
result_distribution = {}
for ag in ["cluster_sup_3"]:
    result_distribution[ag] = {}
    for r in risk_attitude:
        filename = '../results/new/result/' + r + 'result.json'
        with open(filename) as f:
            risk_result = json.load(f)
        result_distribution[ag][r] = calculate_lateness_distribution(risk_result[ag], False, ag, 1.6, r)
result_diff_attitude_distribution["1.6"] = result_distribution
# plot_diff_risk_violin(result_diff_attitude_distribution, risk_attitude)
# plot_distribution_diff_risk(result_diff_attitude_distribution, risk_attitude)
# plot_distribution_group_risk(result_diff_attitude_distribution, risk_attitude)
# plot_diff_disruption(result_diff_disrup, disruption)

# cost = calculate_cost(disruption, risk_attitude)

# tier_agents = group_scenario_by_tier()
# tiers = ['Part', 0, 1]
# tier_result_nominal, tier_result_averse, tier_result_neutral = {}, {}, {}
# for tier in tiers:
#     tier_result_nominal[tier] = []
#     tier_result_averse[tier] = []
#     tier_result_neutral[tier] = []
#     for ag in tier_agents[tier]:
#         try:
#             res = calculate_total_lateness(nominal_result[ag])
#             tier_result_nominal[tier].append(res["mean"])
#             res = calculate_total_lateness(averse_result[ag])
#             tier_result_averse[tier].append(res["mean"])
#             res = calculate_total_lateness(neutral_result[ag])
#             tier_result_neutral[tier].append(res["mean"])
#         except: pass
#
# final_result = {}
# for tier in tiers:
#     final_result[tier] = {"nominal": {}, "averse": {}, "neutral": {}}
#
#     final_result[tier]["nominal"]["mean"] = mean(tier_result_nominal[tier])
#     try:
#         final_result[tier]["nominal"]["stdev"] = stdev(tier_result_nominal[tier])
#     except:
#         final_result[tier]["nominal"]["stdev"] = 0
#
#     final_result[tier]["averse"]["mean"] = mean(tier_result_averse[tier])
#     try:
#         final_result[tier]["averse"]["stdev"] = stdev(tier_result_averse[tier])
#     except:
#         final_result[tier]["averse"]["stdev"] = 0
#
#     final_result[tier]["neutral"]["mean"] = mean(tier_result_neutral[tier])
#     try:
#         final_result[tier]["neutral"]["stdev"] = stdev(tier_result_neutral[tier])
#     except:
#         final_result[tier]["neutral"]["stdev"] = 0
#
# tier_results = {"nominal": tier_result_nominal, "averse": tier_result_averse, "neutral": tier_result_neutral}

# plot_mixed_risk(final_result, tier_results)
# plot_lateness(final_result, tier_results)
# plot_agent_lateness(final_result, tier_results)
print("d")