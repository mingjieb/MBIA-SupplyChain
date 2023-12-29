#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.lines as mlines
import json


filename = '../initialization/TASE_Setup.xlsx'
data = pd.read_excel(filename, sheet_name='Agent', index_col=[0, 4])

with open("../initialization/InitialPlans-New.json") as f:
    initial_plan = json.load(f)

# V = set(data.index.get_level_values('AgentName'))
V = []
for v in data.index.get_level_values('AgentName'):
    if v not in V:
        V.append(v)
link = pd.read_excel(filename, sheet_name='Link', index_col=[0, 1])

info = {}
info['V_type'] = data['AgentType'].to_dict()
info['V_type'] = {key[0]: val for key, val in info['V_type'].items()}
info['depth'] = data['Level'].to_dict()
info['depth'] = {key[0]: val for key, val in info['depth'].items()}

# E = set(link.index)
E = []
for e in link.index:
    if e not in E:
        E.append(e)

# %%
# G = nx.DiGraph()
# # G.graph["graph"] = dict(rankdir="LR")
# G.add_nodes_from(V)
# G.add_edges_from(E)
#
# nx.set_node_attributes(G, info['V_type'], name='type')
# nx.set_node_attributes(G, info['depth'], name='subset')

# UG = G.to_undirected()
# sub_graphs = (UG.subgraph(c).copy() for c in nx.connected_components(UG))
#
# for i, sg in enumerate(sub_graphs):
#     print("subgraph {} has {} nodes".format(i, sg.number_of_nodes()))
#     print( "\tNodes:", sg.nodes(data=True))
#     print("\tEdges:", sg.edges())
V_a, E_a = [], []
V_d, E_d = ["cluster_sup_3"], []
for prod in initial_plan["Productions"]:
    if prod["Agent"] not in V_a:
        V_a.append(prod["Agent"])

for flow in initial_plan["Flows"]:
    if (flow["Source"], flow["Dest"]) not in E_a:
        E_a.append((flow["Source"], flow["Dest"]))
    if flow["Dest"] not in V_a:
        V_a.append(flow["Dest"])
    if flow["Source"] == "cluster_sup_3":
        V_d.append(flow["Dest"])
        E_d.append((flow["Source"], flow["Dest"]))
    if flow["Dest"] == "cluster_sup_3":
        V_d.append(flow["Source"])
        E_d.append((flow["Source"], flow["Dest"]))

info_a = {}
info_a['V_type'] = data['AgentType'].to_dict()
info_a['V_type'] = {key[0]: val for key, val in info_a['V_type'].items() if key[0] in V_a}
info_a['depth'] = data['Level'].to_dict()
info_a['depth'] = {key[0]: val for key, val in info_a['depth'].items() if key[0] in V_a}

G = nx.DiGraph()
# G.graph["graph"] = dict(rankdir="LR")
G.add_nodes_from(V_a)
G.add_edges_from(E_a)

nx.set_node_attributes(G, info_a['V_type'], name='type')
nx.set_node_attributes(G, info_a['depth'], name='subset')



#%%
# final_manuf = [node for node, attrs in G.nodes(data=True) if attrs['subset'] == 2]
subgraphs = {}
def add_pred(succ, root):
    if len(list(G.predecessors(succ))) > 0:
        for pred in G.predecessors(succ):
            subgraphs[root].add_node(pred, type = types[pred], subset=subsets[pred])
            subgraphs[root].add_edge(pred, succ)
            add_pred(pred, root)
    else:
        return 0


types = nx.get_node_attributes(G, 'type')
subsets = nx.get_node_attributes(G, 'subset')
# for node in final_manuf:
#     subgraphs[node] = nx.DiGraph()
#     subgraphs[node].add_node(node, type=types[node], subset=subsets[node])
#     add_pred(node, node)



#%%
# fig, ax = plt.subplots(dpi=1200)
cmap = plt.get_cmap()

ColorMap = {
    'Tier3': "#FFD966",
    'Tier2': "#A9D18E",
    'Tier1': "#9DC3E6",
    'Assembly': "#F4B183",
    'Customer': "#BFBFBF"
}

SizeMap = {
    'Tier3': 50,
    'Tier2': 30,
    'Tier1': 50,
    'Assembly': 120,
    'Customer': 70
}
# LegendMap = {
#     'Tier3': "Raw Material Suppliers",
#     'Tier2': "Parts suppliers",
#     'Tier1': "Component suppliers",
#     'Assembly': "Cockpit assembly",
#     'Customer': "Vehicle assembly (Customer)"
# }

color_values = [ColorMap[type] for type in nx.get_node_attributes(G, 'type').values()]
size_values = [SizeMap[type] for type in nx.get_node_attributes(G, 'type').values()]

# cNorm = colors.Normalize(vmin=0, vmax=max(values))
# scalarMap = cm.ScalarMappable(norm=cNorm, cmap=cmap)
# handler = []
# for label in ColorLegend:
#     handler.append(
#         mlines.Line2D([], [], color=scalarMap.to_rgba(ColorLegend[label]), marker='o', linestyle='None',
#                       label=label))
# handler = []
# for label in ColorMap:
#     handler.append(
#         mlines.Line2D([], [], color=ColorMap[label], marker='o', linestyle='None',
#                       label=LegendMap[label]))


fig, ax = plt.subplots(dpi=400)
# values = [ColorLegend[type] for type in nx.get_node_attributes(G, 'type').values()]
node_pose = nx.multipartite_layout(G)
for key in node_pose.keys():
    if info["depth"][key] == 5:
        node_pose[key][1] *= 5
        node_pose[key][0] *= 1.5
    if info["depth"][key] == 4:
        node_pose[key][1] *= 10
        node_pose[key][0] *= 2
    if info["depth"][key] == 3:
        node_pose[key][1] *= 2
        node_pose[key][0] *= 3
    # if info["depth"][key] == 2:
    #     node_pose[key][1] *= 15
    if info["depth"][key] == 1:
        node_pose[key][1] *= 3

# nx.draw_networkx(G, cmap=cmap, vmin=0, vmax=max(values), node_color=values,
#                  arrows=True, with_labels=False, node_size=50, font_size=4,
#                  pos=node_pose, ax=ax, width=0.5, arrowsize=5)
<<<<<<< Updated upstream
nx.draw_networkx(G, node_color=color_values, linewidths = 0.2, edgecolors='black', node_size=size_values, pos=node_pose,
                 with_labels = False, arrows=True, edge_color='#262626',
                 ax=ax, width=0.5, arrowsize=4)

=======
# nx.draw_networkx(G, node_color=color_values, linewidths = 0.5, edgecolors='black', node_size=size_values, pos=node_pose,
#                  with_labels = True, arrows=True, edge_color='#262626',
#                  ax=ax, width=0.5, arrowsize=4)
node_transparency, edge_transparency = [], []
for v in nx.nodes(G):
    if v in V_d: node_transparency.append(1.0)
    else: node_transparency.append(0.3)

for e in nx.edges(G):
    if e in E_d: edge_transparency.append(1.0)
    else: edge_transparency.append(0.3)

node_label_map = {}
for v in nx.nodes(G):
    if v == "cluster_sup_3" or "assy" in v: node_label_map[v] = v
    else: node_label_map[v] = ""

nx.draw_networkx_nodes(G, node_color=color_values, linewidths = 0.5,  node_size=size_values, pos=node_pose, alpha=node_transparency)
nx.draw_networkx_labels(G, pos=node_pose, labels=node_label_map)
nx.draw_networkx_edges(G, node_pose, arrows=True, edge_color='black', width=2, arrowsize=5, alpha=edge_transparency)

handles = [Line2D([0], [0], marker='o', color='w', markeredgecolor='black', markerfacecolor=node_color, markersize=10) for node_color in list(ColorMap.values())]

labels = ["Raw material\nsupplier", "Part\nsupplier", "Component\nsupplier", "Cockpit\nassembly", "Auto assembly\n(customer)"]
# fig.supxlabel('Normalized metric values of the difference between centralized and distributed approaches')
# fig.supylabel('Level of connectivity')
fig.legend(handles, labels, loc='lower center', ncol=5, bbox_to_anchor=(0.5, 0.1), fontsize=12)

>>>>>>> Stashed changes
plt.axis('off')
# plt.legend(handles=handler, loc="upper center", ncol=len(handler))
# fig.tight_layout()
plt.show()