# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 13:07:36 2021

@author: mingjiebi
"""
import pandas as pd

import gurobipy as gp
from gurobipy import GRB, abs_
import networkx as nx
import matplotlib.pyplot as plt
import math
# from pyvis.network import Network

#### Initialize the supply chain network

parameter_file = "Distributed_Comparison - Copy.xlsx"

# Demand or supply at each vertex for each product
d = pd.read_excel(parameter_file, sheet_name='d', index_col=0)

# Product set P
P = list(d.columns)

# Vertices name
vertices = list(d.index)

# Cost at each link for each product from start vertex to end vertex
c = pd.read_excel(parameter_file, sheet_name='c', index_col=0)

p = pd.read_excel(parameter_file, sheet_name='p', index_col=0)

# The original capacity at each link for each product from start vertex to end vertex
u = pd.read_excel(parameter_file, sheet_name='u', index_col=0)

# The original inventory at each vertices for each product
I_o = pd.read_excel(parameter_file, sheet_name='I_o', index_col=0)
# The inventory limit at each vertices
I_bar = pd.read_excel(parameter_file, sheet_name='I_bar', index_col=0)

# The unit of product k' used for produce/assemble product k
r = pd.read_excel(parameter_file, sheet_name='r', index_col=0)
# The production limit at each vertices
a_bar = pd.read_excel(parameter_file, sheet_name='a_bar', index_col=0)
# beta = pd.read_excel(parameter_file, sheet_name='beta', index_col=0)
c_a = pd.read_excel(parameter_file, sheet_name='c_a', index_col=0)

# The fixed cost to use vertex production
phi_p = pd.read_excel(parameter_file, sheet_name='phi_p', index_col=0)
# The fixed cost to use vertex inventory
phi_I = pd.read_excel(parameter_file, sheet_name='phi_I', index_col=0)

# The fixed cost to use link
f = pd.read_excel(parameter_file, sheet_name='f', index_col=0)

# The fixed cost to unit added capacity
c_Q = pd.read_excel(parameter_file, sheet_name='c_Q', index_col=0)

# Backup vertex
back_v = pd.read_excel(parameter_file, sheet_name='V_a', index_col=0)
# Backup vertex
back_l = pd.read_excel(parameter_file, sheet_name='E_a', index_col=0)


# Links name
start_vertex = list(c.index)
end_vertex = list(c.get("End"))
links = []
for i in range(len(start_vertex)):
    links.append((str(start_vertex[i]), str(end_vertex[i])))

# Backup vertices
V_a = list(back_v.index)
# Backup links
s_v = list(back_l.index)
e_v = list(back_l.get("End"))
E_a = []
for i in range(len(s_v)):
    E_a.append((str(s_v[i]), str(e_v[i])))

# M(k): set of products that are used to produce/assemble product k
M = {k: [] for k in P}
for k in P:
    for p in P:
        if r.loc[p, k] > 1e-6 and p not in M[k]:
            M[k].append(p)

# N(k): set of products that need product k to be produced/assembled
N = {k: [] for k in P}
for k in P:
    for p in P:
        if r.loc[k, p] > 1e-6 and p not in N[k]:
            N[k].append(p)

# Reformate the data as a 1-D list

# (start, end, product)
links_with_products = []
cost = []
links_with_customer = []
price = []
for i in range(len(start_vertex)):
    for j in range(len(P)):
        # Cost data with the link from start_vertex
        tmp = pd.DataFrame(c.loc[str(start_vertex[i]), ["End", P[j]]])
        # Issue with unknown reason: the index and column of tmp is transposed when there is only one row
        if tmp.shape[0] == 1 or tmp.shape[1] == 1:
            tmp = tmp.transpose()
        # print(tmp.loc[tmp["End"] == str(end_vertex[i])].get(P[j]))
        # If there is a cost, then the link can transport the product
        if tmp.loc[tmp["End"] == str(end_vertex[i])].get(P[j]).iloc[0] > 1e-6:
            links_with_products.append((str(start_vertex[i]), str(end_vertex[i]), str(P[j])))
            cost.append(tmp.loc[tmp["End"] == str(end_vertex[i])].get(P[j]).iloc[0])
            if str(end_vertex[i]) == "Customer":
                links_with_customer.append((str(start_vertex[i]), str(end_vertex[i]), str(P[j])))
                price.append(tmp.loc[tmp["End"] == str(end_vertex[i])].get(P[j]).iloc[0] * 1.5)
        # print(cost)

# (vertex, product)
vertices_with_products = []
for v in vertices:
    for p in P:
        vertices_with_products.append((v, p))


#### Build the model
model = gp.Model('FordSupplyNetwork-CentralizedModel')

# Decision variables

# The flow rate at each link for each product from start vertex to end vertex
y = model.addVars(links_with_products, vtype=GRB.INTEGER, name="flow")
# Inventory at each vertex for each product
I = model.addVars(vertices_with_products, vtype=GRB.INTEGER, name="inventory")
# I_diff = model.addVars(vertices_with_products, vtype=GRB.INTEGER, name="inventory_diff")
# The added capacity at each link for each product from start vertex to end vertex
Q = model.addVars(links, vtype=GRB.INTEGER, name="added_capacity")
# The binary variable for each link to indicate the link is used
z = model.addVars(links, vtype=GRB.BINARY, name="link_use")
# The binary variable for each vertex to indicate the vertex is used
zeta_p = model.addVars(vertices_with_products, vtype=GRB.BINARY, name="v_use_production")
# The binary variable for each vertex to indicate the vertex is used
zeta_I = model.addVars(vertices, vtype=GRB.BINARY, name="v_use_invertory")
# The production unit for each product at each vertex
a = model.addVars(vertices_with_products, vtype=GRB.INTEGER, name="production")
# # The multiplication of the binary variables that shows the used link and associated vertices
# mul1 = model.addVars(links, vtype=GRB.INTEGER, name="multiplication1")
# mul2 = model.addVars(links, vtype=GRB.INTEGER, name="multiplication2")

#### Objective function
# total_cost = model.setObjective(gp.quicksum(cost[i] * y[links_with_products[i]] for i in range(len(links_with_products)))
#                                 + gp.quicksum(z[links[i]] * f.iloc[i, 1] + Q[links[i]] * c_Q.iloc[i, 1]
#                                               for i in range(len(links)))
#                                 + gp.quicksum(gp.quicksum(zeta_p[(v, p)] * phi_p.loc[v, p] for p in P) +
#                                               zeta_I[v] * phi_I.loc[v, 'phiI'] for v in vertices)
#                                 + gp.quicksum(c_a.loc[v, p] * a[(v, p)] for v in vertices for p in P), GRB.MINIMIZE)
total_cost = model.setObjective(gp.quicksum(price[i] * y[links_with_customer[i]] for i in range(len(links_with_customer)))
                                - (gp.quicksum(cost[i] * y[links_with_products[i]] for i in range(len(links_with_products)))
                                + gp.quicksum(z[links[i]] * f.iloc[i, 1] + Q[links[i]] * c_Q.iloc[i, 1]
                                              for i in range(len(links)))
                                + gp.quicksum(gp.quicksum(zeta_p[(v, p)] * phi_p.loc[v, p] for p in P) +
                                              zeta_I[v] * phi_I.loc[v, 'phiI'] for v in vertices)
                                + gp.quicksum(c_a.loc[v, p] * a[(v, p)] for v in vertices for p in P)), GRB.MAXIMIZE)
#### Constraints

# Flow balance at each vertex for each product

# flow_balance_constrs = model.addConstrs((gp.quicksum(y.select(v, '*', p))
#                                          - gp.quicksum(y.select('*', v, p))
#                                          == d.loc[v, p] + I_o.loc[v, p] - I[(v, p)]
#                                  for v in vertices
#                                  for p in P), name="flow_balance")

# Flow balance at each vertex for each product

# flow_balance_constrs = model.addConstrs((gp.quicksum(y.select(v, '*', p)) + sum(r.loc[p, k] * a[(v, k)] for k in N[p])
#                                          - gp.quicksum(y.select('*', v, p)) - a[(v, p)]
#                                          == d.loc[v, p] + I_o.loc[v, p] - I[(v, p)]
#                                          for v in vertices
#                                          for p in P), name="flow_balance")
flow_balance_constrs = model.addConstrs((gp.quicksum(y.select(v, '*', p)) + sum(r.loc[p, k] * a[(v, k)] for k in N[p])
                                         - gp.quicksum(y.select('*', v, p)) - a[(v, p)]
                                         == d.loc[v, p]
                                         for v in vertices
                                         for p in P), name="flow_balance")

# Flow on each link by its capacity
# used_binary_constrs_1 = model.addConstrs((mul1[links[i]] == zeta[links[i][0]] * zeta[links[i][1]]
#                                           for i in range(len(links))), name="used_v")
# used_binary_constrs_2 = model.addConstrs((mul2[links[i]] == z[links[i]] * mul1[links[i]]
#                                           for i in range(len(links))), name="used_l")
link_capacity_constrs = model.addConstrs((gp.quicksum(y.select(u.index[i], u.iloc[i, 0], '*'))
                                          <= (u.iloc[i, 1] + Q[links[i]]) * z[links[i]]
                                          for i in range(len(links))), name="link_capacity")

# Production and inventory cannot exceed limit
a_constrs = model.addConstrs((a[(v, p)] <= a_bar.loc[v,p] * zeta_p[(v, p)]
                              for v in vertices for p in P), name="a_capacity")


I_constrs = model.addConstrs((gp.quicksum(y.select(v, '*', '*')) <= I_bar.loc[v,"Ibar"] * zeta_I[v] for v in vertices), name="I_used")
# I_constrs = model.addConstrs((gp.quicksum(I_o.loc[v, p] - I[(v, p)] for p in P) <= I_bar.loc[v,"Ibar"] * zeta_I[v]
#                               for v in vertices), name="I_used")

# Positive constraints for parameters
y_positive_constrs = model.addConstrs((y.select(l)[0] >= 0.0
                                       for l in links_with_products), name="y_positive")

I_positive_constrs = model.addConstrs((I[v_p] >= 0.0
                                       for v_p in vertices_with_products), name="I_positive")

Q_positive_constrs = model.addConstrs((Q[l] >= 0.0
                                       for l in links), name="Q_positive")

# Production constraints
production_constrs = model.addConstrs((a[(v, p)] <= (gp.quicksum(y.select('*', v, k)) + I_o.loc[v, k]) / r.loc[k, p]
                                       for v in vertices
                                       for p in P
                                       for k in M[p]), name="production")
# Not use backup
# newlink_novertex = [("Steel supplier2", "Transmission OEM")]
# zetap_zero_constrs2 = model.addConstrs((zeta_p[v] == 0 for v in ["Steel supplier2", "Steel supplier"]), name="zp_zero2")

## comment this for only allowing new links
# z_zero_constrs1 = model.addConstrs((z[l] == 0 for l in E_a if l in newlink_novertex), name="z_zero1")
#
# ## comment these for only allowing new vertex and connected links
# zetap_zero_constrs = model.addConstrs((zeta_p[v] == 0 for v in V_a), name="zp_zero")
# zetaI_zero_constrs = model.addConstrs((zeta_I[v] == 0 for v in V_a), name="zI_zero")
# z_zero_constrs2 = model.addConstrs((z[l] == 0 for l in E_a if l not in newlink_novertex), name="z_zero2")

## uncomment this for remove vertex and connected links
# remove_vertex = ["Transmission OEM"]
# z_zero_constrs3 = model.addConstrs((z[l] == 0 for l in links if l[0] in remove_vertex or l[1] in remove_vertex), name="z_zero")


# z_zero_constrs = model.addConstrs((z[l] == 0 for l in E_a), name="z_zero1")
# zetap_zero_constrs = model.addConstrs((zeta_p[(v,p)] == 0 for v in V_a for p in P), name="zp_zero")
# zetaI_zero_constrs = model.addConstrs((zeta_I[v] == 0 for v in V_a), name="zI_zero")


model.setParam("Presolve", 0)

#### Optimization
model.optimize()

#### Diagnose
removed_constrs = []
while model.status != GRB.OPTIMAL:
    model.computeIIS()
    # Print the violated constraints
    for c in model.getConstrs():
        if c.IISConstr:
            print("Violated constraints: ", c)
            removed_constrs.append(str(c))
            model.remove(c)
            break
    model.optimize()
if len(removed_constrs) != 0:
    print("Following constraints are removed: ", removed_constrs)
# model.feasRelaxS(0, True, False, True)


#### Output
# Flow y
product_flow = pd.DataFrame(columns = P, index = pd.MultiIndex.from_tuples(links, names=('start', 'end')))
print("The non-zero product flows are")
n_y = 0
for l_p in links_with_products:
    l = (l_p[0], l_p[1])
    product_flow.loc[l, str(l_p[2])] = y[l_p].x
    if y[l_p].x > 1e-6:
        n_y += 1
        print(str(l), "for product", str(l_p[2]), ":",  y[l_p].x)
print("Number of flow is: ", n_y)

# Inventory I
inventory = pd.DataFrame(columns = P, index = vertices)
print("The non-zero inventory is")
for v_p in vertices_with_products:
    inventory.loc[v_p[0], v_p[1]] = I[v_p].x
    if I[v_p].x > 1e-6:
        print(str(v_p),":",  I[v_p].x)

# Added capacity Q
added_capacity = pd.DataFrame(columns = ["Q"], index = pd.MultiIndex.from_tuples(links, names=('start', 'end')))
n_Q = 0
print("The non-zero added capacity is")
for l in links:
    added_capacity.loc[l,"Q"] = Q[l].x
    if Q[l].x > 1e-6:
        n_Q += 1
        print(str(l), ":",  Q[l].x)
print("Number of links that added capacity is: ", n_Q)

# Production p*L
production = pd.DataFrame(columns = P, index = vertices)
n_p = 0
print("The non-zero production is")
for v_p in vertices_with_products:
    production.loc[v_p[0], v_p[1]] = a[v_p].x
    if a[v_p].x > 1e-6:
        n_p += 1
        print(str(v_p),":",  a[v_p].x)
print("Number of vertices for production is: ", n_p)

# Used links
used_links = pd.DataFrame(columns = ["uselink"], index = pd.MultiIndex.from_tuples(links, names=('start', 'end')))
n_l = 0
print("The used links are")
for l in links:
    used_links.loc[l,"uselink"] = z[l].x
    if z[l].x > 1e-6:
        n_l += 1
        print(str(l), ":",  z[l].x)
print("Number of used links is: ", n_l)

# Used vertices (Have issue with the raw material supplier)
used_verticesI = pd.DataFrame(columns = ["usevI"], index = vertices)
n_vI = 0
print("The vertices whose inventory are used are")
for v in vertices:
    used_verticesI.loc[v,"usevI"] = zeta_I[v].x
    if zeta_I[v].x > 1e-6:
        n_vI += 1
        print(str(v), ":",  zeta_I[v].x)
used_verticesP = pd.DataFrame(columns = P, index = vertices)
print("Number of used vertices for inventory is: ", n_vI)

n_vP = 0
print("The vertices used for production are")
for v_p in vertices_with_products:
    used_verticesP.loc[v_p[0], v_p[1]] = zeta_p[(v_p[0], v_p[1])].x
    if zeta_p[(v_p[0], v_p[1])].x > 1e-6:
        n_vP += 1
        print(str(v_p[0]), ":",  zeta_p[(v_p[0], v_p[1])].x)
print("Number of used vertices for production is: ", n_vP)

# Cost output
# Flow cost
print("The flow cost is: ", gp.quicksum(cost[i] * y[links_with_products[i]].x for i in range(len(links_with_products))))
# Cost of using links and added capacity
print("The cost of using links is: ", gp.quicksum(z[links[i]].x * f.iloc[i, 1] for i in range(len(links))))
print("The cost of added capacity is: ", gp.quicksum(Q[links[i]].x * c_Q.iloc[i, 1] for i in range(len(links))))
print("The cost of links is: ", gp.quicksum(z[links[i]].x * f.iloc[i, 1] + Q[links[i]].x * c_Q.iloc[i, 1]
                                              for i in range(len(links))))
# Cost of using vertices
print("The cost of using vertices is: ", gp.quicksum(gp.quicksum(zeta_p[(v, p)].x * phi_p.loc[v, p] for p in P) +
                                              zeta_I[v].x * phi_I.loc[v, 'phiI'] for v in vertices))
# Cost of production
print("The cost of production is: ", gp.quicksum(c_a.loc[v, p] * a[(v, p)].x for v in vertices for p in P))
# print("The cost of car production is: ", gp.quicksum(c_a.loc[v, 'Car'] * a[(v, 'Car')].x for v in vertices))
# print("The cost of gown is: ", gp.quicksum(c_a.loc[v, 'Gown'] * a[(v, 'Gown')].x for v in vertices))
# print("The cost of ventilator is: ", gp.quicksum(c_a.loc[v, 'Ventilator'] * a[(v, 'Ventilator')].x for v in vertices))

#### Network visualization
G = nx.DiGraph()
G.add_nodes_from(vertices)
G.add_edges_from(links)
# for v in vertices:
#     for k in P:
#         G.nodes[v]["d" + str(k)] = d.loc[v, k]
#         G.nodes[v]["I" + str(k)] = inventory.loc[v, k]

nx.draw(G, with_labels=True)

