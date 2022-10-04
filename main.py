import sys
import gurobipy as gp
import numpy as np
import pandas as pd
from scipy.stats import truncnorm
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.lines as mlines
import json

# %%
SCID = 00
filename = 'ConferenceCase.xlsx'
data = pd.read_excel(filename, sheet_name=str(SCID).zfill(2) + '_SD', index_col=[0, 1])

V = set(data.index.get_level_values('StageName'))
# K = set(data.index.get_level_values('prodType'))

link = pd.read_excel(filename, sheet_name=str(SCID).zfill(2) + '_LL', index_col=[0, 1])
info = {}
info['V_type'] = data['stageClassification'].to_dict()
info['V_type'] = {key[0]: val for key, val in info['V_type'].items()}
info['depth'] = data['relDepth'].to_dict()
info['depth'] = {key[0]: val for key, val in info['depth'].items()}

E = set(link.index)

# %%
G = nx.DiGraph()
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
final_manuf = [node for node, attrs in G.nodes(data=True) if attrs['subset'] == 2]
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
for node in final_manuf:
    subgraphs[node] = nx.DiGraph()
    subgraphs[node].add_node(node, type=types[node], subset=subsets[node])
    add_pred(node, node)



#%%
# fig, ax = plt.subplots(dpi=1200)
cmap = plt.get_cmap()
ColorLegend = {
    'Dist': 1,
    'Manuf': 2,
    'Part': 3,
    'Retail': 4
}

values = [ColorLegend[type] for type in nx.get_node_attributes(G, 'type').values()]


cNorm = colors.Normalize(vmin=0, vmax=max(values))
scalarMap = cm.ScalarMappable(norm=cNorm, cmap=cmap)
handler = []
for label in ColorLegend:
    handler.append(
        mlines.Line2D([], [], color=scalarMap.to_rgba(ColorLegend[label]), marker='o', linestyle='None',
                      label=label))


# %%
for key, subgraph in subgraphs.items():
    if key == 'Manuf_0047':
        fig, ax = plt.subplots(dpi=400)
        values = [ColorLegend[type] for type in nx.get_node_attributes(subgraph, 'type').values()]
        nx.draw_networkx(subgraph,
                         cmap=cmap, vmin=0, vmax=max(values), node_color=values,
                         arrows=True,
                         with_labels=True,
                         # labels={v: "" for v in V},
                         node_size=50,
                         font_size=4,
                         pos=nx.multipartite_layout(G),
                         # pos=nx.spectral_layout(G),
                         ax=ax)
        plt.axis('off')
        plt.legend(handles=handler, loc="lower left", ncol=len(handler))
        fig.tight_layout()
        plt.show()

#%%
def jaccard_similarity(g, h):
    i = set(g).intersection(h)
    return round(len(i) / (len(g) + len(h) - len(i)),3)

import numpy as np
shape = (len(subgraphs), len(subgraphs))
sim = np.zeros(shape)
list_subgraphs = list(subgraphs.values())
for i, j in np.indices(shape):
    sim[i, j] = [v for v in nx.optimize_graph_edit_distance(list_subgraphs[0], list_subgraphs[1])][0]

print(sim)
#%%
import collections
degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
# print "Degree sequence", degree_sequence
degreeCount = collections.Counter(degree_sequence)
deg, cnt = zip(*degreeCount.items())

fig, ax = plt.subplots()
plt.bar(deg, cnt, width=0.80, color='b')

plt.title("Degree Histogram")
plt.ylabel("Count")
plt.xlabel("Degree")
ax.set_xticks([d + 0.4 for d in deg])
ax.set_xticklabels(deg)


plt.show()