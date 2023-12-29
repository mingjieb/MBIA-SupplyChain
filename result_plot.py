#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

import statistics
import matplotlib.pyplot as plt
import json
import pandas as pd
<<<<<<< Updated upstream
=======
import seaborn as sns
from matplotlib.lines import Line2D
import math
>>>>>>> Stashed changes

# Read result files

with open('Distributed/results/Distributed_results.json') as f:
    distributed_data = json.load(f)
with open('CentralizedResults/Centralized_results.json') as f:
    centralized_results = json.load(f)
with open('CentralizedResults/runtime.json') as f:
    centralized_runtime = json.load(f)
<<<<<<< Updated upstream
with open('CentralizedResults/communication.json') as f:
=======
with open('CentralizedResults/Case4-Penalty/communication.json') as \
        f:
>>>>>>> Stashed changes
    centralized_communication = json.load(f)
tier_info = pd.read_excel('Distributed/initialization/TASE_Setup.xlsx', sheet_name='Agent').set_index(['AgentType'])

# Filling the communication and runtime to centralized_results
for key in centralized_results:
    centralized_results[key]["results"]["M_e"] = centralized_communication[key]
    centralized_results[key]["results"]["T_e"] = centralized_runtime[key]

# Split tier level
tier_list_info = list(tier_info.loc["Tier3", "AgentName"].values) + list(
    tier_info.loc["Tier2", "AgentName"].values) + list(
    tier_info.loc["Tier1", "AgentName"].values)
tier_list = []
for ag in tier_list_info:
    if ag in list(distributed_data.keys()) and ag not in tier_list:
        tier_list.append(ag)
mfg_list = tier_list + ['cockpit_assy_1', 'cockpit_assy_2', 'cockpit_assy_3']
tier1, tier2, tier3 = [], [], []
[tier1.append(x) for x in tier_list if x in list(tier_info.loc["Tier1", "AgentName"].values)]
[tier2.append(x) for x in tier_list if x in list(tier_info.loc["Tier2", "AgentName"].values)]
[tier3.append(x) for x in tier_list if x in list(tier_info.loc["Tier3", "AgentName"].values)]
tier_numbers = [len(tier3) + 0.5, len(tier3) + len(tier2) + 0.5, len(tier1) + len(tier2) + len(tier3) + 0.5]

# Get the indices of scenarios where the demands are satisfied and not satisfied
# for both centralized and distributed methods
n_dis_met, n_dis_unmet, n_cen_met, n_cen_unmet = [], [], [], []
for i in range(len(mfg_list)):
    if distributed_data[mfg_list[i]]["results"]["delta_d"] - 0 < 0.1:
        n_dis_met.append(i)
    if distributed_data[mfg_list[i]]["results"]["delta_d"] - 0 > 0.1:
        n_dis_unmet.append(i)
    if centralized_results[mfg_list[i]]["results"]["delta_d"] - 0 < 0.1:
        n_cen_met.append(i)
    if centralized_results[mfg_list[i]]["results"]["delta_d"] - 0 > 0.1:
        n_cen_unmet.append(i)


# Reformulate the data structures for agent attributes and results (may not be used)
def reformulate_results(distributed_data, centralized_results):
<<<<<<< Updated upstream
    agent_attributes = {"g_in": {}, "g_out": {}, "g_com": {}, "P": {}, "Q": {}, "F": {}, "l": {}, "n": {}}
=======
    agent_attributes = {"g_in": {}, "g_out": {}, "g_com": {}, "P": {}, "Q": {}, "F": {}, "kf": {}, "depth": {}, "v": {}, "n": {}, "l": {}}
>>>>>>> Stashed changes

    attr_explain = {"g_in": "Agent in-flow degree", "g_out": "Agent out-flow degree",
                    "g_com": "Agent communication degree",
                    "P": "Minimum capability redundancy", "Q": "Maximum capacity utility",
                    "F": "Maximum flow contribution",
                    "l": "# of needed production steps", "n": "# of contributed final products"}
    metric_explain = {"C_f": "Change of total flow cost", "C_p": "Change of total production cost",
                      "N_f": "Number of changed existing flows", "N_p": "Number of changed existing production",
                      "H_f": "Number of added edges", "H_p": "Number of added agent",
                      "O_c_flow": "Cost of total over-capacity flows",
                      "O_c_production": "Cost of total over-production flows",
                      "M_e": "Number of agent communication", "T_e": "Implementation running time",
                      "delta_d": "Unmet demand"}
    metrics = ["delta_d", "O_c_flow", "O_c_production", "C_f", "C_p", "N_f", "N_p", "H_f", "H_p", "M_e", "T_e"]
    agent_list = list(distributed_data.keys())
    final_results = {}
    for key in agent_attributes.keys():
        for agent in agent_list:
            if key not in ["P", "Q"]:
                agent_attributes[key][agent] = distributed_data[agent]["attributes"][key]
<<<<<<< Updated upstream
            elif key == "P":
                agent_attributes[key][agent] = min(x[1] for x in distributed_data[agent]["attributes"][key].items())
=======
            # elif key == "F":
            #     # agent_attributes[key][agent] = min(x[1] for x in distributed_data[agent]["attributes"][key].items())
            #     agent_attributes[key][agent] = statistics.mean([x[1] for x in distributed_data[agent]["attributes"][key].items()])
>>>>>>> Stashed changes
            else:
                agent_attributes[key][agent] = max(x[1] for x in distributed_data[agent]["attributes"][key].items())
    for attr in agent_attributes.keys():
        final_results[attr] = {"attr_value": [], "centralized": {}, "distributed": {}, "agent": None}
        for a in agent_attributes[attr].items():
            final_results[attr]["agent"] = a[0]
            final_results[attr]["attr_value"].append(a[1])
            for metric in metrics:
                try:
                    final_results[attr]["centralized"][metric].append(centralized_results[a[0]]["results"][metric])
                    final_results[attr]["distributed"][metric].append(distributed_data[a[0]]["results"][metric])
                except:
                    final_results[attr]["centralized"][metric] = [centralized_results[a[0]]["results"][metric]]
                    final_results[attr]["distributed"][metric] = [distributed_data[a[0]]["results"][metric]]
    return agent_attributes


# Plot all the attributes of each agents
def plot_attributes(mfg_list, agent_attributes):
    ax1 = plt.subplot(311)
    ax2 = plt.subplot(312)
    ax3 = plt.subplot(313)
    x = [i + 1 for i in range(len(mfg_list))]

    # Plot in-flow, out-flow, and communication degree
    g_in = [agent_attributes["g_in"][mfg_list[i]] for i in range(len(mfg_list))]
    g_out = [agent_attributes["g_out"][mfg_list[i]] for i in range(len(mfg_list))]
    g_com = [agent_attributes["g_com"][mfg_list[i]] for i in range(len(mfg_list))]
    # ax1.plot(x, g_in, marker='.', color='#6699CC', label=r'$g_{in}$', linewidth=2)
    # ax1.plot(x, g_out, marker='.', color='#EEB479', label=r'$g_{out}$', linewidth=2)
    # ax1.plot(x, g_com, marker='.', color='#CC6677', label=r'$g_{com}$', linewidth=2)
    ax1.scatter(x, g_in, marker='+', color='#6699CC', label=r'$g_{in}$')
    ax1.scatter(x, g_out, marker='x', color='#EEB479', label=r'$g_{out}$')
    ax1.scatter(x, g_com, marker='^', color='#CC6677', label=r'$g_{com}$')
    ax1.set_ylabel(r'$g_{in}$' ', ' r'$g_{out}$' ', and ' r'$g_{com}$', fontsize=12)
    ax1.set_title("In-degree, out-degree, and communication degree", fontsize=12)

    # Plot capability redundancy and capacity sufficiency
    p = [agent_attributes["P"][mfg_list[i]] for i in range(len(mfg_list))]
    q = [agent_attributes["Q"][mfg_list[i]] for i in range(len(mfg_list))]
    # f = [agent_attributes["F"][mfg_list[i]] for i in range(len(mfg_list))]
    # ax2.plot(x, p, marker='.', color='#6699CC', label=r'$P_i(m)$', linewidth=2)
    # ax2.plot(x, q, marker='.', color='#EEB479', label=r'$Q_i(m)$', linewidth=2)
    ax2.scatter(x, p, marker='+', color='#6699CC', label=r'$P_i(m)$')
    ax2.scatter(x, q, marker='x', color='#EEB479', label=r'$Q_i(m)$')
    # ax2.plot(x, f, marker='.', color='#CC6677', label=r'$F_i(m)$', linewidth=2)
    ax2.set_ylabel(r'$P_i(m)$' ' and ' r'$Q_i(m)$', fontsize=12)
    ax2.set_title("Capability redundancy and capacity sufficiency", fontsize=12)

    # Plot production need and contributions to final products
    l = [agent_attributes["l"][mfg_list[i]] for i in range(len(mfg_list))]
    n = [agent_attributes["n"][mfg_list[i]] for i in range(len(mfg_list))]
    # ax3.plot(x, l, marker='.', color='#6699CC', label=r'$l_i(k)$', linewidth=2)
    # ax3.plot(x, n, marker='.', color='#EEB479', label=r'$n_i(k)$', linewidth=2)
    ax3.scatter(x, l, marker='+', color='#6699CC', label=r'$l_i(k)$')
    ax3.scatter(x, n, marker='x', color='#EEB479', label=r'$n_i(k)$')
    ax3.set_xlabel("Disruption scenarios", fontsize=12)
    ax3.set_ylabel(r'$l_i(k)$' ' and ' r'$n_i(k)$', fontsize=12)
    ax3.set_title("Production need and contribution to final products", fontsize=12)

    ax1.legend()
    ax2.legend()
    ax3.legend()
    plt.subplots_adjust(hspace=0.4)
    plt.show()


# Plot the demand satisfaction
def demand_satisfaction_plots(distributed_data, centralized_results, mfg_list, n_dis_unmet, n_cen_unmet):

    # # Check the attributes of the unmet demand scenarios
    # for i in n_dis_unmet:
    #     print(i, mfg_list[i], distributed_data[mfg_list[i]]["results"]["delta_d"], agent_attributes["P"][mfg_list[i]],
    #           agent_attributes["Q"][mfg_list[i]], agent_attributes["n"][mfg_list[i]])
    # for i in n_cen_unmet:
    #     print(i, mfg_list[i], centralized_results[mfg_list[i]]["results"]["delta_d"], agent_attributes["P"][mfg_list[i]],
    #           agent_attributes["Q"][mfg_list[i]], agent_attributes["n"][mfg_list[i]])

    # Bar plot of the unmet demand
    barWidth = 0.25
    fig = plt.subplots()
    dis_delta_d = [distributed_data[mfg_list[i]]["results"]["delta_d"] for i in n_dis_unmet]
    cen_delta_d = [centralized_results[mfg_list[i]]["results"]["delta_d"] for i in n_cen_unmet]

    br1 = [r for r in range(len(dis_delta_d))]
    br2 = [x + barWidth for x in br1]

    plt.axvspan(-0.3, 1.65, facecolor='0.6', alpha=0.5)
    plt.bar(br1, dis_delta_d, color='#9DC3E7', width=barWidth, edgecolor='grey', label='Distributed')
    plt.bar(br2, cen_delta_d, color='#FEB2B4', width=barWidth, edgecolor='grey', label='Centralized')
    plt.text(-0.1, 200, r'$P_i(m)=1$', fontsize=12)
    plt.text(6, 200, r'$P_i(m)=0$', fontsize=12)

    plt.xlabel('Disruption scenarios ' r'($\Delta^d>0$)', fontsize=12)
    plt.ylabel('Unmet demand ' r'$\Delta^d$', fontsize=12)
    idx = [i + 1 for i in n_dis_unmet]
    plt.xticks([r + barWidth / 2 for r in range(len(dis_delta_d))],
               ['%s' % i for i in idx])
    plt.title("Unmet demand using centralized and distributed methods", fontsize=12)
    plt.legend()
    plt.show()


# Plot the changes to costs and the network
def network_change_plots(distributed_data, centralized_results, mfg_list, n_dis_met, n_cen_met):
    # Scatter plot of changes to cost
    ax1 = plt.subplot(311)
    ax2 = plt.subplot(312)
    ax3 = plt.subplot(313)
    x = [i + 1 for i in n_dis_met]

    # Changes to the flow cost
    y_fd = [distributed_data[mfg_list[i]]["results"]["C_f"] for i in n_dis_met]
    y_fc = [centralized_results[mfg_list[i]]["results"]["C_f"] for i in n_dis_met]
    # ax1.plot(x, y_fd, marker='.', color='#496C88', label=r'$C_f$' ', distributed', linewidth=2)
    # ax1.plot(x, y_fc, marker='.', color='#E88482', label=r'$C_f$' ', centralized', linewidth=2)
    ax1.scatter(x, y_fd, marker='+', color='#496C88', label=r'$C_f$' ', distributed')
    ax1.scatter(x, y_fc, marker='x', color='#E88482', label=r'$C_f$' ', centralized')
    ax1.axhline(y=0.0, color='grey', linestyle='--')
    ax1.set_ylabel(r'$C_f$', fontsize=12)
    ax1.set_title("Changes to cost of flows", fontsize=12)

    # Changes to the production cost
    y_pd = [distributed_data[mfg_list[i]]["results"]["C_p"] for i in n_dis_met]
    y_pc = [centralized_results[mfg_list[i]]["results"]["C_p"] for i in n_dis_met]
    # ax2.plot(x, y_pd, marker='.', color='#496C88', label=r'$C_p$' ', distributed', linewidth=2)
    # ax2.plot(x, y_pc, marker='.', color='#E88482', label=r'$C_p$' ', centralized', linewidth=2)
    ax2.scatter(x, y_pd, marker='+', color='#496C88', label=r'$C_p$' ', distributed')
    ax2.scatter(x, y_pc, marker='x', color='#E88482', label=r'$C_p$' ', centralized')
    ax2.axhline(y=0.0, color='grey', linestyle='--')
    ax2.set_ylabel(r'$C_p$', fontsize=12)
    ax2.set_title("Changes to cost of productions", fontsize=12)

    # Changes to the total cost
    y_totald = [distributed_data[mfg_list[i]]["results"]["C_f"] + distributed_data[mfg_list[i]]["results"]["C_p"]
                for i in n_dis_met]
    y_totalc = [centralized_results[mfg_list[i]]["results"]["C_f"] + centralized_results[mfg_list[i]]["results"]["C_p"]
                for i in n_dis_met]
    # ax3.plot(x, y_totald, marker='.', color='#496C88', label=r'$C_{total}$' ', distributed', linewidth=2)
    # ax3.plot(x, y_totalc, marker='.', color='#E88482', label=r'$C_{total}$' ', centralized', linewidth=2)
    ax3.scatter(x, y_totald, marker='+', color='#496C88', label='Distributed')
    ax3.scatter(x, y_totalc, marker='x', color='#E88482', label='Centralized')
    ax3.axhline(y=0.0, color='grey', linestyle='--')
    ax3.set_xlabel("Disruption scenarios " r'($\Delta^d=0$)', fontsize=12)
    ax3.set_ylabel(r'$C_{total}$', fontsize=12)
    ax3.set_title("Changes to total cost of flows and productions", fontsize=12)

    # # Get the mean and standard deviation
    # fd_mean, fd_std = statistics.mean(y_fd), statistics.stdev(y_fd)
    # print(fd_mean, fd_std)
    # pd_mean, pd_std = statistics.mean(y_pd), statistics.stdev(y_pd)
    # print(pd_mean, pd_std)
    # fc_mean, fc_std = statistics.mean(y_fc), statistics.stdev(y_fc)
    # print(fc_mean, fc_std)
    # pc_mean, pc_std = statistics.mean(y_pc), statistics.stdev(y_pc)
    # print(pc_mean, pc_std)

    # ax1.legend(loc='upper left')
    # ax2.legend()
    ax3.legend()
    plt.subplots_adjust(hspace=0.4)
    plt.show()

    # Scatter plot of changes to network
    ax1 = plt.subplot(221)
    ax2 = plt.subplot(222)
    ax3 = plt.subplot(223)
    ax4 = plt.subplot(224)

    # Added transportation edges
    y_fd = [distributed_data[mfg_list[i]]["results"]["H_f"] for i in n_dis_met]
    y_fc = [centralized_results[mfg_list[i]]["results"]["H_f"] for i in n_dis_met]
    ax1.scatter(x, y_fd, marker='+', color='#496C88', label=r'$H_f$' ', distributed')
    ax1.scatter(x, y_fc, marker='x', color='#CC6677', label=r'$H_f$' ', centralized')
    ax1.set_xlabel("Disruption scenarios " r'($\Delta^d=0$)', fontsize=12)
    ax1.set_ylabel(r'$H_f$', fontsize=12)
    ax1.set_title("Number of added transportation edges", fontsize=12)

    # Added agent for production
    y_pd = [distributed_data[mfg_list[i]]["results"]["H_p"] for i in n_dis_met]
    y_pc = [centralized_results[mfg_list[i]]["results"]["H_p"] for i in n_dis_met]
    ax2.scatter(x, y_pd, marker='+', color='#496C88', label='Distributed')
    ax2.scatter(x, y_pc, marker='x', color='#CC6677', label='Centralized')
    ax2.set_xlabel("Disruption scenarios " r'($\Delta^d=0$)', fontsize=12)
    ax2.set_ylabel(r'$H_p$', fontsize=12)
    ax2.set_title("Number of added agents", fontsize=12)

    # # Get the mean and standard deviation
    # fd_mean, fd_std = statistics.mean(y_fd), statistics.stdev(y_fd)
    # print(fd_mean, fd_std)
    # pd_mean, pd_std = statistics.mean(y_pd), statistics.stdev(y_pd)
    # print(pd_mean, pd_std)
    # fc_mean, fc_std = statistics.mean(y_fc), statistics.stdev(y_fc)
    # print(fc_mean, fc_std)
    # pc_mean, pc_std = statistics.mean(y_pc), statistics.stdev(y_pc)
    # print(pc_mean, pc_std)

    # Existing edges that change flows
    y_fd = [distributed_data[mfg_list[i]]["results"]["N_f"] for i in n_dis_met]
    y_fc = [centralized_results[mfg_list[i]]["results"]["N_f"] for i in n_dis_met]
    ax3.scatter(x, y_fd, marker='+', color='#496C88', label=r'$N_f$' ', distributed')
    ax3.scatter(x, y_fc, marker='x', color='#CC6677', label=r'$N_f$' ', centralized')
    ax3.set_xlabel("Disruption scenarios " r'($\Delta^d=0$)', fontsize=12)
    ax3.set_ylabel(r'$N_f$', fontsize=12)
    ax3.set_title("Number of transportation \n that changed flows", fontsize=12)

    # Existing agents that chagne production
    y_pd = [distributed_data[mfg_list[i]]["results"]["N_p"] for i in n_dis_met]
    y_pc = [centralized_results[mfg_list[i]]["results"]["N_p"] for i in n_dis_met]
    ax4.scatter(x, y_pd, marker='+', color='#496C88', label=r'$N_p$' ', distributed')
    ax4.scatter(x, y_pc, marker='x', color='#CC6677', label=r'$N_p$' ', centralized')
    ax4.set_xlabel("Disruption scenarios " r'($\Delta^d=0$)', fontsize=12)
    ax4.set_ylabel(r'$N_p$', fontsize=12)
    ax4.set_title("Number of agents \n that changed productions", fontsize=12)

    # # Get the mean and standard deviation
    # fd_mean, fd_std = statistics.mean(y_fd), statistics.stdev(y_fd)
    # print(fd_mean, fd_std)
    # pd_mean, pd_std = statistics.mean(y_pd), statistics.stdev(y_pd)
    # print(pd_mean, pd_std)
    # fc_mean, fc_std = statistics.mean(y_fc), statistics.stdev(y_fc)
    # print(fc_mean, fc_std)
    # pc_mean, pc_std = statistics.mean(y_pc), statistics.stdev(y_pc)
    # print(pc_mean, pc_std)

    # ax1.legend(loc='upper left')
    ax2.legend(loc='upper left')
    # ax3.legend(loc='upper left')
    # ax4.legend(loc='upper left')
    plt.subplots_adjust(hspace=0.6, wspace=0.4)
    plt.show()

    # # Line plot of costs of over-capacity in production and flow
    # ax1 = plt.subplot(211)
    # ax2 = plt.subplot(212)
    # # ax3 = plt.subplot(313)
    # x = [i + 1 for i in n_dis_met]
    #
    # # Cost of over-capacity flow
    # y_fd = [distributed_data[mfg_list[i]]["results"]["O_c_flow"] for i in n_dis_met]
    # y_fc = [centralized_results[mfg_list[i]]["results"]["O_c_flow"] for i in n_dis_met]
    # ax1.plot(x, y_fd, marker='.', color='#496C88', label=r'$O_f$' ', distributed', linewidth=2)
    # ax1.plot(x, y_fc, marker='.', color='#E88482', label=r'$O_f$' ', centralized', linewidth=2)
    # # ax1.set_xlabel("Disruption scenarios", fontsize=12)
    # ax1.set_ylabel(r'$O_f$', fontsize=12)
    # ax1.set_title("Cost of over-capacity flows", fontsize=12)
    # # print(y_fd[index[0]], y_fd[index[1]], y_fd[index[2]])
    # # print(y_fc[index[0]], y_fc[index[1]], y_fc[index[2]])
    #
    # # Cost of over-capacity production
    # y_pd = [distributed_data[mfg_list[i]]["results"]["O_c_production"] for i in n_dis_met]
    # y_pc = [centralized_results[mfg_list[i]]["results"]["O_c_production"] for i in n_dis_met]
    # ax2.plot(x, y_pd, marker='.', color='#496C88', label=r'$O_p$' ', distributed', linewidth=2)
    # ax2.plot(x, y_pc, marker='.', color='#E88482', label=r'$O_p$' ', centralized', linewidth=2)
    # ax2.set_xlabel("Disruption scenarios " r'($\Delta^d=0$)', fontsize=12)
    # ax2.set_ylabel(r'$O_p$', fontsize=12)
    # ax2.set_title("Cost of over-capacity productions", fontsize=12)
    #
    # # print(y_fd[45], y_fd[48], y_fd[49])
    # # print(y_fc[45], y_fc[48], y_fc[49])

    # y_totald = [distributed_data[mfg_list[i]]["results"]["O_c_flow"] + distributed_data[mfg_list[i]]["results"]["O_c_production"]
    #             for i in n_dis_met]
    # y_totalc = [centralized_results[mfg_list[i]]["results"]["O_c_flow"] + centralized_results[mfg_list[i]]["results"]["O_c_production"]
    #             for i in n_dis_met]
    # ax3.plot(x, y_totald, marker='.', color='#1f77b4', label='O_total distributed')
    # ax3.plot(x, y_totalc, marker='.', color='#ff7f0e', label='O_total centralized')

    # ax1.legend()
    # ax2.legend()
    # # ax3.legend()
    # plt.subplots_adjust(hspace=0.4)
    # plt.show()

    # # Line plot of changes to costs and network
    # ax1 = plt.subplot(411)
    # ax2 = plt.subplot(412)
    # ax3 = plt.subplot(413)
    # ax4 = plt.subplot(414)
    # x = [i + 1 for i in n_dis_met]
    # y_fd = [distributed_data[mfg_list[i]]["results"]["H_f"] for i in n_dis_met]
    # y_fc = [centralized_results[mfg_list[i]]["results"]["H_f"] for i in n_dis_met]
    # ax1.plot(x, y_fd, marker='.', color='#496C88', label=r'$H_f$' ', distributed', linewidth=2)
    # ax1.plot(x, y_fc, marker='.', color='#E88482', label=r'$H_f$' ', centralized', linewidth=2)
    # ax1.set_ylabel(r'$H_f$', fontsize=12)
    # ax1.set_title("Number of added transportation edges", fontsize=12)
    # #
    # y_pd = [distributed_data[mfg_list[i]]["results"]["H_p"] for i in n_dis_met]
    # y_pc = [centralized_results[mfg_list[i]]["results"]["H_p"] for i in n_dis_met]
    # ax2.plot(x, y_pd, marker='.', color='#496C88', label=r'$H_p$' ', distributed', linewidth=2)
    # ax2.plot(x, y_pc, marker='.', color='#E88482', label=r'$H_p$' ', centralized', linewidth=2)
    # ax2.set_ylabel(r'$H_p$', fontsize=12)
    # ax2.set_title("Number of added agents", fontsize=12)
    #
    # y_fd = [distributed_data[mfg_list[i]]["results"]["N_f"] for i in n_dis_met]
    # y_fc = [centralized_results[mfg_list[i]]["results"]["N_f"] for i in n_dis_met]
    # ax3.plot(x, y_fd, marker='.', color='#496C88', label=r'$N_f$' ', distributed', linewidth=2)
    # ax3.plot(x, y_fc, marker='.', color='#E88482', label=r'$N_f$' ', centralized', linewidth=2)
    # ax3.set_ylabel(r'$N_f$', fontsize=12)
    # ax3.set_title("Number of transportation that changed flows", fontsize=12)
    # #
    # y_pd = [distributed_data[mfg_list[i]]["results"]["N_p"] for i in n_dis_met]
    # y_pc = [centralized_results[mfg_list[i]]["results"]["N_p"] for i in n_dis_met]
    # ax4.plot(x, y_pd, marker='.', color='#496C88', label=r'$N_p$' ', distributed', linewidth=2)
    # ax4.plot(x, y_pc, marker='.', color='#E88482', label=r'$N_p$' ', centralized', linewidth=2)
    # ax4.set_xlabel("Disruption scenarios " r'($\Delta^d=0$)', fontsize=12)
    # ax4.set_ylabel(r'$N_p$', fontsize=12)
    # ax4.set_title("Number of agents that changed productions", fontsize=12)
    #
    # ax1.legend(loc='upper left')
    # ax2.legend(loc='upper left')
    # ax3.legend(loc='upper left')
    # ax4.legend(loc='upper left')
    # plt.subplots_adjust(hspace=0.4)
    # plt.show()


# Plot the algorithm performance
def algo_perf_plots(distributed_data, centralized_results, mfg_list, n_dis_met, n_dis_unmet, n_cen_met, n_cen_unmet):
    # Split results based on approaches and whether they satisfy the demand
    data_1 = [distributed_data[mfg_list[i]]["results"]["T_e"] for i in n_dis_met]
    data_2 = [centralized_results[mfg_list[i]]["results"]["T_e"] for i in n_cen_met]
    data_3 = [distributed_data[mfg_list[i]]["results"]["M_e"] for i in n_dis_met]
    data_4 = [centralized_results[mfg_list[i]]["results"]["M_e"] for i in n_cen_met]
    data_5 = [distributed_data[mfg_list[i]]["results"]["T_e"] for i in n_dis_unmet]
    data_6 = [centralized_results[mfg_list[i]]["results"]["T_e"] for i in n_cen_unmet]
    data_7 = [distributed_data[mfg_list[i]]["results"]["M_e"] for i in n_dis_unmet]
    data_8 = [centralized_results[mfg_list[i]]["results"]["M_e"] for i in n_cen_unmet]

    # # Compute the mean and standard deviation
    # cen_m_e_mean = statistics.mean(data_4+data_8)
    # cen_m_e_std = statistics.stdev(data_4+data_8)
    # cen_t_e_mean = statistics.mean(data_2+data_6)
    # cen_t_e_std = statistics.stdev(data_2+data_6)
    # print(cen_m_e_mean, cen_m_e_std, cen_t_e_mean, cen_t_e_std)
    # dis_m_e_mean = statistics.mean(data_3+data_7)
    # dis_m_e_std = statistics.stdev(data_3+data_7)
    # dis_t_e_mean = statistics.mean(data_1+data_5)
    # dis_t_e_std = statistics.stdev(data_1+data_5)
    # print(dis_m_e_mean, dis_m_e_std, dis_t_e_mean, dis_t_e_std)

    # Scatter plot of M_e and T_e
    x1 = [i + 1 for i in n_dis_met]
    x2 = [i + 1 for i in n_dis_unmet]

    ax1 = plt.subplot(211)
    ax2 = plt.subplot(212)

    ax1.scatter(x1, data_3, marker='+', color='#888888', label=r'$\Delta^d=0$, distributed')
    ax1.scatter(x2, data_7, marker='+', color='#469990', label=r'$\Delta^d>0$, distributed')
    ax1.scatter(x1, data_4, marker='x', color='#888888', label=r'$\Delta^d=0$, centralized')
    ax1.scatter(x2, data_8, marker='x', color='#469990', label=r'$\Delta^d>0$, centralized')

    # ax1.set_xlabel("Disruption scenarios", fontsize=12)
    ax1.set_ylabel(r'$M_e$', fontsize=12)
    ax1.set_title('Number of agent communication using \n centralized and distributed approaches', fontsize=12)

    ax2.scatter(x1, data_1, marker='+', color='#888888', label=r'$\Delta^d=0$, distributed')
    ax2.scatter(x2, data_5, marker='+', color='#469990', label=r'$\Delta^d>0$, distributed')
    ax2.scatter(x1, data_2, marker='x', color='#888888', label=r'$\Delta^d=0$, centralized')
    ax2.scatter(x2, data_6, marker='x', color='#469990', label=r'$\Delta^d>0$, centralized')

    ax2.set_xlabel("Disruption scenarios", fontsize=12)
    ax2.set_ylabel(r'$T_e$', fontsize=12)
    ax2.set_title('Running time using centralized and distributed approaches', fontsize=12)

    # ax1.legend()
    ax2.legend(ncol=2)
    plt.subplots_adjust(hspace=0.4)
    plt.show()

    # # Line plot of M_e and T_e
    # ax1 = plt.subplot(221)
    # ax2 = plt.subplot(222)
    # ax3 = plt.subplot(223)
    # ax4 = plt.subplot(224)
    #
    # ax1.plot(x1, data_3, marker='.', color='#888888', label=r'$\Delta^d=0$', linewidth=2)
    # ax1.plot(x2, data_7, marker='.', color='#469990', label=r'$\Delta^d>0$', linewidth=2)
    # ax1.set_xlabel("Disruption scenarios", fontsize=12)
    # ax1.set_ylabel(r'$M_e$', fontsize=12)
    # ax1.set_title('Number of agent communication, \n distributed', fontsize=12)
    # #
    # ax2.plot(x1, data_4, marker='.', color='#888888', label=r'$\Delta^d=0$', linewidth=2)
    # ax2.plot(x2, data_8, marker='.', color='#469990', label=r'$\Delta^d>0$', linewidth=2)
    # ax2.set_xlabel("Disruption scenarios", fontsize=12)
    # ax2.set_ylabel(r'$M_e$', fontsize=12)
    # ax2.set_title('Number of agent communication, \n centralized', fontsize=12)
    #
    # ax3.plot(x1, data_1, marker='.', color='#888888', label=r'$\Delta^d=0$', linewidth=2)
    # ax3.plot(x2, data_5, marker='.', color='#469990', label=r'$\Delta^d>0$', linewidth=2)
    # ax3.set_xlabel("Disruption scenarios", fontsize=12)
    # ax3.set_ylabel(r'$T_e$', fontsize=12)
    # ax3.set_title('Running time, distributed', fontsize=12)
    # #
    # ax4.plot(x1, data_2, marker='.', color='#888888', label=r'$\Delta^d=0$', linewidth=2)
    # ax4.plot(x2, data_6, marker='.', color='#469990', label=r'$\Delta^d>0$', linewidth=2)
    # ax4.set_xlabel("Disruption scenarios", fontsize=12)
    # ax4.set_ylabel(r'$T_e$', fontsize=12)
    # ax4.set_title('Running time, centralized', fontsize=12)
    #
    # ax1.legend()
    # ax2.legend()
    # ax3.legend()
    # ax4.legend()
    # plt.subplots_adjust(hspace=0.4)
    # plt.show()

    # # Box plot of M_e and T_e
    # ax1 = plt.subplot(221)
    # ax2 = plt.subplot(222)
    # ax3 = plt.subplot(223)
    # ax4 = plt.subplot(224)
    # labels = ['Scenarios\n ' r'$\Delta^d=0$', 'Scenarios\n ' r'$\Delta^d>0$']
    # bp1 = ax1.boxplot([data_1, data_5], patch_artist=True, labels=labels)
    # ax1.set_title('Running time, distributed', fontsize=12)
    # ax1.set_xticklabels(labels=labels, Fontsize=12)
    # ax1.set_ylabel('Running time ' r'$T_e$', fontsize=12)
    #
    # bp2 = ax2.boxplot([data_2, data_6], patch_artist=True, labels=labels)
    # ax2.set_title('Running time, centralized', fontsize=12)
    # ax2.set_xticklabels(labels=labels, Fontsize=12)
    # ax2.set_ylabel('Running time ' r'$T_e$', fontsize=12)
    #
    # bp3 = ax3.boxplot([data_3, data_7], patch_artist=True, labels=labels)
    # ax3.set_title('Number of agent communication,\n distributed', fontsize=12)
    # ax3.set_xticklabels(labels=labels, Fontsize=12)
    # ax3.set_ylabel('Number of agent communication ' r'$M_e$', fontsize=12)
    #
    # bp4 = ax4.boxplot([data_4, data_8], patch_artist=True, labels=labels)
    # ax4.set_title('Number of agent communication,\n centralized', fontsize=12)
    # ax4.set_xticklabels(labels=labels, Fontsize=12)
    # ax4.set_ylabel('Number of agent communication ' r'$M_e$', fontsize=12)
    # colors = ['pink', 'lightblue']
    # for bplot in (bp1, bp2, bp3, bp4):
    #     for patch, color in zip(bplot['boxes'], colors):
    #         patch.set_facecolor(color)
    #
    # plt.subplots_adjust(wspace=0.4, hspace=0.4)
    # plt.show()


# (Did not use it) Plot all the data
def plot_all_information(agent_list, attr_explain, metric_explain):
    # agent_list = list(centralized_results.keys())
    final_results = {}

    plot_order = {"C_f": [0, 0], "C_p": [1, 0], "O_c_flow": [0, 1], "O_c_production": [1, 1], "H_f": [0, 0],
                  "H_p": [1, 0],
                  "N_f": [0, 1], "N_p": [1, 1], "M_e": [0, 0], "T_e": [1, 0], "delta_d": [0, 1]}
    plot_split = [["C_f", "C_p", "O_c_flow", "O_c_production"], ["H_f", "H_p", "N_f", "N_p"], ["M_e", "T_e", "delta_d"]]

    n = [i for i in range(len(agent_list))]
    for attr in agent_attributes.keys():
        final_results[attr] = {"attr_value": [], "centralized": {}, "distributed": {}}
        for j in range(3):
            fig, axs = plt.subplots(2, 2, constrained_layout=True)
            fig.suptitle('Metrics values versus agent attribute (%s)' % attr_explain[attr], fontsize=16)
            for metric in plot_split[j]:
                loc = plot_order[metric]
                axs[loc[0]][loc[1]].scatter(n, final_results[attr]["centralized"][metric], s=70)
                axs[loc[0]][loc[1]].scatter(n, final_results[attr]["distributed"][metric], s=20)
                # for i, txt in enumerate(final_results[attr]["attr_value"]):
                # axs[loc[0]][loc[1]].annotate(txt, (n[i], final_results[attr]["centralized"][metric][i]))
                axs[loc[0]][loc[1]].set_title("%s" % metric_explain[metric])
                axs[loc[0]][loc[1]].set_xlabel("%s" % attr)
                axs[loc[0]][loc[1]].set_ylabel("%s" % metric)

            plt.show()
        print("x")


# (Did not use it) Sort the agent based on each attributes
def sort_by_attribute():
    sorted_by_g_in = sorted(agent_attributes["g_in"].items(), key=lambda x: x[1])
    sorted_by_g_out = sorted(agent_attributes["g_out"].items(), key=lambda x: x[1])
    sorted_by_g_com = sorted(agent_attributes["g_com"].items(), key=lambda x: x[1])
    sorted_by_l_max = sorted(agent_attributes["l_max"].items(), key=lambda x: x[1])
    sorted_by_min_P = sorted(agent_attributes["P"].items(), key=lambda x: x[1])
    sorted_by_max_Q = sorted(agent_attributes["Q"].items(), key=lambda x: x[1])
    sorted_by_max_F = sorted(agent_attributes["F"].items(), key=lambda x: x[1])

    sorted_attributes = {"g_in": sorted_by_g_in, "g_out": sorted_by_g_out, "g_com": sorted_by_g_com,
                         "l_max": sorted_by_l_max,
                         "P": sorted_by_min_P, "Q": sorted_by_max_Q, "F": sorted_by_max_F}
    metrics = ["delta_d", "O_c_flow", "O_c_production", "C_f", "C_p", "N_f", "N_p", "H_f", "H_p", "M_e", "T_e"]

    result_by_g_in = {"attr_value": [], "centralized": {}, "distributed": {}}
    result_by_g_out = {"attr_value": [], "centralized": {}, "distributed": {}}
    result_by_g_com = {"attr_value": [], "centralized": {}, "distributed": {}}
    result_by_l_max = {"attr_value": [], "centralized": {}, "distributed": {}}
    result_by_min_P = {"attr_value": [], "centralized": {}, "distributed": {}}
    result_by_max_Q = {"attr_value": [], "centralized": {}, "distributed": {}}
    result_by_max_F = {"attr_value": [], "centralized": {}, "distributed": {}}

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

    organized_results = {"Agent_in-flow_degree": result_by_g_in, "Agent_out-flow_degree": result_by_g_out,
                         "Agent_communication_degree": result_by_g_com, "Production_importance": result_by_l_max,
                         "Minimum_capability_redundancy": result_by_min_P,
                         "Maximum_capacity_proportion": result_by_max_Q,
                         "Maximum_flow_contribution": result_by_max_F}
    return organized_results


def get_category(agent_attributes):
    connectivity = [agent_attributes["g_in"][mfg_list[i]] + agent_attributes["g_out"][mfg_list[i]] for i in
                    range(len(mfg_list))]
    min_con = min([agent_attributes["g_in"][mfg_list[i]] + agent_attributes["g_out"][mfg_list[i]] for i in
                    range(len(n_cen_met))])
    max_con = max([agent_attributes["g_in"][mfg_list[i]] + agent_attributes["g_out"][mfg_list[i]] for i in
                    range(len(n_cen_met))])

<<<<<<< Updated upstream
plot_attributes(mfg_list, agent_attributes)

demand_satisfaction_plots(distributed_data, centralized_results, mfg_list, n_dis_unmet, n_cen_unmet)

network_change_plots(distributed_data, centralized_results, mfg_list, n_dis_met, n_cen_met)

algo_perf_plots(distributed_data, centralized_results, mfg_list, n_dis_met, n_dis_unmet, n_cen_met, n_cen_unmet)
=======
    low_con_idx = [i for i in range(len(mfg_list)) if connectivity[i] <= 2]
    mid_con_idx = [i for i in range(len(mfg_list)) if 2 < connectivity[i] <= 5]
    high_con_idx = [i for i in range(len(mfg_list)) if 5 < connectivity[i] <= 11]

    capacity = [agent_attributes["Q"][mfg_list[i]] for i in range(len(mfg_list))]
    low_cap_idx = [i for i in range(len(mfg_list)) if 0.4 < capacity[i] <= 1]
    high_cap_idx = [i for i in range(len(mfg_list)) if 0 < capacity[i] <= 0.4]

    impact = [agent_attributes["n"][mfg_list[i]] for i in range(len(mfg_list))]
    low_imp_idx = [i for i in range(len(mfg_list)) if 0 < impact[i] <= 3]
    high_imp_idx = [i for i in range(len(mfg_list)) if 3 < impact[i] <= 6]

    depth = [agent_attributes["depth"][mfg_list[i]] for i in range(len(mfg_list))]
    low_dep_idx = [i for i in range(len(mfg_list)) if 0 < depth[i] <= 1]
    high_dep_idx = [i for i in range(len(mfg_list)) if 1 < depth[i] <= 3]

    category = ["lhl", "lhm", "lhh",  "hhl", "hhm", "hhh", "lll", "llm", "llh", "hll", "hlm", "hlh"]
    index_list_by_category = {key:[] for key in category}
    for i in low_imp_idx:
        if i in low_cap_idx and i in low_con_idx:
            index_list_by_category["lll"].append(i)
        if i in low_cap_idx and i in mid_con_idx:
            index_list_by_category["llm"].append(i)
        if i in low_cap_idx and i in high_con_idx:
            index_list_by_category["llh"].append(i)
        if i in high_cap_idx and i in low_con_idx:
            index_list_by_category["lhl"].append(i)
        if i in high_cap_idx and i in mid_con_idx:
            index_list_by_category["lhm"].append(i)
        if i in high_cap_idx and i in high_con_idx:
            index_list_by_category["lhh"].append(i)
    for i in high_imp_idx:
        if i in low_cap_idx and i in low_con_idx:
            index_list_by_category["hll"].append(i)
        if i in low_cap_idx and i in mid_con_idx:
            index_list_by_category["hlm"].append(i)
        if i in low_cap_idx and i in high_con_idx:
            index_list_by_category["hlh"].append(i)
        if i in high_cap_idx and i in low_con_idx:
            index_list_by_category["hhl"].append(i)
        if i in high_cap_idx and i in mid_con_idx:
            index_list_by_category["hhm"].append(i)
        if i in high_cap_idx and i in high_con_idx:
            index_list_by_category["hhh"].append(i)

    return category, index_list_by_category

def plot_simplify_category(agent_attributes):
    # connectivity = [agent_attributes["g_in"][mfg_list[i]] + agent_attributes["g_out"][mfg_list[i]] for i in
    #                 range(len(mfg_list))]
    #
    # low_con_idx = [i for i in range(len(mfg_list)) if connectivity[i] <= 5]
    # high_con_idx = [i for i in range(len(mfg_list)) if 5 < connectivity[i] <= 11]
    #
    # capacity = [agent_attributes["Q"][mfg_list[i]] for i in range(len(mfg_list))]
    # low_cap_idx = [i for i in range(len(mfg_list)) if 0.4 < capacity[i] <= 1]
    # high_cap_idx = [i for i in range(len(mfg_list)) if 0 < capacity[i] <= 0.4]
    #
    # depth = [agent_attributes["depth"][mfg_list[i]] for i in range(len(mfg_list))]
    # low_dep_idx = [i for i in range(len(mfg_list)) if 0 < depth[i] <= 1]
    # high_dep_idx = [i for i in range(len(mfg_list)) if 1 < depth[i] <= 3]
    #
    # impact = [agent_attributes["n"][mfg_list[i]] for i in range(len(mfg_list))]
    # low_imp_idx = [i for i in range(len(mfg_list)) if 0 < impact[i] <= 3]
    # high_imp_idx = [i for i in range(len(mfg_list)) if 3 < impact[i] <= 6]

    connectivity = {i: agent_attributes["g_in"][mfg_list[i]] + agent_attributes["g_out"][mfg_list[i]] for i in
                     n_dis_met}

    low_con_idx = [i for i in n_dis_met if connectivity[i] <= 5]
    high_con_idx = [i for i in n_dis_met if 5 < connectivity[i] <= 11]

    capacity = {i: agent_attributes["Q"][mfg_list[i]] for i in n_dis_met}
    low_cap_idx = [i for i in n_dis_met if 0.4 < capacity[i] <= 1]
    high_cap_idx = [i for i in n_dis_met if 0 < capacity[i] <= 0.4]

    depth = {i: agent_attributes["depth"][mfg_list[i]] for i in n_dis_met}
    low_dep_idx = [i for i in n_dis_met if 0 < depth[i] <= 1]
    high_dep_idx = [i for i in n_dis_met if 1 < depth[i] <= 3]

    impact = {i: agent_attributes["kf"][mfg_list[i]]/360 for i in n_dis_met}
    # low_imp_idx = [i for i in n_dis_met if 0 < impact[i] <= 180]
    # high_imp_idx = [i for i in n_dis_met if 180 < impact[i] <= 360]

    low_imp_idx = [i for i in n_dis_met if 0 < impact[i] <= 0.5]
    high_imp_idx = [i for i in n_dis_met if 0.5 < impact[i] <= 1.01]

    prod = {i: agent_attributes["F"][mfg_list[i]] for i in n_dis_met}
    low_prod_idx = [i for i in n_dis_met if 0 < prod[i] <= 0.65]
    high_prod_idx = [i for i in n_dis_met if 0.65 < prod[i] <= 1.01]

    variety = {i: agent_attributes["v"][mfg_list[i]] for i in n_dis_met}
    low_var_idx = [i for i in n_dis_met if 0 < variety[i] <= 1]
    high_var_idx = [i for i in n_dis_met if 1 < variety[i] <= 3]

    kf = {i: agent_attributes["n"][mfg_list[i]] for i in n_dis_met}
    low_kf_idx = [i for i in n_dis_met if 0 <= kf[i] <= 3]
    high_kf_idx = [i for i in n_dis_met if 3 < kf[i] <= 6]

    comp = {i: agent_attributes["l"][mfg_list[i]] for i in n_dis_met}
    low_comp_idx = [i for i in n_dis_met if 0 <= comp[i] <= 5]
    high_comp_idx = [i for i in n_dis_met if 5 < comp[i] <= 12]

    kf = {i: agent_attributes["n"][mfg_list[i]]+agent_attributes["l"][mfg_list[i]] for i in n_dis_met}
    low_kf_idx = [i for i in n_dis_met if 0 <= kf[i] <= 6]
    high_kf_idx = [i for i in n_dis_met if 6 < kf[i] <= 15]

    category = ["ll", "lh", "hl", "hh"]
    index_list = {key: [] for key in category}
    # for i in low_con_idx:
    #     if i in low_dep_idx:
    #         index_list["ll"].append(i)
    #     if i in high_dep_idx:
    #         index_list["lh"].append(i)
    # for i in high_con_idx:
    #     if i in low_dep_idx:
    #         index_list["hl"].append(i)
    #     if i in high_dep_idx:
    #         index_list["hh"].append(i)

    # for i in low_con_idx:
    #     if i in low_imp_idx:
    #         index_list["ll"].append(i)
    #     if i in high_imp_idx:
    #         index_list["lh"].append(i)
    # for i in high_con_idx:
    #     if i in low_imp_idx:
    #         index_list["hl"].append(i)
    #     if i in high_imp_idx:
    #         index_list["hh"].append(i)

    for i in low_con_idx:
        if i in low_kf_idx:
            index_list["ll"].append(i)
        if i in high_kf_idx:
            index_list["lh"].append(i)
    for i in high_con_idx:
        if i in low_kf_idx:
            index_list["hl"].append(i)
        if i in high_kf_idx:
            index_list["hh"].append(i)

    # for i in low_dep_idx:
    #     if i in low_kf_idx:
    #         index_list["ll"].append(i)
    #     if i in high_kf_idx:
    #         index_list["lh"].append(i)
    # for i in high_dep_idx:
    #     if i in low_kf_idx:
    #         index_list["hl"].append(i)
    #     if i in high_kf_idx:
    #         index_list["hh"].append(i)

    # category = ["l", "h"]
    # index_list = {"l": low_con_idx, "h": high_con_idx}
    # index_list = {"l": low_cap_idx, "h": high_cap_idx}
    # index_list = {"l": low_imp_idx, "h": high_imp_idx}
    # index_list = {"l": low_dep_idx, "h": high_dep_idx}
    # index_list = {"l": low_prod_idx, "h": high_prod_idx}
    # index_list = {"l": low_var_idx, "h": high_var_idx}
    # index_list = {"l": low_kf_idx, "h": high_kf_idx}
    # index_list = {"l": low_comp_idx, "h": high_comp_idx}


    metrics = ["T", "O", "N", "H", "M_e"]
    cen_res = {met: {c: [] for c in category} for met in metrics}
    dis_res = {met: {c: [] for c in category} for met in metrics}

    difference = {met: [] for met in metrics}
    idx_for_diff = n_dis_met

    for metric in metrics:
        for cat in category:
            if metric == "O":
                cen_res[metric][cat] = [
                    centralized_results[mfg_list[i]]["results"]["O_c_flow"]+
                    centralized_results[mfg_list[i]]["results"]["O_c_production"]
                    for i in index_list[cat]]
                dis_res[metric][cat] = [
                    distributed_data[mfg_list[i]]["results"]["O_c_flow"] +
                    distributed_data[mfg_list[i]]["results"]["O_c_production"]
                    for i in index_list[cat]]

            if metric == "N":
                cen_res[metric][cat] = [centralized_results[mfg_list[i]]["results"]["N_f"] +
                                        centralized_results[mfg_list[i]]["results"]["N_p"]
                                        for i in index_list[cat]]
                dis_res[metric][cat] = [distributed_data[mfg_list[i]]["results"]["N_f"] +
                                        distributed_data[mfg_list[i]]["results"]["N_p"]
                                        for i in index_list[cat]]
            if metric == "H":
                cen_res[metric][cat] = [centralized_results[mfg_list[i]]["results"]["H_f"] +
                                        centralized_results[mfg_list[i]]["results"]["H_p"]
                                        for i in index_list[cat]]
                dis_res[metric][cat] = [distributed_data[mfg_list[i]]["results"]["H_f"] +
                                        distributed_data[mfg_list[i]]["results"]["H_p"]
                                        for i in index_list[cat]]
            if metric == "M_e":
                cen_res[metric][cat] = [centralized_results[mfg_list[i]]["results"]["M_e"]
                                        for i in index_list[cat]]
                dis_res[metric][cat] = [distributed_data[mfg_list[i]]["results"]["M_e"]
                                        for i in index_list[cat]]
            if metric == "T":
                cen_res[metric][cat] = [centralized_results[mfg_list[i]]["results"]["T_e"]
                                        for i in index_list[cat]]
                dis_res[metric][cat] = [distributed_data[mfg_list[i]]["results"]["T_e"]
                                        for i in index_list[cat]]

        if metric == "O":
            difference[metric] = [centralized_results[mfg_list[i]]["results"]["O_c_flow"] +
                                      centralized_results[mfg_list[i]]["results"]["O_c_production"] -
                                      distributed_data[mfg_list[i]]["results"]["O_c_flow"] -
                                      distributed_data[mfg_list[i]]["results"]["O_c_production"] for i in idx_for_diff]
        if metric == "N":
            difference[metric] = [centralized_results[mfg_list[i]]["results"]["N_f"] +
                                      centralized_results[mfg_list[i]]["results"]["N_p"] -
                                      distributed_data[mfg_list[i]]["results"]["N_f"] -
                                      distributed_data[mfg_list[i]]["results"]["N_p"] for i in idx_for_diff]
        if metric == "H":
            difference[metric] = [centralized_results[mfg_list[i]]["results"]["H_f"] +
                                      centralized_results[mfg_list[i]]["results"]["H_p"] -
                                      distributed_data[mfg_list[i]]["results"]["H_f"] -
                                      distributed_data[mfg_list[i]]["results"]["H_p"] for i in idx_for_diff]
        if metric == "M_e":
            difference[metric] = [centralized_results[mfg_list[i]]["results"]["M_e"] -
                                      distributed_data[mfg_list[i]]["results"]["M_e"] for i in idx_for_diff]

    difference["delta_d"] = [centralized_results[mfg_list[i]]["results"]["delta_d"] -
                                      distributed_data[mfg_list[i]]["results"]["delta_d"] for i in range(len(mfg_list))]

    performance_numbers = {met: {c: [] for c in ["c", "d", "s"]} for met in metrics}
    for i in range(len(difference["O"])):
        if difference["O"][i] >= 20:
            performance_numbers["O"]["d"].append(i)
        if difference["O"][i] <= -10:
            performance_numbers["O"]["c"].append(i)
        if -10 < difference["O"][i] < 20:
            performance_numbers["O"]["s"].append(i)

    for i in range(len(difference["N"])):
        if difference["N"][i] >= 1:
            performance_numbers["N"]["d"].append(i)
        if difference["N"][i] <= -1:
            performance_numbers["N"]["c"].append(i)
        if -1 < difference["N"][i] < 1:
            performance_numbers["N"]["s"].append(i)

    for i in range(len(difference["H"])):
        if difference["H"][i] >= 1:
            performance_numbers["H"]["d"].append(i)
        if difference["H"][i] <= -1:
            performance_numbers["H"]["c"].append(i)
        if -1 < difference["H"][i] < 1:
            performance_numbers["H"]["s"].append(i)

    performance_numbers["delta_d"] = {c: [] for c in ["c", "d", "s"]}
    for i in range(len(difference["delta_d"])):
        if difference["delta_d"][i] >= 3:
            performance_numbers["delta_d"]["d"].append(i)
        if difference["delta_d"][i] <= -3:
            performance_numbers["delta_d"]["c"].append(i)
        if -3 < difference["delta_d"][i] < 3:
            performance_numbers["delta_d"]["s"].append(i)



    # fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    # for met, ax in zip(metrics, axes.flat):
    #     ax.scatter(range(74), difference[met])
    #     # ax.title("Metrics: %s" % met)
    # plt.show()

    simple_res = {met: {key: [] for key in ["category", "approach", "value"]} for met in metrics}

    for met in metrics:
        simple_res[met]["category"] += ["Low connectivity, low capacity"] * len(index_list["ll"]) +\
                                     ["Low connectivity, high capacity"] * len(index_list["lh"]) +\
                                     ["High connectivity, low capacity"] *  len(index_list["hl"]) + \
                                     ["High connectivity, high capacity"] *  len(index_list["hh"]) + \
                                       ["Low connectivity, low capacity"] * len(index_list["ll"]) + \
                                       ["Low connectivity, high capacity"] * len(index_list["lh"]) + \
                                       ["High connectivity, low capacity"] * len(index_list["hl"]) + \
                                       ["High connectivity, high capacity"] * len(index_list["hh"])
        # simple_res[met]["category"] += ["Low"] * len(index_list["l"]) + ["High"] * len(index_list["h"]) + ["Low"] * len(index_list["l"]) + ["High"] * len(index_list["h"])

        simple_res[met]["approach"] += ["Centralized"] * sum(len(cen_res[met][cat]) for cat in category) +\
                                       ["Distributed"] * sum(len(dis_res[met][cat]) for cat in category)

        for cat in category:
            simple_res[met]["value"] += cen_res[met][cat]
        for cat in category:
            simple_res[met]["value"] += dis_res[met][cat]

    # x = ["Low connectivity\nlow depth", "Low connectivity\nhigh depth", "High connectivity\nlow depth",
    #      "High connectivity\nhigh depth"]
    x = ["Low connectivity\nlow complexity", "Low connectivity\nhigh complexity", "High connectivity\nlow complexity",
         "High connectivity\nhigh complexity"]
    # x = ["Low depth", "high depth"]
    # x = ["Low connectivity", "high connectivity"]
    # x = ["Low impact", "high impact"]
    title = {"O": 'Overage cost for different agent categories and approaches',
             "N": 'Network changes for different agent categories and approaches',
             "H": 'Network additions for different agent categories and approaches',
             "M_e": 'Communication for different agent categories and approaches'}
    y_label = {"O": 'Overage costs', "N": 'Network changes',
             "H": 'Network additions', "M_e": 'Communication (log10 scaled)'}

    title = {"O": 'Overage cost for different approaches',
             "N": 'Network changes for different approaches',
             "H": 'Network additions for different approaches',
             "M_e": 'Communication for different approaches',
             "T": 'Run time for different approaches'}
    y_label = {"O": 'Overage costs', "N": 'Network changes',
               "H": 'Network additions', "M_e": 'Communication', "T": 'Run Time'}
    for met in metrics:
        fig, ax = plt.subplots(figsize=(4, 4.5))
        df = pd.DataFrame(data=simple_res[met])
        # sns.boxplot(ax=ax, data=df, x="category", y="value", hue="approach", palette="Pastel1", linewidth=1, width=0.5, showmeans=True)
        sns.boxplot(ax=ax, data=df, x="approach", y="value", palette="Pastel1", linewidth=1, width=0.3,
                    showmeans=True)
        plt.show()
        ax.set_xticklabels(["Centralized", "Distributed"], fontsize=15)
        ax.set(xlabel=None, ylabel=None)
        ax.set_title(title[met], fontsize=15)
        ax.set_ylabel(y_label[met], fontsize=15)
        # ax.get_legend().remove()
        handles, labels = ax.get_legend_handles_labels()
        for line in ax.get_lines()[5::14]:
            line.set_marker("^")
            line.set_markerfacecolor('#E88482')
            line.set_markeredgecolor("black")
            line.set_markersize("10")
        for line in ax.get_lines()[12::14]:
            line.set_marker("s")
            line.set_markerfacecolor('#6699CC')
            line.set_markeredgecolor("black")
            line.set_markersize("10")
        handles += [
            Line2D([0], [0], marker='^', color='w', markeredgecolor='black', markerfacecolor='#E88482', markersize=10),
            Line2D([0], [0], marker='s', color='w', markeredgecolor='black', markerfacecolor='#6699CC', markersize=10)]
        labels += ["Mean Value (Centralized)", "Mean Value (Distributed)"]

        ax.legend(handles, labels, fontsize=12)
        plt.show()
        print("plot")

    for met in metrics:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        df = pd.DataFrame(data=simple_res[met])
        sns.boxplot(ax=ax, data=df, x="category", y="value", hue="approach", palette="Pastel1", linewidth=1, width=0.5, showmeans=True)
        plt.show()
        ax.set_xticklabels(x, fontsize=12)
        ax.set(xlabel=None, ylabel=None)
        ax.set_title(title[met], fontsize=15)
        ax.set_ylabel(y_label[met], fontsize=15)
        ax.get_legend().remove()
        handles, labels = ax.get_legend_handles_labels()
        if met == "M_e":
            ax.set_yscale('log')
        for line in ax.get_lines()[5::14]:
            line.set_marker("^")
            line.set_markerfacecolor('#E88482')
            line.set_markeredgecolor("black")
            line.set_markersize("10")
        for line in ax.get_lines()[12::14]:
            line.set_marker("s")
            line.set_markerfacecolor('#6699CC')
            line.set_markeredgecolor("black")
            line.set_markersize("10")
        handles += [
            Line2D([0], [0], marker='^', color='w', markeredgecolor='black', markerfacecolor='#E88482', markersize=10),
            Line2D([0], [0], marker='s', color='w', markeredgecolor='black', markerfacecolor='#6699CC', markersize=10)]
        labels += ["Mean Value (Centralized)", "Mean Value (Distributed)"]

        ax.legend(handles, labels, fontsize=12)
        plt.show()
        print("plot")

    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    plt.subplots_adjust(wspace=0.15, hspace=0.5)
    x = ["Low connectivity\nlow complexity", "Low connectivity\nhigh complexity", "High connectivity\nlow complexity","High connectivity\nhigh complexity"]
    x = ["Low connectivity\nlow depth", "Low connectivity\nhigh depth", "High connectivity\nlow depth",
         "High connectivity\nhigh depth"]
    x = ["Low depth\nlow complexity", "Low depth\nhigh complexity", "High depth\nlow complexity",
         "High depth\nhigh complexity"]
    # fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    # plt.subplots_adjust(wspace=0.15, hspace=0.25)
    # x = ["Low impact", "high impact"]
    # x = ["Low connectivity", "high connectivity"]
    # x = ["Low depth", "high depth"]
    # x = ["Low complexity", "high complexity"]
    title = {"O": 'Overage cost', "N": 'Network changes',
             "H": 'Network additions', "M_e": 'Communication (log10 scaled)'}
    for met, ax in zip(metrics, axes.flat):
        df = pd.DataFrame(data=simple_res[met])
        # sns.violinplot(ax=ax, data=df, x="metric", y="value", hue="approach", split=True,  palette="Pastel1", linewidth=1, inner=None)
        sns.boxplot(ax=ax, data=df, x="category", y="value", hue="approach", palette="Pastel1", linewidth=1,
                    width=0.5,
                    showmeans=True)
        ax.set_xticklabels(x, fontsize=12)
        ax.set(xlabel=None, ylabel=None)
        ax.set_title(title[met], fontsize=12)
        ax.get_legend().remove()
        handles, labels = ax.get_legend_handles_labels()

        for line in ax.get_lines()[5::14]:
            line.set_marker("^")
            line.set_markerfacecolor('#E88482')
            line.set_markeredgecolor("black")
            line.set_markersize("10")
        for line in ax.get_lines()[12::14]:
            line.set_marker("s")
            line.set_markerfacecolor('#6699CC')
            line.set_markeredgecolor("black")
            line.set_markersize("10")
        if met == "M_e":
            ax.set_yscale('log')
    handles += [
        Line2D([0], [0], marker='^', color='w', markeredgecolor='black', markerfacecolor='#E88482', markersize=10),
        Line2D([0], [0], marker='s', color='w', markeredgecolor='black', markerfacecolor='#6699CC', markersize=10)]
    labels += ["Mean Value (Centralized)", "Mean Value (Distributed)"]

    fig.legend(handles, labels, loc='upper center', ncol=4, bbox_to_anchor=(0.5, 0.95), fontsize=12)
    fig.suptitle("Performance metrics for categorized disruption scenarios",
                 fontsize=16)
    plt.show()
    print("Stop")


def performance_by_category(category, index_list_by_category):
    metrics = ["O", "N", "H", "M_e"]
    cen_res = {met: {c: [] for c in category} for met in metrics}
    dis_res = {met: {c: [] for c in category} for met in metrics}
    cen_mean_res = {met: {c: None for c in category} for met in metrics}
    dis_mean_res = {met: {c: None for c in category} for met in metrics}
    max_res = {met: None for met in metrics}

    for metric in metrics:
        for cat in category:
            if metric == "C":
                cen_res[metric][cat] = [centralized_results[mfg_list[i]]["results"]["C_f"]+
                                        centralized_results[mfg_list[i]]["results"]["C_p"]
                                        for i in index_list_by_category[cat]]
                dis_res[metric][cat] = [distributed_data[mfg_list[i]]["results"]["C_f"] +
                                        distributed_data[mfg_list[i]]["results"]["C_p"]
                                        for i in index_list_by_category[cat]]

            if metric == "O":
                cen_res[metric][cat] = [
                    # centralized_results[mfg_list[i]]["results"]["O_c_flow"]+
                                        centralized_results[mfg_list[i]]["results"]["O_c_production"]
                                        for i in index_list_by_category[cat]]
                dis_res[metric][cat] = [
                    # distributed_data[mfg_list[i]]["results"]["O_c_flow"] +
                                        distributed_data[mfg_list[i]]["results"]["O_c_production"]
                                        for i in index_list_by_category[cat]]

            if metric == "N":
                cen_res[metric][cat] = [centralized_results[mfg_list[i]]["results"]["N_f"]+
                                        centralized_results[mfg_list[i]]["results"]["N_p"]
                                        for i in index_list_by_category[cat]]
                dis_res[metric][cat] = [distributed_data[mfg_list[i]]["results"]["N_f"] +
                                        distributed_data[mfg_list[i]]["results"]["N_p"]
                                        for i in index_list_by_category[cat]]
            if metric == "H":
                cen_res[metric][cat] = [centralized_results[mfg_list[i]]["results"]["H_f"]+
                                        centralized_results[mfg_list[i]]["results"]["H_p"]
                                        for i in index_list_by_category[cat]]
                dis_res[metric][cat] = [distributed_data[mfg_list[i]]["results"]["H_f"] +
                                        distributed_data[mfg_list[i]]["results"]["H_p"]
                                        for i in index_list_by_category[cat]]
            if metric == "M_e":
                cen_res[metric][cat] = [centralized_results[mfg_list[i]]["results"]["M_e"]+
                                        centralized_results[mfg_list[i]]["results"]["M_e"]
                                        for i in index_list_by_category[cat]]
                dis_res[metric][cat] = [distributed_data[mfg_list[i]]["results"]["M_e"] +
                                        distributed_data[mfg_list[i]]["results"]["M_e"]
                                        for i in index_list_by_category[cat]]

        #     cen_mean_res[metric][cat] = statistics.mean(cen_res[metric][cat])
        #     dis_mean_res[metric][cat] = statistics.mean(dis_res[metric][cat])
        # max_res[metric] = max([cen_mean_res[metric][cat] for cat in category]+[dis_mean_res[metric][cat] for cat in category])
    res = {cat: {key: [] for key in ["approach", "metric", "value"]} for cat in category}
    # for metric in metrics:
    #     max_value = max([max(cen_res[metric][cat]) for cat in category if len(cen_res[metric][cat])!=0] +
    #                     [max(dis_res[metric][cat]) for cat in category if len(dis_res[metric][cat])!=0])
    #     for cat in category:
    #         cen_res[metric][cat][:] = [x / max_value for x in cen_res[metric][cat]]
    #         dis_res[metric][cat][:] = [x / max_value for x in dis_res[metric][cat]]

        #     cen_mean_res[metric][cat] = statistics.mean(cen_res[metric][cat])
        #     dis_mean_res[metric][cat] = statistics.mean(dis_res[metric][cat])
        # max_res[metric] = max(
        #     [cen_mean_res[metric][cat] for cat in category] + [dis_mean_res[metric][cat] for cat in category])

    # reformulating results
    for cat in category:
        for met in metrics:
            res[cat]["approach"] += ["Centralized"]*len(cen_res[met][cat]) + ["Distributed"]*len(dis_res[met][cat])
            res[cat]["metric"] += [met] * (len(cen_res[met][cat])+len(dis_res[met][cat]))
            res[cat]["value"] += cen_res[met][cat] + dis_res[met][cat]

    new_res = {conn: {key: [] for key in ["category", "metric", "value"]} for conn in ["low", "mid", "high"]}

    for met in metrics:
        new_res["low"]["category"] += ["Low impact, low capacity"] * len(index_list_by_category["lll"]) + \
                                     ["Low impact, high capacity"] * len(index_list_by_category["lhl"]) + \
                                     ["High impact, low capacity"] * len(index_list_by_category["hll"]) + \
                                     ["High impact, high capacity"] * len(index_list_by_category["hhl"])
        new_res["mid"]["category"] += ["Low impact, low capacity"] * len(index_list_by_category["llm"]) + \
                                     ["Low impact, high capacity"] * len(index_list_by_category["lhm"]) + \
                                     ["High impact, low capacity"] * len(index_list_by_category["hlm"]) + \
                                     ["High impact, high capacity"] * len(index_list_by_category["hhm"])
        new_res["high"]["category"] += ["Low impact, low capacity"] * len(index_list_by_category["llh"]) + \
                                      ["Low impact, high capacity"] * len(index_list_by_category["lhh"]) + \
                                      ["High impact, low capacity"] * len(index_list_by_category["hlh"]) + \
                                      ["High impact, high capacity"] * len(index_list_by_category["hhh"])

        new_res["low"]["metric"] += [met] * (len(index_list_by_category["lll"]) + \
                                     len(index_list_by_category["lhl"]) + \
                                     len(index_list_by_category["hll"]) + \
                                     len(index_list_by_category["hhl"]))
        new_res["mid"]["metric"] += [met] * (len(index_list_by_category["llm"]) + \
                                     len(index_list_by_category["lhm"]) + \
                                     len(index_list_by_category["hlm"]) + \
                                     len(index_list_by_category["hhm"]))
        new_res["high"]["metric"] += [met] * (len(index_list_by_category["llh"]) + \
                                      len(index_list_by_category["lhh"]) + \
                                      len(index_list_by_category["hlh"]) + \
                                      len(index_list_by_category["hhh"]))
        for cat in ["lll", "lhl", "hll", "hhl"]:
            new_res["low"]["value"] += [cen_res[met][cat][i] - dis_res[met][cat][i] for i in range(len(cen_res[met][cat]))]
        for cat in ["llm", "lhm", "hlm", "hhm"]:
            new_res["mid"]["value"] += [cen_res[met][cat][i] - dis_res[met][cat][i] for i in range(len(cen_res[met][cat]))]
        for cat in ["llh", "lhh", "hlh", "hhh"]:
            new_res["high"]["value"] += [cen_res[met][cat][i] - dis_res[met][cat][i] for i in range(len(cen_res[met][cat]))]

    diff_res = {met: {c: [] for c in category} for met in metrics}
    for metric in metrics:
        for cat in category:
            for i in range(len(cen_res[metric][cat])):
                diff_res[metric][cat].append(cen_res[metric][cat][i]-dis_res[metric][cat][i])

    for metric in metrics:
        max_value = max([max(abs(diff_res[metric][cat][i]) for i in range(len(diff_res[metric][cat]))) for cat in category if len(diff_res[metric][cat])!=0])
        for cat in category:
            diff_res[metric][cat][:] = [x / (abs(max_value)+1e-5) for x in diff_res[metric][cat]]
    new_res2 = {met: {key: [] for key in ["category", "connectivity", "value"]} for met in metrics}

    for met in metrics:
        new_res2[met]["category"] += ["Low impact, low capacity"] * len(index_list_by_category["lll"]) + \
                                     ["Low impact, high capacity"] * len(index_list_by_category["lhl"]) + \
                                     ["High impact, low capacity"] * len(index_list_by_category["hll"]) + \
                                     ["High impact, high capacity"] * len(index_list_by_category["hhl"]) + \
                                     ["Low impact, low capacity"] * len(index_list_by_category["llm"]) + \
                                     ["Low impact, high capacity"] * len(index_list_by_category["lhm"]) + \
                                     ["High impact, low capacity"] * len(index_list_by_category["hlm"]) + \
                                     ["High impact, high capacity"] * len(index_list_by_category["hhm"]) +\
                                     ["Low impact, low capacity"] * len(index_list_by_category["llh"]) + \
                                     ["Low impact, high capacity"] * len(index_list_by_category["lhh"]) + \
                                     ["High impact, low capacity"] * len(index_list_by_category["hlh"]) + \
                                     ["High impact, high capacity"] * len(index_list_by_category["hhh"])

        new_res2[met]["connectivity"] += ["Low"] * (len(index_list_by_category["lll"]) + \
                                     len(index_list_by_category["lhl"]) + \
                                     len(index_list_by_category["hll"]) + \
                                     len(index_list_by_category["hhl"]))
        new_res2[met]["connectivity"] += ["Mid"] * (len(index_list_by_category["llm"]) + \
                                     len(index_list_by_category["lhm"]) + \
                                     len(index_list_by_category["hlm"]) + \
                                     len(index_list_by_category["hhm"]))
        new_res2[met]["connectivity"] += ["High"] * (len(index_list_by_category["llh"]) + \
                                      len(index_list_by_category["lhh"]) + \
                                      len(index_list_by_category["hlh"]) + \
                                      len(index_list_by_category["hhh"]))
        for cat in ["lll", "lhl", "hll", "hhl", "llm", "lhm", "hlm", "hhm", "llh", "lhh", "hlh", "hhh"]:
            new_res2[met]["value"] += diff_res[met][cat]

    return res, new_res, new_res2


def plot_difference_by_category(new_res2):
    metrics = ["O", "N", "H", "M_e"]
    title = {"O": 'Cost of over-capacity', "N": 'Changes to existing network',
             "H": 'New agents/edges to network', "M_e": 'Occurred agent communication'}
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    plt.subplots_adjust(wspace=0.2, hspace=0.25)
    for cat, ax in zip(metrics, axes.flat):

        df = pd.DataFrame(data=new_res2[cat])

        sns.boxplot(ax=ax, data=df, y="connectivity", x="value", hue="category", palette=['white', '#9DC3E7', '#BCE6D8', '#FEB2B4'], linewidth=1, width=0.6, orient="h", flierprops={"marker": "x"},showmeans=True)

        ax.set(xlabel=None, ylabel=None)
        ax.set_xlabel('Perfomrance difference (centralized minus distributed)', fontsize=12)
        ax.set_ylabel('Connectivity', fontsize=12)
        ax.set_yticklabels(["Low", "Mid", "High"], fontsize=12)
        ax.yaxis.set_label_coords(-0.1, 0.5)
        ax.set_title(title[cat], fontsize=12)
        ax.get_legend().remove()
        handles, labels = ax.get_legend_handles_labels()

        for line in ax.get_lines()[5::28]:
            line.set_marker("^")
            line.set_markerfacecolor('0.8')
            line.set_markeredgecolor("black")
            line.set_markersize("7")
        for line in ax.get_lines()[12::28]:
            line.set_marker("s")
            line.set_markerfacecolor('#6699CC')
            line.set_markeredgecolor("black")
            line.set_markersize("7")
        for line in ax.get_lines()[19::28]:
            line.set_marker("o")
            line.set_markerfacecolor('#0AAF88')
            line.set_markeredgecolor("black")
            line.set_markersize("7")
        for line in ax.get_lines()[26::28]:
            line.set_marker("d")
            line.set_markerfacecolor('#E88482')
            line.set_markeredgecolor("black")
            line.set_markersize("7")
        line = ax.get_lines()[75]
        line.set_marker("d")
        line.set_markerfacecolor('#E88482')
        line.set_markeredgecolor("black")
        line.set_markersize("7")
        if cat == "O":
            ax.set_xlim(-0.18, 0.13)
            ax.axvline(x=0, ls='--', color='grey')
        if cat == "N": ax.set_xlim(0.0, 0.5)
        if cat == "H": ax.set_xlim(-1.05, 0.05)
        if cat == "M_e": ax.set_xlim(0.55, 1.05)


    handles += [Line2D([0], [0], marker='^', color='w', markeredgecolor='black', markerfacecolor='0.8', markersize=7),
                Line2D([0], [0], marker='s', color='w', markeredgecolor='black', markerfacecolor='#6699CC', markersize=7),
                Line2D([0], [0], marker='o', color='w', markeredgecolor='black', markerfacecolor='#0AAF88', markersize=7),
                Line2D([0], [0], marker='d', color='w', markeredgecolor='black', markerfacecolor='#E88482', markersize=7)]
    labels += ["Mean (low capacity, low impact)", "Mean (low impact, high capacity", "Mean (high impact, low capacity", "Mean (high impact, high capacity)"]

    # fig.supxlabel('Normalized metric values of the difference between centralized and distributed approaches')
    # fig.supylabel('Level of connectivity')
    fig.legend(handles, labels, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.0), fontsize=12)
    fig.suptitle("Normalized metric values of the difference between centralized and distributed approaches\nfor categorized disruption scenarios based on agent attributes", fontsize=16)
    plt.show()


def plot_all_categories(distributed_data, centralized_results, category, res):
# plt.subplots_adjust(wspace=0.2, hspace=0.4)
# plt.suptitle("Normalized average values of performance metrics for scenarios that are categorized by agent attributes", fontsize=16)
# x = ["Total \n over-capacity \n cost", "# of changes \n to existing \n agents and edges", "# of added \n new agents \n and edges", "# of agent \n communication"]
    fig, axes = plt.subplots(4, 3, figsize=(15, 12))
    plt.subplots_adjust(wspace=0.15, hspace=0.5)
    x = ["Cost of\nover-capacity", "Changes to\nnetwork", "Additions to\nnetwork", "Agent\ncommunication"]
    title = {"lll": 'Low impact, low capacity, low connectivity', "llm": 'Low impact, low capacity, mid connectivity', "llh": 'Low impact, low capacity, high connectivity',
             "lhl": 'Low impact, high capacity, low connectivity', "lhm": 'Low impact, high capacity, mid connectivity', "lhh":'Low impact, high capacity, high connectivity',
             "hll": 'High impact, low capacity, low connectivity', "hlm": 'High impact, low capacity, mid connectivity', "hlh": 'High impact, low capacity, high connectivity',
             "hhl": 'High impact, high capacity, low connectivity', "hhm": 'High impact, high capacity, mid connectivity', "hhh":'High impact, high capacity, high connectivity'}
    for cat, ax in zip(category, axes.flat):

    # for n, cat in enumerate(category):
    #     # add a new subplot iteratively
    #     ax = plt.subplot(2, 3, n + 1)

        df = pd.DataFrame(data=res[cat])
        # sns.violinplot(ax=ax, data=df, x="metric", y="value", hue="approach", split=True,  palette="Pastel1", linewidth=1, inner=None)
        try:
            sns.boxplot(ax=ax, data=df, x="metric", y="value", hue="approach", palette="Pastel1", linewidth=1, width=0.5,
                    showmeans=True)

    # , meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black","markersize":"5"}
        # ax.scatter(x, [dis_mean_res[m][cat] for m in metrics], marker='s', color='#496C88', s=100)
        # ax.scatter(x, [cen_mean_res[m][cat] for m in metrics], marker='^', color='#CC6677', s=100)
            ax.text(-0.85, 0, "Low", fontsize=12)
            ax.text(-0.85, 1, "High", fontsize=12)
            ax.set_xticklabels(x, fontsize=10)
            ax.set_yticklabels([])
            ax.set_ylim(-0.05, 1.05)
            ax.set(xlabel=None, ylabel=None)
            ax.set_title(title[cat], fontsize=12)
            ax.get_legend().remove()
            handles, labels = ax.get_legend_handles_labels()

            for line in ax.get_lines()[5::14]:
                line.set_marker("^")
                line.set_markerfacecolor('#E88482')
                line.set_markeredgecolor("black")
                line.set_markersize("10")
            for line in ax.get_lines()[12::14]:
                line.set_marker("s")
                line.set_markerfacecolor('#6699CC')
                line.set_markeredgecolor("black")
                line.set_markersize("10")
        except:
            delta_d = {key: [] for key in ["approach", "category", "value"]}
            barWidth = 0.25
            idx = [i for i in n_dis_unmet if abs(distributed_data[mfg_list[i]]["results"]["delta_d"]-centralized_results[mfg_list[i]]["results"]["delta_d"]) > 0.5 and i<50]

            delta_d["approach"] = ["Centralized"]*len(idx) + ["Distributed"]*len(idx)
            delta_d["value"] = [centralized_results[mfg_list[i]]["results"]["delta_d"] for i in idx] + [distributed_data[mfg_list[i]]["results"]["delta_d"] for i in idx]
            # for i in idx:
            #     if i in low_imp_idx and i in low_con_idx:
            #         delta_d["category"].append("low impact, low connectivity")
            #     if i in low_imp_idx and i in mid_con_idx:
            #         delta_d["category"].append("low impact, mid connectivity")
            #     if i in low_imp_idx and i in high_con_idx:
            #         delta_d["category"].append("low impact, high connectivity")
            #     if i in high_imp_idx and i in low_con_idx:
            #         delta_d["category"].append("high impact, low connectivity")
            #     if i in high_imp_idx and i in mid_con_idx:
            #         delta_d["category"].append("high impact, mid connectivity")
            #     if i in high_imp_idx and i in high_con_idx:
            #         delta_d["category"].append("high impact, high connectivity")
            # delta_d["category"] *= 2
            delta_d["category"] = idx*2

            ax.axvspan(-0.5, 2.5, facecolor='0.8', alpha=0.5)
            df = pd.DataFrame(data=delta_d)
            sns.barplot(ax=ax, data=df, x="category", y="value", hue="approach", palette="Pastel1", width=0.5, edgecolor=".5")
            # br1 = [r for r in range(len(idx))]
            # br2 = [x + barWidth for x in br1]
            #
            # ax.bar(br1, dis_delta_d, color='#9DC3E7', width=barWidth, edgecolor='grey', label='Distributed')
            # ax.bar(br2, cen_delta_d, color='#FEB2B4', width=barWidth, edgecolor='grey', label='Centralized')
            ax.text(0.5, 90, "High impact", fontsize=12)
            ax.text(3.65, 80, "Low \nimpact", fontsize=12)

            # ax.set_facecolor('0.95')
            ax.set_xticklabels([])
            ax.set_xlabel('Disruption scenarios ' r'($\Delta^d>0$):' '\n low connectivity and insufficient capacity', fontsize=10)
            ax.set_ylabel('Unmet demand ' r'$\Delta^d$', fontsize=12)
            ax.yaxis.set_label_coords(-0.07, 0.5)
            ax.get_legend().remove()
            # tick_idx = [i + 1 for i in idx]
            # ax.set_xticklabels(['%s' % i for i in tick_idx])
            ax.set_title("Unmet demands in scenarios with redundancy", fontsize=12)

        # if n == 4: ax.legend(labels=["Distributed", "Centralized"], ncol=2, bbox_to_anchor=(0.5, -0.3), loc='lower center')
    handles += [Line2D([0], [0], marker='^', color='w', markeredgecolor='black', markerfacecolor='#E88482', markersize=10),
                Line2D([0], [0], marker='s', color='w', markeredgecolor='black', markerfacecolor='#6699CC', markersize=10)]
    labels += ["Mean Value (Centralized)", "Mean Value (Distributed)"]

    fig.legend(handles, labels, loc='upper center', ncol=4, bbox_to_anchor=(0.5, 0.95), fontsize=12)
    fig.suptitle("Normalized performance metrics for categorized disruption scenarios based on agent attributes", fontsize=16)
    plt.show()


agent_attributes = reformulate_results(distributed_data, centralized_results)
# category, index_list_by_category = get_category(agent_attributes)
# res, new_res, new_res2 = performance_by_category(category, index_list_by_category)
# demand_satisfaction_plots(distributed_data, centralized_results, mfg_list, n_dis_unmet, n_cen_unmet)


plot_simplify_category(agent_attributes)
print("Stop")

# plot_attributes(mfg_list, agent_attributes)
#
# demand_satisfaction_plots(distributed_data, centralized_results, mfg_list, n_dis_unmet, n_cen_unmet)
#
# network_change_plots(distributed_data, centralized_results, mfg_list, n_dis_met, n_cen_met)
#
# algo_perf_plots(distributed_data, centralized_results, mfg_list, n_dis_met, n_dis_unmet, n_cen_met, n_cen_unmet)
>>>>>>> Stashed changes
