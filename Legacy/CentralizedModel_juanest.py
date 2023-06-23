import numpy as np
import gurobipy as gp
from gurobipy import GRB
import json
from scipy import stats
from scipy.optimize import curve_fit
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections.abc import MutableMapping

BIGGER_SIZE = 26
plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE-2)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=BIGGER_SIZE-3)    # fontsize of the tick labels
plt.rc('ytick', labelsize=BIGGER_SIZE-3)    # fontsize of the tick labels
plt.rc('legend', fontsize=BIGGER_SIZE-5.5)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

def setup_model(params,ratios,relax,TASE):
    def encode_params(param,override=[]):
        param_dict = {}
        for i in param:
            if type(i['index']) == list:
                index = tuple(i['index'])
            else:
                index = i['index']
            if len(override) == 0: 
                param_dict[index] = i['value']   
            else:
                param_dict[index] = override[0]   
        return param_dict 
    
    def flatten(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, MutableMapping):
                items.extend(flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    m = gp.Model('CentralizedModel_Gurobi')
    #Sets
    m._V = params['V'] #vertices
    m._K = params['K'] #product range
    m._E = [tuple(l) for l in params['E']] #links

    
    ##parameters

    #network flow parameters
    m._q_mix = encode_params(param=params['u_mix']) #Link mixed-product capacity
    m._q_ind = encode_params(param=params['u_ind']) #Capacity of product in link
    m._f = encode_params(param=params['f']) #link cost
    m._c = encode_params(param=params['c']) #transportation cost

    #production parameters
    m._phi = encode_params(param=params['phi']) #production line opening fixed cost
    m._p_cap = encode_params(param=params['p']) #production rate 
    m._p_bar = encode_params(param=params['Lmax']) #production run length capacity
    m._e = encode_params(param=params['e']) #production cost
    m._r = encode_params(param=params['r'])

    #demand/inventory
    m._d = encode_params(param=params['d']) #demand
    m._h = encode_params(param=params['h']) # unit holding cost
    m._I_0 = encode_params(param=params['I_0']) #initial invetory
    m._I_s = encode_params(param=params['I_s']) #safety inventory target

    #penalty
    m._rho_I = encode_params(param=params['rho_I']) #penalty cost for unmet demand
    m._rho_d = encode_params(param=params['rho_d']) #penalty cost for unmet target inventory

    #lead time parameters
    m._l = encode_params(param=params['l']) #leadtime
    m._t = encode_params(param=params['t']) #due date of the agent
    m._bigM = 100 #BigM parameter
    m._LatePenaltyInitial = ratios[1]
    m._LatePenaltySlope = ratios[0]
    m._prods = encode_params(param=params['p']) 

    #Subsets for lead time consideration
    m._V_type = encode_params(param=params['v_type']) #type of each agent
    m._depth = pd.DataFrame(params['depth']).set_index(['AgentName','ProductType'])['Level']
    m._p_type = pd.DataFrame(params['depth']).set_index(['AgentName','ProductType'])['Level']
    #display(m._p_type)
    m._v_subsets = {}
    m._v_subsets['Part'] = []
    m._v_subsets['Manuf'] = []
    m._v_subsets['Dist'] = []
    m._v_subsets['Retail'] = []
    for k,i in m._V_type.items():
        m._v_subsets[i].append(k)

    m._active_prods = {}
    for i in m._V:
        m._active_prods[i] = []
        for k in m._K:
            if m._prods[i,k] == 1:
                m._active_prods[i].append(k)
    
    m._prod_conv = pd.DataFrame(params['conv'])

    #full arc information
    #Encoding arcs information (only valid ones)
    m._arc_subsets = {}
    for tier,lst in m._v_subsets.items():
        m._arc_subsets[tier] = {}
        prod_list = []
        for i,j in m._E:
            if i in lst:
                for k in m._active_prods[i]:
                    if k not in prod_list:
                        m._arc_subsets[tier][k] = []
                        prod_list.append(k)
                    m._arc_subsets[tier][k].append((i,j,k))
    m._valid_arcs = []
    for idx,lst in flatten(m._arc_subsets).items():
        for arc in lst:
            m._valid_arcs.append(arc)
    if TASE == False: ##Fix this ordering thing by changing the parsing of the sheet
        pos_1 = 0
        pos_2 = 1
    else:
        pos_1 = 1
        pos_2 = 0
    m._prod_stucture = {}
    all_prods = []
    for idx,val in m._r.items():
        if val > 0:
            if idx[pos_1] not in all_prods:
                all_prods.append(idx[pos_1])
                m._prod_stucture[idx[pos_1]] = {}
            m._prod_stucture[idx[pos_1]][idx[pos_2]] = val

    m._valid_i_k = []
    for i,prods in m._active_prods.items():
        for k in prods:
            if i in m._v_subsets['Manuf']:
                for kk in m._prod_stucture[k].keys():
                    m._valid_i_k.append((i,kk))
            m._valid_i_k.append((i,k))
    m._valid_i_k = list(set(m._valid_i_k))
    ## variables

    #network flow
    #m._y = m.addVars(m._E,m._K, name='flow') #flow variables
    m._y = m.addVars(m._valid_arcs, name='flow') #flow variables
    #m._beta = m.addVars(m._E,m._K, vtype=GRB.BINARY, name='link_product_usage') #link usage per product
    if relax == True:
        #networkflow,production,late vars
        m._beta = m.addVars(m._valid_arcs, name='link_product_usage',lb=0, ub=1) #link usage per product
        m._zeta = m.addVars(m._V, name='prodLine_usage',lb=0, ub=1) #product line usage
        m._z = m.addVars(m._valid_arcs, name='duedate_exceeded',lb=0, ub=1) #duedate penalty indicator variable
    else:
        m._beta = m.addVars(m._valid_arcs, vtype=GRB.BINARY, name='link_product_usage')
        m._zeta = m.addVars(m._V, vtype=GRB.BINARY, name='prodLine_usage') #product line usage
        m._z = m.addVars(m._valid_arcs,vtype=GRB.BINARY, name='duedate_exceeded') #duedate penalty indicator variable
        
    m._x = m.addVars(m._valid_i_k, name='demand_satisfied',lb=-GRB.INFINITY,ub=0) #unmet demand

    ##Production/inventory variables
    m._p = m.addVars(m._valid_i_k, name='run_length') #run length
    m._I = m.addVars(m._valid_i_k, name='inventory') #inventory

    ##Penalty terms
    m._delta_d = m.addVars(m._valid_i_k, name='penalty_demand') #demand penalty term
    m._delta_I = m.addVars(m._valid_i_k, name='penalty_inv') #inventory penalty term

    
    ##Lead time variables
    #m._a = m.addVars(m._E, m._K, name='arrival_time') #arrival time computation variable
    m._a = m.addVars(m._valid_arcs, name='arrival_time') #arrival time computation variable
    m._o = m.addVars(m._valid_i_k, name='initial_proc_time') #Initial processing time variable
    #m._z = m.addVars(m._E, m._K,vtype=GRB.BINARY, name='duedate_exceeded') #duedate penalty indicator variable
    #m._m_z = m.addVars(m._E, m._K, name='product_z_a') #Variable to compute product between z and a
    m._m_z = m.addVars(m._valid_arcs, name='product_z_a') #Variable to compute product between z and a
    #m._m_beta = m.addVars(m._E, m._K, name='product_beta_o') #Variable to compute product between beta and o
    m._m_beta = m.addVars(m._valid_arcs, name='product_beta_o') #Variable to compute product between beta and o
    #m._w = m.addVars(m._E, m._K, name='total penalty computed') #duedate penalty indicator variable
    m._w = m.addVars(m._valid_arcs, name='total penalty computed') #duedate penalty indicator variable
    
    #Objective function
    m.setObjective(gp.quicksum(m._c[tuple([i,j,k])] * m._y[i,j,k] for i,j,k in m._valid_arcs) +
                        gp.quicksum(m._h[tuple([i,k])] * m._I[i,k] for i,k in m._valid_i_k) +
                        gp.quicksum(m._e[tuple([i,k])] * m._p[i,k] for i,k in m._valid_i_k) +
                        gp.quicksum(m._f[tuple([i,j,k])] * m._beta[i,j,k] for i,j,k in m._valid_arcs) +
                        gp.quicksum(m._phi[i] * m._zeta[i] for i in m._V) + 
                        gp.quicksum( m._rho_I[i, k] * m._delta_I[i, k] for i,k in m._valid_i_k) + 
                        gp.quicksum(m._rho_d[i, k] * m._delta_d[i, k] for i,k in m._valid_i_k ) +
                        gp.quicksum(m._w[i,j,k] for i,j,k in m._valid_arcs)
                        ,GRB.MINIMIZE)

    #Constraints
    
    m.addConstrs(((gp.quicksum(m._y[i,j,k] for _,j,kk in m._valid_arcs if _ == i if kk == k) - gp.quicksum(m._y[j,i,k] for j,_,kk in m._valid_arcs if _ == i if kk == k) 
                    + gp.quicksum( m._r[k,k1]*m._p_cap[i,k1]*m._p[i,k1] for _,k1 in m._valid_i_k if _ == i) - m._p_cap[i,k]*m._p[i,k] 
                    == 
                    m._x[i,k] + m._I_0[i,k]-m._I[i,k]) for i,k in m._valid_i_k)
                    ,'Flow balance constraints')
    
    m.addConstrs((m._y[i,j,k] <= m._q_ind[i,j,k]*m._beta[i,j,k] for i,j,k in m._valid_arcs),name='Link_product_capacity')
    m.addConstrs((gp.quicksum(m._y[i,j,k] for _,__,k in m._valid_arcs if _ == i if __ == j) <= m._q_mix[i,j] for i,j,_ in m._valid_arcs),name='Link_capacity')
    m.addConstrs((gp.quicksum(m._p[i,k] for _,k in m._valid_i_k if _ == i) <= m._p_bar[i]*m._zeta[i] for i,_ in m._valid_i_k),name='production capacity')
    m.addConstrs((m._delta_d[i,k] >= m._x[i,k] - m._d[i,k] for i,k in m._valid_i_k),name='Demand penalty')
    m.addConstrs((m._delta_I[i,k] >= m._I_s[i,k] - m._I[i,k] for i,k in m._valid_i_k),name='Inventory penalty')
    #m.addConstrs((m._x[i,k] >= m._d[i,k] for i,k in m._valid_i_k),name='Demand constraints')
    
    #Lead time variable inclusion
    #including 
    for i in m._V:
        if m._V_type[i] == 'Part':
            for k in m._K:
                if (i,k) in m._valid_i_k:
                    m.addConstr((m._o[i,k] == 0),name='Last tier start time')
    for i,j in m._E:
        #if m._V_type[j] == 'Part':
        #    for k in m._active_prods[j]:
        #        m.addConstr((m._o[j,k] == 0),name='Last tier start time')
                #print(f'o_{j},{k}=0')
        if ((m._V_type[j] == 'Dist') | (m._V_type[j] == 'Retail')):
            for k in m._K:
                if (i,j,k) in m._valid_arcs:
                    if (j,k) in m._valid_i_k:
                        m.addConstr((m._o[j,k] >= m._a[i,j,k]),name='Initial processing time non transformation')
                #print(f'o_{j},{k} >= a_{i},{j},{k} NO transformation involved NO!')
        else:
            for k in m._active_prods[j]:
                for k_sub in m._prod_conv[m._prod_conv['downstream']==k]['upstream']:
                    if (i,j,k_sub) in m._valid_arcs:
                        if (j,k) in m._valid_i_k:
                            m.addConstr((m._o[j,k] >= m._a[i,j,k_sub]),name='Initial processing time transformation')
                    #print(f'o_{j},{k} >= a_{i},{j},{k_sub} transformation involved!')
    
    #linearlizing contraints for product of o and beta: 
    #m.addConstrs((m._a[i,j,k] == (m._l[i,j,k]+m._o[i,k])*m._beta[i,j,k] for i,j,k in m._valid_arcs),name='Arrival time')
    m.addConstrs((m._m_beta[i,j,k] <= m._bigM*m._beta[i,j,k] for i,j,k in m._valid_arcs),name='o_beta_linear1')
    m.addConstrs((m._m_beta[i,j,k] <= m._o[i,k] for i,j,k in m._valid_arcs if (i,k) in m._valid_i_k),name='o_beta_linear2')
    m.addConstrs((m._m_beta[i,j,k] >= m._o[i,k] - ((1-m._beta[i,j,k])*m._bigM) for i,j,k in m._valid_arcs if (i,k) in m._valid_i_k),name='o_beta_linear3')
    m.addConstrs((m._a[i,j,k] == m._l[i,j,k]*m._beta[i,j,k] + m._m_beta[i,j,k] for i,j,k in m._valid_arcs if (i,k) in m._valid_i_k),name='o_beta_linear4')
    
    #m.addConstrs((m._o[j,k] >= m._a[i,j,k] for i,j in m._E if j not in m._v_subsets['Part'] for k in m._K),name='Initial processing time')
    m.addConstrs((m._a[i,j,k] <= m._t[j,k]+(m._bigM*m._z[i,j,k]) for i,j,k in m._valid_arcs),name='DueDate Penalty computation')
    
    #Linearization of constraints for product of a and z
    #m.addConstrs((m._w[i,j,k] == m._z[i,j,k]*(m._LatePenaltyInitial + (m._LatePenaltySlope*(m._a[i,j,k]-m._t[j,k]))) for i,j,k in m._valid_arcs),name='TotalPenaltyComputation')
    m.addConstrs((m._m_z[i,j,k] <= m._bigM*m._z[i,j,k] for i,j,k in m._valid_arcs),name='a_z_linear1')
    m.addConstrs((m._m_z[i,j,k] <= m._a[i,j,k] for i,j,k in m._valid_arcs),name='a_z_linear2')
    m.addConstrs((m._m_z[i,j,k] >= m._a[i,j,k] - ((1-m._z[i,j,k])*m._bigM) for i,j,k in m._valid_arcs),name='a_z_linear3')
    m.addConstrs((m._w[i,j,k] == m._LatePenaltyInitial*m._z[i,j,k] + m._LatePenaltySlope*m._m_z[i,j,k] - m._LatePenaltySlope*m._z[i,j,k]*m._t[j,k] for i,j,k in m._valid_arcs),name='a_z_linear4')
    
    return m

class CentralizedSinglePeriod:
    def __init__(self, params,ratios=[],relax=False,TASE=bool):
        self.results = None
        self.solved = False
        self.m = setup_model(params,ratios,relax,TASE)
        #Setting colormap for style
        self.color_map = {'Vehicle1':'tab:red','Dashboard':'brown','Vehicle2':'tab:blue','PowerTrain1':'orange','Transmission':'tab:green','PowerTrain2':'black'}
    

    def solve(self,disruption_response=False,silent=False):
        self.results = {}
        if silent == False:
            self.m.Params.LogToConsole = 1
        else:
            self.m.Params.LogToConsole = 0
        sc = gp.StatusConstClass
        d = {sc.__dict__[k]: k for k in sc.__dict__.keys() if k[0] >= 'A' and k[0] <= 'Z'}
        self.m.optimize()
        stat = self.m.Status
        if d[stat] == 'OPTIMAL': 
            
            self.y_sol = self.m.getAttr('x',self.m._y)
            self.beta_sol = self.m.getAttr('x',self.m._beta)
            self.x_sol = self.m.getAttr('x',self.m._x)

            self.p_sol = self.m.getAttr('x',self.m._p)
            self.zeta_sol = self.m.getAttr('x',self.m._zeta)
            self.I_sol = self.m.getAttr('x',self.m._I)

            self.delta_d_sol = self.m.getAttr('x',self.m._delta_d)
            self.delta_I_sol = self.m.getAttr('x',self.m._delta_I)

            self.m_beta_sol = self.m.getAttr('x',self.m._beta)
            self.a_sol = self.m.getAttr('x',self.m._a)
            self.o_sol = self.m.getAttr('x',self.m._o)
            self.z_sol = self.m.getAttr('x',self.m._z)

            prodCost = 0
            for i in self.m._V:
                prodCost += self.m._phi[i]*self.zeta_sol[i]
                for k in self.m._K:
                    if (i,k) in self.m._valid_i_k:
                        prodCost += self.m._e[i,k]*self.p_sol[i,k]
            transCost = 0
            for i,j,k in self.m._valid_arcs:
                transCost += self.m._f[i,j,k]*self.beta_sol[i,j,k]
                transCost += self.m._c[i,j,k]*self.y_sol[i,j,k]

            self.prodCost = prodCost
            self.transCost = transCost
            
        elif d[stat] == 'INFEASIBLE' :
            print('Instance reported as infeasible')
            self.m.computeIIS()
            self.m.write("model.ilp")
        else:
            print(d[stat])
        return

    def write_initialPlan(self,filename='InitialPlans.json'):
        initialPlans = {}
        initialPlans['Production cost'] = self.prodCost
        initialPlans['Flow cost'] = self.transCost
        initialPlans['Productions'] = []
        initialPlans['Flows'] = []
        #Production plan writing
        zeta = self.zeta_sol
        p = self.p_sol
        for (i,k),value in p.items():
            if value > 0:
                if zeta[i] > 0:
                    prod_time = self.o_sol[i,k]
                    prod_dict = {'Agent':i,'Product':k,'Value':np.round(value,0),'Prod_time':np.round(prod_time,0)}
                    initialPlans['Productions'].append(prod_dict)
        #Flow plan writing
        y = self.y_sol
        a = self.a_sol
        for (i,j,k),value in y.items():
            if value > 0.5:
                Arr_time = a[i,j,k]
                flow_dict = {'Source':i,'Dest':j,'Product':k,'Value':np.round(value,0),'Arr_time':np.round(Arr_time,0)}
                initialPlans['Flows'].append(flow_dict)
        with open(filename, "w") as outfile:
            json.dump(initialPlans, outfile,indent=4)

    def solution_visualization(self):

        self.linestyle_map = {'Vehicle1':':','Vehicle2':':','PowerTrain1':':','Dashboard':':','PowerTrain2':':','Transmission':':'}


        flow_arcs_color_1 = []
        flow_arcs_1 = []
        flow_arcs_number_1 = []
        flow_arcs_label_1 = {}
        flow_arcs_style_1 = []

        flow_arcs_color_2 = []
        flow_arcs_2 = []
        flow_arcs_number_2 = []
        flow_arcs_label_2 = {}

        ysolkeys = list(self.y_sol.keys())
        nodes_involved = []
        arcs_involved = []
        #print('Edge      | ','Capacity','|','Mixed flow')
        for key,val in self.m._q_mix.items():
            i = key[0]
            j = key[1]
            sum = 0
            for k in self.m._K:
                if (i,j,k) in ysolkeys:
                    sum += self.y_sol[i,j,k]
                    if self.y_sol[i,j,k] > 0:
                        nodes_involved.append(i)
                        nodes_involved.append(j)
                        arcs_involved.append((j,k))
            #print(key,val,'|',sum)
        nodes_involved = list(set(nodes_involved))
        arcs_involved = list(set(arcs_involved))

        used_arcs = []
        for k,i in self.y_sol.items():
            if i > 0:
                if (k[0],k[1]) in used_arcs:
                    flow_arcs_2.append((k[0],k[1]))
                    flow_arcs_number_2.append(i/500)
                    #flow_arcs_color_2.append(self.color_map[k[2]])
                    #text = f'{{{k[0]},{k[1]},{k[2]}}}'
                    #text_time = f'{int(np.round(self.a_sol[k],0))}'
                    #flow_arcs_label_2[(k[0],k[1])]=r'$a_{}={}$'.format(text,text_time)
                else:
                    used_arcs.append((k[0],k[1]))
                    flow_arcs_1.append((k[0],k[1]))
                    flow_arcs_number_1.append(i)
                    #flow_arcs_color_1.append(self.color_map[k[2]])
                    #flow_arcs_style_1.append(self.linestyle_map[k[2]])
                    #text = f'{{{k[0]},{k[1]},{k[2]}}}'
                    #text_time = f'{int(np.round(self.a_sol[k],0))}'
                    #flow_arcs_label_1[(k[0],k[1])]=r'$a_{}={}$'.format(text,text_time)

        o_time_label_1 = {}
        o_time_label_2 = {}
        used_nodes = []
        trivial = False
        '''
        for k,i in self.o_sol.items():
            if k[0] in nodes_involved:
                if trivial == False:
                    if i > 0:
                        if self.m._V_type[k[0]] != 'Retail':
                            if k[0] in used_nodes:
                                text = f'{{{k[0]},{k[1]}}}'
                                text_time = f'{int(np.round(self.o_sol[k],0))}'
                                o_time_label_2[k[0]]=r'$o_{}={}$'.format(text,text_time)
                            else:
                                used_nodes.append(k[0])
                                text = f'{{{k[0]},{k[1]}}}'
                                text_time = f'{int(np.round(self.o_sol[k],0))}'
                                o_time_label_1[k[0]]=r'$o_{}={}$'.format(text,text_time)
        '''
        self.G = nx.DiGraph(rankdir='LR',seed=2)
        self.G.add_nodes_from(self.m._V)
        sol_arcs = []
        for k,i in self.beta_sol.items():
            if i > 0:
                sol_arcs.append((k[0],k[1]))
        self.G.add_edges_from(sol_arcs)
        nx.set_node_attributes(self.G, self.m._V_type, name='type')
        nx.set_node_attributes(self.G, self.m._depth, name='subset')

        self.edge_ptype = {}
        for idx,_ in self.m._l.items():
            self.edge_ptype[idx[0:2]] = idx[-1]

        nx.set_edge_attributes(self.G, self.m._p_type,name='p_type')
        ColorLegend = {'Dist': 'wheat', 'Manuf': 'lightskyblue', 'Part': 'lightsteelblue', 'Retail': 'mistyrose'}
        
        
        nx.set_edge_attributes(self.G, self.edge_ptype, name='ptype')
        
        

        values = [ColorLegend[type] for type in nx.get_node_attributes(self.G, 'type').values()]
        #styles = [linestyle_map[type] for type in nx.get_edge_attributes(self.G, 'p_type').values()]
        for type in nx.get_edge_attributes(self.G, 'p_type').values():
            print(type)
            print('-----')
        plt.figure(figsize=(12,10) )
        pos = nx.nx_agraph.graphviz_layout(self.G, prog="dot")
        #nx.draw_networkx_nodes(Tree_orig, pos,node_size=800 , nodelist=list(final_data[final_data['Qsol']<0.5].index), node_color="green")
        nx.draw(self.G, pos,node_size=4000,width=2,with_labels=True, vmin=1, vmax=max(values),
                                #node_color=values,
                                font_size=15,
                                font_color='k',
                                edge_color='white',
                                arrows=False)
        #Adding first flows
        nx.draw_networkx_edges(
                self.G,
                pos,
                edgelist=flow_arcs_1,
                alpha=1,
                width=flow_arcs_number_1,
                connectionstyle='arc3',
                #style=flow_arcs_style_1
                #edge_color=flow_arcs_color_1,
                #'arc3,rad=0.2'
            )
        #Adding labels of a variable
        '''
        nx.draw_networkx_edge_labels(G, 
                                    pos, 
                                    edge_labels=flow_arcs_label_1, 
                                    label_pos=0.5, 
                                    font_size=7, 
                                    font_color='k',
                                    rotate=True,
                                    verticalalignment='bottom')

        #Adding labels of o variable
        nx.draw_networkx_labels(G, 
                                pos, 
                                labels=o_time_label_1, 
                                font_size=7, 
                                font_color='k', 
                                font_family='sans-serif', 
                                horizontalalignment='left', 
                                verticalalignment='bottom')
        #Adding labels of o variable for possible second output product
        if len(o_time_label_2) > 0:
            nx.draw_networkx_labels(G, 
                                    pos, 
                                    labels=o_time_label_2, 
                                    font_size=7, 
                                    font_color='k', 
                                    font_family='sans-serif', 
                                    horizontalalignment='left', 
                                    verticalalignment='top')
        '''
        #Adding possible secong flow of different product to same node
        if len(flow_arcs_2) > 0:
            nx.draw_networkx_edges(
                    self.G,
                    pos,
                    edgelist=flow_arcs_2,
                    alpha=1,
                    width=flow_arcs_number_2,
                    edge_color=flow_arcs_color_2,
                    connectionstyle='arc3,rad=-0.2'
                )
            #Adding labels of a variable
            '''
            nx.draw_networkx_edge_labels(G, 
                                        pos, 
                                        edge_labels=flow_arcs_label_2, 
                                        label_pos=0.5, 
                                        font_size=7, 
                                        font_color='k',
                                        rotate=True,
                                        verticalalignment='bottom')
            '''
        #plt.title(f'Action space progression over {T-1} periods with {total_states} facilities to build with {count} possible paths',fontsize=15)
        plt.show()
        return        
    def sample_gaussian_trunc(self,lc,uc,mean,sd,n_samples):
        a, b = (lc - mean) / sd, (uc - mean) / sd
        samples = stats.truncnorm.rvs(a, b, size=n_samples,loc=mean)

        #For later, we can save each distribution
        '''
        myclip_a = 0
        myclip_b = 100
        my_mean = 0.5
        my_std = 0.3

        a, b = (myclip_a - my_mean) / my_std, (myclip_b - my_mean) / my_std
        x_range = np.linspace(0,min(myclip_b,0+10),1000)
        plt.plot(x_range, truncnorm.pdf(x_range, a, b, loc = my_mean, scale = my_std),c='k',label='hola')
        plt.legend()
        plt.show()
        '''
        return samples

    def sample_log_norm(self,mean,sd,n_samples):
        samples = stats.lognorm.rvs(s=sd,loc=mean,size=n_samples)

        #For later, we can save each distribution
        '''
        myclip_a = 0
        myclip_b = 100
        my_mean = 0.5
        my_std = 0.3

        a, b = (myclip_a - my_mean) / my_std, (myclip_b - my_mean) / my_std
        x_range = np.linspace(0,min(myclip_b,0+10),1000)
        plt.plot(x_range, truncnorm.pdf(x_range, a, b, loc = my_mean, scale = my_std),c='k',label='hola')
        plt.legend()
        plt.show()
        '''
        return samples

    def TASE_adapt(self):
        SC = self.SC
        V = self.V
        #Checking for entities that are Part vs Manuf (Considering that we have no distributors in this instance)
        downstream = {}
        upstream = {}
        for v in V:
            downstream[v] = []
            upstream[v] = []
        for _,r in SC.iterrows():
            source = r['Source']
            destination = r['Destination']
            downstream[source].append(destination)
            upstream[destination].append(source)
        AgentType = {}
        parts = []#Agents that qualify as parts (they start the SC)
        for idx,upstream_ents in upstream.items():
            if len(upstream_ents) == 0:
                parts.append(idx)
        for v in V:
            if v in parts:
                AgentType[v] = 'Part'
            elif len(downstream[v]) == 0:
                AgentType[v] = 'Retail'
            else:
                AgentType[v] = 'Manuf'
        #Market = pd.read_excel('TASE_Setup.xlsx',sheet_name='Agent')
        #Market['AgentType'] = Market['AgentName'].map(AgentType)
        downstream = {}
        upstream = {}
        for v in V:
            downstream[v] = []
            upstream[v] = []
        for _,r in SC.iterrows():
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

        #seed
        tier = 0
        manuf_groups[0] = []
        for j in manufs:
            upstream_manufs = 0
            for i in upstream[j]:
                if i in manufs:
                    upstream_manufs +=1
            if upstream_manufs == 0:
                manuf_tier[j] = 0
                manuf_groups[0].append(j)
        while len(manuf_set) > 0:
            for i in manuf_groups[tier]:
                for j in downstream[i]:
                    if j in manufs:
                        if tier+1 not in manuf_groups.keys():
                            manuf_groups[tier+1] = []
                        manuf_tier[j] = tier+1
                        manuf_groups[tier+1].append(j)
                if i in manuf_set:
                    manuf_set.remove(i)
            if tier+1 in manuf_groups.keys():
                manuf_groups[tier+1] = list(set(manuf_groups[tier+1]))
            tier += 1
        for manuf,tier in manuf_tier.items():
            self.m._V_type[manuf] = tier
        
        return
    
    def simulate_flows(self,lead_time_instance,id=None):
        #Out of sample testing
        active_flows = {}
        for key,val in self.y_sol.items():
            if val > 0:
                if key not in list(active_flows.keys()):
                    active_flows[key] = {}
                active_flows[key]['flow'] = val
                active_flows[key]['lead_time'] = lead_time_instance[key]

        active_flows = pd.DataFrame(active_flows).T.reset_index()
        active_flows.columns = ['i','j','k','flow','lead_time']
        in_flows = {}
        out_flows = {}
        #simulating flows
        for i in range(len(active_flows)):
                origin = active_flows.iloc[i]['i']
                dest = active_flows.iloc[i]['j']
                prod = active_flows.iloc[i]['k']
                flow = active_flows.iloc[i]['flow']
                l_time = active_flows.iloc[i]['lead_time']

                #Setting up in flow dictionary

                if dest not in list(in_flows.keys()):
                        in_flows[dest] = {}
                if origin not in list(in_flows[dest].keys()):
                        in_flows[dest][origin] = {}
                in_flows[dest][origin][prod] = {}
                in_flows[dest][origin][prod]['flow'] = flow
                in_flows[dest][origin][prod]['lead_time'] = l_time

                #Setting up out flow dictionary
                if origin not in list(out_flows.keys()):
                        out_flows[origin] = {}
                if dest not in list(out_flows[origin].keys()):
                        out_flows[origin][dest] = {}
                out_flows[origin][dest][prod] = {}
                out_flows[origin][dest][prod]['flow'] = flow
                out_flows[origin][dest][prod]['lead_time'] = l_time

                #print('Moving ',flow,' of ',prod,' from: ',origin,' to ',dest, ' with lead time of ',time)

        tier_members = {}
        tiers = ['Part',0,1,2,'Retail']
        for tier in tiers:
            tier_members[tier] = []
        for v,type in self.m._V_type.items():
            tier_members[type].append(v)
        o = {}
        a = {}
        for j,items in in_flows.items():
            for i,info in items.items():
                for k,data in info.items():
                    #if (j,k) not in list(time_computation.keys()):
                    #        time_computation[(j,k)]  = {}
                    a[(i,j,k)] = data['lead_time']
        #Setting incumbent solution
        for part in tier_members['Part']:
                ks = self.m._active_prods[part]
                for k in ks:
                    o[(part,k)] = 0 
        sequence = [0,1,2,'Retail'] #We just need to consider those that take flow
        transformers = [0,1,2] #Considering those vertices that transform 
        active_vertices = in_flows.keys()
        for tier in sequence:
            if tier in transformers:
                for j in tier_members[tier]:
                    if j in active_vertices:
                        for i,info in in_flows[j].items():
                            for k,data in info.items():
                                #if (j,k) not in list(time_computation.keys()):
                                #        time_computation[(j,k)]  = {}
                                a[(i,j,k)] = np.ceil(data['lead_time']) + np.ceil(o[(i,k)])
                        for k in self.m._active_prods[j]:
                            #print('---------')
                            #print(j,k)
                            #print('---------')
                            subproduct_flow_time = []
                            subproduct_flow_id = []
                            subproduct_received = []
                            sub_prods = self.m._prod_conv[self.m._prod_conv['downstream']==k]['upstream'].values
                            #print(k,sub_prods)
                            for i,info in in_flows[j].items():
                                for prod,data in info.items():
                                    if prod in sub_prods:
                                        subproduct_flow_time.append(a[(i,j,prod)])
                                        subproduct_flow_id.append((i,j,prod))
                                        subproduct_received.append(prod)
                                        #print(i,j,prod)
                            
                            if set(sub_prods).issubset(subproduct_received) == True:
                                #print(j,k,subproduct_flow_time,subproduct_flow_id)
                                temp = max(subproduct_flow_time)
                                max_id = np.argmax(subproduct_flow_time)
                                #print(temp,subproduct_flow_id[max_id])
                                o[(j,k)] = temp
            else:
                for j in tier_members[tier]:
                    if j in active_vertices:
                        #print('========')
                        #print(j)
                        #print(in_flows[j])
                        #print('========')
                        for i,info in in_flows[j].items():
                            for k,data in info.items():
                                #if (j,k) not in list(time_computation.keys()):
                                #        time_computation[(j,k)]  = {}
                                a[(i,j,k)] = np.ceil(data['lead_time']) + np.ceil(o[(i,k)])
                                #print(i,j,k,a[i,j,k])
                        for k in self.m._active_prods[j]:
                            #print(j,k)
                            product_flow_time = []
                            product_flow_id = []
                            product_received = []
                            for i,info in in_flows[j].items():
                                for prod,data in info.items():
                                    if prod == k:
                                        product_flow_time.append(a[(i,j,prod)])
                                        product_flow_id.append((i,j,prod))
                                        product_received.append(prod)
                                        #print(i,j,prod)
                            #print(product_flow_id)
                            if len(product_flow_time) > 0:
                                for prod,data in info.items():
                                    temp = max(product_flow_time)
                                    max_id = np.argmax(product_flow_time)
                                    #print(temp,subproduct_flow_id[max_id])
                                    #print('o',j,prod,'agregado!')
                                    o[(j,k)] = temp
            arrival_times = pd.DataFrame({'a':a,'flows':self.y_sol,'Link capacity':self.m._q_ind}).reset_index()
            arrival_times = arrival_times[arrival_times['flows']>1e-10]
        arrival_times.columns = ['i','j','k','time','flow','Link capacity']

        vertex_cap = []
        due_dates = []
        for r in range(len(arrival_times)):
            row = arrival_times.iloc[r]
            i = row['i']
            j = row['j']
            k = row['k']
            vertex_cap.append(self.m._p_bar[i])
            due_dates.append(self.m._t[(j,k)])

        arrival_times['Link utilization'] = arrival_times['flow']/arrival_times['Link capacity']
        arrival_times['Link utilization'] = round(arrival_times['Link utilization'],2)
        arrival_times['Vertex capacity'] = vertex_cap
        arrival_times['Vertex utilization'] = arrival_times['flow']/arrival_times['Vertex capacity']
        arrival_times['Vertex utilization'] = round(arrival_times['Vertex utilization'],2)

        arrival_times = arrival_times[['i','j','k','time','flow','Link utilization','Vertex utilization']]

        arrival_times['due_date'] = due_dates
        arrival_times['lateness'] = arrival_times['time']-arrival_times['due_date']
        arrival_times.loc[arrival_times['lateness'] < 0, 'lateness'] = 0
        arrival_times['Fixed Penalty'] = 0
        arrival_times.loc[arrival_times['lateness'] > 1e-10, 'Fixed Penalty'] = arrival_times['flow']*self.m._LatePenaltyInitial
        arrival_times['lateness'] = np.ceil(arrival_times['lateness']).astype(int)
        arrival_times['Linear Penalty'] = arrival_times['lateness']*arrival_times['flow']*self.m._LatePenaltySlope
        arrival_times['Linear Penalty'] = arrival_times['Linear Penalty'].astype(int)
        arrival_times['Total Penalty'] = arrival_times['Fixed Penalty'] + arrival_times['Linear Penalty']
        arrival_times = arrival_times[['i','j','k','time','flow','lateness','Link utilization','Vertex utilization','Total Penalty']]
        arrival_times = arrival_times.sort_values(by=['time','i','j'])
        if id != None:
            arrival_times['id'] = id
        return arrival_times
    
    def generate_stochastic_leadtime(self,n_samples,disrupted_agents={}):
        disrupted_agents_list = list(disrupted_agents.keys())
        #key_mapper = {'i':0,'j':1,'k':2}

        sampled_scenarios = []
        sampled_scenarios_idx = []

        for idx,mean in self.m._l.items():
            sampled_scenarios_idx.append(idx)
            search_idx = (idx[0],idx[2])

            if (len(disrupted_agents) == 1) & (list(disrupted_agents.keys())[0] == 'All'):
                if disrupted_agents['All'][0] == 'log_norm':
                    samples = self.sample_log_norm(mean=mean,sd=disrupted_agents['All'][1],n_samples=n_samples)
                elif disrupted_agents['All'][0]  == 'gaussian_trunc':
                    agent_info = disrupted_agents['All'][0][1]
                    samples = self.sample_gaussian_trunc(lc=agent_info[0],uc=agent_info[1],mean=mean,sd=agent_info[2],n_samples=n_samples)
                sampled_scenarios.append(samples)
            elif search_idx in disrupted_agents_list: #We are impliying the format of the input here... It could be adaptive.
                if disrupted_agents[search_idx][0] == 'log_norm':
                    samples = self.sample_log_norm(mean=mean,sd=disrupted_agents[search_idx][1],n_samples=n_samples)
                elif disrupted_agents[search_idx][0] == 'gaussian_trunc':
                    agent_info = disrupted_agents[search_idx][1]
                    samples = self.sample_gaussian_trunc(lc=agent_info[0],uc=agent_info[1],mean=mean,sd=agent_info[2],n_samples=n_samples)
                sampled_scenarios.append(samples)
            else:
                samples = np.empty(n_samples, dtype=np.int)
                samples.fill(mean)
                sampled_scenarios.append(samples)     

        self.scenarios = pd.DataFrame(sampled_scenarios,index=sampled_scenarios_idx)

        simulated_results = []
        for s in self.scenarios:
            simulated_results.append(self.simulate_flows(self.scenarios[s],id=s))
        self.df_sim_res = pd.concat(simulated_results)

        return self.df_sim_res,self.scenarios
    
    def condensed_statistics_compare(self,simulations,colors,filename,x_low=2,x_high=12):
        '''
        def func(x, a, b, c):
            return a + b*x + c*x*x # example function
        xData = k_data.index
        yData = k_data.index

        # curve fit the data using curve_fit's default inital parameter estimates
        fittedParameters, pcov = curve_fit(func, xData, yData)

        y_fit = func(xData, *fittedParameters)

        plt.bar(xData, yData) # plot the raw data as bar chart
        plt.plot(xData, y_fit) # plot the equation using the fitted parameters
        '''
        stats = pd.concat(simulations, ignore_index=True)
        stats['Type'] = stats['j'].map(self.m._V_type)
        hist_data = stats[stats['Type']=='Retail']
        #colors = [colors1,colors2]

        ks = hist_data['k'].unique()
        for idx in range(len(ks)):
            k = ks[idx]
            hist_k = hist_data[hist_data['k']==k]
            k_data = hist_k[['lateness','flow','scenario']].groupby(['lateness','scenario']).sum().unstack().fillna(0)
            #display(k_data)
            k_data_idx_exist = list(k_data.index)
            for i in range(x_low,x_high):
                if (i in k_data_idx_exist) == False:
                    dummyrow = pd.DataFrame(k_data.iloc[-1])
                    dummyrow[k_data.index[-1]] = 0
                    dummyrow = dummyrow.T
                    dummyrow.index = [i]
                    k_data = k_data.append(dummyrow)
            k_data.sort_index(inplace=True)
            for c in k_data.columns:
                col = k_data[c]
                sum = col.sum()
                for r in col.index:
                    k_data.loc[r,c] = int(k_data.loc[r,c]/sum*100)
            legends = []
            #colors = ['#FF0000','tab:orange','tab:red','tab:blue']
            hatches = ['*','x','+','O','-','.','|','*','o']
            for l in k_data.columns:
                prod = l[1]
                #colors.append(self.color_map[prod])
                if prod[-1].isnumeric():
                    prod = f'{prod}'
                if prod == '0:0':
                    prod = 'No penalty'
                if prod == '1:1':
                    prod = '1:0'
                legends.append(prod)
                
            ax = plt.figure(figsize=(10, 6)).add_subplot(111)
            
            k_data.plot.bar(ax=ax,stacked=False,color=colors,width=0.8)
            
            n_bars = len(list(k_data['flow'].columns))
            bars = ax.patches
            patterns = hatches[0:n_bars]# set hatch patterns in the correct order
            hatches = []  # list for hatches in the order of the bars
            for h in patterns:  # loop over patterns to create bar-ordered hatches
                for i in range(int(len(bars) / len(patterns))):
                    hatches.append(h)
            for bar, hatch in zip(bars, hatches):  # loop over bars and hatches to set hatches in correct order
                bar.set_hatch(hatch)
        
                #print(i)
                #thisbar.set_hatch(hatches[position])
            plt.xlabel(f'Delivery lateness of {k[:-1]}$_{k[-1]}$ to customers')
            plt.ylabel(r'$\%$ of total flow')
            plt.legend(legends,bbox_to_anchor=(1, 1.25),ncol=n_bars,borderaxespad=0,title='Unit penalty : Fixed penalty',title_fontsize=BIGGER_SIZE-4)
            plt.xticks(rotation=0)
            plt.yticks([0,20,40,60])
            plt.savefig(f'{filename}.pdf',bbox_inches='tight')
            plt.show()

        return k_data