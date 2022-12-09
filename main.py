import sys
import gurobipy as gp
import numpy as np
import pandas as pd
from scipy.stats import truncnorm
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.lines as mlines
import json

with open('Distributed/results/Distributed_results.json') as f:
    distributed_data = json.load(f)
with open('CentralizedResults/Centralized_results.json') as f:
    centralized_results = json.load(f)
with open('CentralizedResults/runtime.json') as f:
    centralized_runtime = json.load(f)
with open('CentralizedResults/communication.json') as f:
    centralized_communication = json.load(f)

for key in centralized_results:
    centralized_results[key]["results"]["M_e"] = centralized_communication[key]
    centralized_results[key]["results"]["T_e"] = centralized_runtime[key]

agent_attributes = {"g_in": {}, "g_out": {}, "g_com": {}, "l_max": {}, "P": {}, "Q": {}, "F": {}}

for key in agent_attributes.keys():
    for agent in distributed_data.keys():
        agent_attributes[key][agent] = distributed_data[agent]["attributes"][key]

sorted_by_g_in = sorted(agent_attributes["g_in"].items(), key=lambda x: x[1])
sorted_by_g_out = sorted(agent_attributes["g_out"].items(), key=lambda x: x[1])
sorted_by_g_com = sorted(agent_attributes["g_com"].items(), key=lambda x: x[1])
sorted_by_l_max = sorted(agent_attributes["l_max"].items(), key=lambda x: x[1])
sorted_by_min_P = sorted(agent_attributes["P"].items(), key=lambda x: min(x[1].values()))
sorted_by_max_Q = sorted(agent_attributes["Q"].items(), key=lambda x: max(x[1].values()))
sorted_by_max_F = sorted(agent_attributes["F"].items(), key=lambda x: max(x[1].values()))

sorted_attributes = {"g_in": sorted_by_g_in, "g_out": sorted_by_g_out, "g_com": sorted_by_g_com, "l_max": sorted_by_l_max,
                     "P": sorted_by_min_P, "Q": sorted_by_max_Q, "F": sorted_by_max_F}
metrics = ["delta_d", "O_c_flow", "O_c_production", "C_f", "C_p", "N_f", "N_p", "H_f", "H_p", "M_e", "T_e"]

result_by_g_in = {"attr_value": [], "centralized": {}, "distributed": {}}
result_by_g_out = {"attr_value": [], "centralized": {}, "distributed": {}}
result_by_g_com = {"attr_value": [], "centralized": {}, "distributed": {}}
result_by_l_max = {"attr_value": [], "centralized": {}, "distributed": {}}
result_by_min_P = {"attr_value": [], "centralized": {}, "distributed": {}}
result_by_max_Q = {"attr_value": [], "centralized": {}, "distributed": {}}
result_by_max_F = {"attr_value": [], "centralized": {}, "distributed": {}}

for ag in centralized_results.keys():
    # if centralized_results[ag]["results"]["C_f"] > 0:
    #     print(ag)
    if distributed_data[ag]["results"]["C_f"] != centralized_results[ag]["results"]["C_f"]:
        print(ag)


for tuple in sorted_by_g_in:
# for tuple in agent_attributes["g_in"].items():
    result_by_g_in["attr_value"].append(tuple[1])
    for metric in metrics:
        try:
            result_by_g_in["centralized"][metric].append(centralized_results[tuple[0]]["results"][metric])
            result_by_g_in["distributed"][metric].append(distributed_data[tuple[0]]["results"][metric])
        except:
            result_by_g_in["centralized"][metric] = [centralized_results[tuple[0]]["results"][metric]]
            result_by_g_in["distributed"][metric] = [distributed_data[tuple[0]]["results"][metric]]

for tuple in sorted_by_g_out:
    result_by_g_out["attr_value"].append(tuple[1])
    for metric in metrics:
        try:
            result_by_g_out["centralized"][metric].append(centralized_results[tuple[0]]["results"][metric])
            result_by_g_out["distributed"][metric].append(distributed_data[tuple[0]]["results"][metric])
        except:
            result_by_g_out["centralized"][metric] = [centralized_results[tuple[0]]["results"][metric]]
            result_by_g_out["distributed"][metric] = [distributed_data[tuple[0]]["results"][metric]]

for tuple in sorted_by_g_com:
    result_by_g_com["attr_value"].append(tuple[1])
    for metric in metrics:
        try:
            result_by_g_com["centralized"][metric].append(centralized_results[tuple[0]]["results"][metric])
            result_by_g_com["distributed"][metric].append(distributed_data[tuple[0]]["results"][metric])
        except:
            result_by_g_com["centralized"][metric] = [centralized_results[tuple[0]]["results"][metric]]
            result_by_g_com["distributed"][metric] = [distributed_data[tuple[0]]["results"][metric]]

for tuple in sorted_by_l_max:
    result_by_l_max["attr_value"].append(tuple[1])
    for metric in metrics:
        try:
            result_by_l_max["centralized"][metric].append(centralized_results[tuple[0]]["results"][metric])
            result_by_l_max["distributed"][metric].append(distributed_data[tuple[0]]["results"][metric])
        except:
            result_by_l_max["centralized"][metric] = [centralized_results[tuple[0]]["results"][metric]]
            result_by_l_max["distributed"][metric] = [distributed_data[tuple[0]]["results"][metric]]

for tuple in sorted_by_min_P:
    result_by_min_P["attr_value"].append(tuple[1])
    for metric in metrics:
        try:
            result_by_min_P["centralized"][metric].append(centralized_results[tuple[0]]["results"][metric])
            result_by_min_P["distributed"][metric].append(distributed_data[tuple[0]]["results"][metric])
        except:
            result_by_min_P["centralized"][metric] = [centralized_results[tuple[0]]["results"][metric]]
            result_by_min_P["distributed"][metric] = [distributed_data[tuple[0]]["results"][metric]]

for tuple in sorted_by_max_Q:
    result_by_max_Q["attr_value"].append(tuple[1])
    for metric in metrics:
        try:
            result_by_max_Q["centralized"][metric].append(centralized_results[tuple[0]]["results"][metric])
            result_by_max_Q["distributed"][metric].append(distributed_data[tuple[0]]["results"][metric])
        except:
            result_by_max_Q["centralized"][metric] = [centralized_results[tuple[0]]["results"][metric]]
            result_by_max_Q["distributed"][metric] = [distributed_data[tuple[0]]["results"][metric]]

for tuple in sorted_by_max_F:
    result_by_max_F["attr_value"].append(tuple[1])
    for metric in metrics:
        try:
            result_by_max_F["centralized"][metric].append(centralized_results[tuple[0]]["results"][metric])
            result_by_max_F["distributed"][metric].append(distributed_data[tuple[0]]["results"][metric])
        except:
            result_by_max_F["centralized"][metric] = [centralized_results[tuple[0]]["results"][metric]]
            result_by_max_F["distributed"][metric] = [distributed_data[tuple[0]]["results"][metric]]


plot_order = {"C_f": [0,0], "C_p": [1,0], "O_c_flow": [0,1], "O_c_production": [1,1], "H_f": [0,2], "H_p": [1,2],
              "N_f": [0,3], "N_p": [1,3], "M_e": [0,4], "T_e": [1,4], "delta_d": [0,5]}
organized_results = {"Agent in-flow degree": result_by_g_in, "Agent out-flow degree": result_by_g_out,
                     "Agent communication degree": result_by_g_com, "Production importance": result_by_l_max,
                     "Minimum capability redundancy": result_by_min_P, "Maximum capacity proportion": result_by_max_Q,
                     "Maximum flow contribution": result_by_max_F}
metric_explain = {"C_f": "Change of total flow cost", "C_p": "Change of total production cost",
                  "N_f": "Number of changed existing flows", "N_p": "Number of changed existing production",
                  "H_f": "Number of added edges", "H_p": "Number of added agent",
                  "O_c_flow": "Cost of total over-capacity flows", "O_c_production": "Cost of total over-production flows",
                  "M_e": "Number of agent communication", "T_e": "Implementation running time", "delta_d": "Unmet demand"}
# for attr in organized_results.keys():
#     result = organized_results[attr]
#
#     fig, axs = plt.subplots(2, 6, constrained_layout=True)
#     fig.suptitle('Metrics values versus agent attribute (%s)' % attr, fontsize=16)
#     n = [i for i in range(len(centralized_results))]
#     for metric in plot_order.keys():
#         loc = plot_order[metric]
#         axs[loc[0]][loc[1]].scatter(n, result["centralized"][metric], s=70)
#         axs[loc[0]][loc[1]].scatter(n, result["distributed"][metric], s=20)
#         for i, txt in enumerate(result["attr_value"]):
#             axs[loc[0]][loc[1]].annotate(txt, (n[i], result["centralized"][metric][i]))
#         axs[loc[0]][loc[1]].set_title("%s" % metric_explain[metric])
#         axs[loc[0]][loc[1]].set_xlabel("%s" % attr)
#         axs[loc[0]][loc[1]].set_ylabel("%s" % metric)
#
#     # i = 1
#     # for metric in metrics:
#     #     plt.subplot(2, 6, i)
#     #     plt.scatter(result["attr_value"], result["centralized"][metric], s=70, color='blue')
#     #     plt.scatter(result["attr_value"], result["distributed"][metric], s=20, color='coral')
#     #     i += 1
#     #     plt.title("%s" % metric)
#     # plt.title("xxx")
#     plt.show()


agent_list = list(centralized_results.keys())
final_results = {}
attr_explain = {"g_in": "Agent in-flow degree", "g_out": "Agent out-flow degree", "g_com": "Agent communication degree",
                "l_max": "Production importance", "P": "Minimum capability redundancy", "Q": "Maximum capacity proportion",
                "F": "Maximum flow contribution"}

plot_order = {"C_f": [0,0], "C_p": [1,0], "O_c_flow": [0,1], "O_c_production": [1,1], "H_f": [0,0], "H_p": [1,0],
              "N_f": [0,1], "N_p": [1,1], "M_e": [0,0], "T_e": [1,0], "delta_d": [0,1]}
plot_split = [["C_f", "C_p", "O_c_flow", "O_c_production"], ["H_f", "H_p", "N_f", "N_p"], ["M_e", "T_e", "delta_d"]]

n = [i for i in range(len(agent_list))]
for attr in agent_attributes.keys():
    final_results[attr] = {"attr_value": [], "centralized": {}, "distributed": {}}
    for tuple in agent_attributes["g_in"].items():
        final_results[attr]["attr_value"].append(tuple[1])
        for metric in metrics:
            try:
                final_results[attr]["centralized"][metric].append(centralized_results[tuple[0]]["results"][metric])
                final_results[attr]["distributed"][metric].append(distributed_data[tuple[0]]["results"][metric])
            except:
                final_results[attr]["centralized"][metric] = [centralized_results[tuple[0]]["results"][metric]]
                final_results[attr]["distributed"][metric] = [distributed_data[tuple[0]]["results"][metric]]

    for j in range(3):
        fig, axs = plt.subplots(2, 2, constrained_layout=True)
        fig.suptitle('Metrics values versus agent attribute (%s)' % attr_explain[attr], fontsize=16)
        for metric in plot_split[j]:
            loc = plot_order[metric]
            axs[loc[0]][loc[1]].scatter(n, final_results[attr]["centralized"][metric], s=70)
            axs[loc[0]][loc[1]].scatter(n, final_results[attr]["distributed"][metric], s=20)
            for i, txt in enumerate(final_results[attr]["attr_value"]):
                axs[loc[0]][loc[1]].annotate(txt, (n[i], final_results[attr]["centralized"][metric][i]))
            axs[loc[0]][loc[1]].set_title("%s" % metric_explain[metric])
            axs[loc[0]][loc[1]].set_xlabel("%s" % attr)
            axs[loc[0]][loc[1]].set_ylabel("%s" % metric)

        plt.show()
    print("x")