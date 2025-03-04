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


filename = '../initialization/TASE_Setup.xlsx'
data = pd.read_excel(filename, sheet_name='Agent', index_col=[0, 4])

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
G = nx.DiGraph()
# G.graph["graph"] = dict(rankdir="LR")
G.add_nodes_from(V)
G.add_edges_from(E)

nx.set_node_attributes(G, info['V_type'], name='type')
nx.set_node_attributes(G, info['depth'], name='subset')

# UG = G.to_undirected()
# sub_graphs = (UG.subgraph(c).copy() for c in nx.connected_components(UG))
#
# for i, sg in enumerate(sub_graphs):
#     print("subgraph {} has {} nodes".format(i, sg.number_of_nodes()))
#     print( "\tNodes:", sg.nodes(data=True))
#     print("\tEdges:", sg.edges())

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
    'Tier2': "#9DC3E6",
    'Tier1': "#A9D18E",
    'Assembly': "#BFBFBF",
    'Customer': "#F4B183"
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
        node_pose[key][1] *= 10
        node_pose[key][0] *= 1.5
    if info["depth"][key] == 4:
        node_pose[key][1] *= 20
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
nx.draw_networkx(G, node_color=color_values, linewidths = 0.2, edgecolors='black', node_size=size_values, pos=node_pose,
                 with_labels = False, arrows=True, edge_color='#262626',
                 ax=ax, width=0.5, arrowsize=4)

plt.axis('off')
# plt.legend(handles=handler, loc="upper center", ncol=len(handler))
# fig.tight_layout()
plt.show()