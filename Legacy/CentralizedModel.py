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
import time
import os


class Params:
    def __init__(self,filename, scid=0):
        self.V, self.E, self.K = (set() for i in range(3))
        self.c, self.due_date = (type(None)() for i in range(2))
        self.info = {}
        self.d  = {(v, k): 0 for v in self.V for k in self.K}
        self.st = {(v, k): 0 for v in self.V for k in self.K}
        self.stageTypes = ['Manuf', 'Part']
        self.instantiated = False
        self._disabled_V = set()
        self._disabled_E = set()
        self.G = nx.DiGraph(rankdir='LR')
        self.G.add_nodes_from(self.V)
        self.G.add_edges_from(self.E)
        self.read_msom(filename=filename,scid=scid)
        

    def read_msom(self, filename,  scid=0):
        data = pd.read_excel(filename, sheet_name='Agent', index_col=[0,1]).sort_index()
        stageCost = data['ProductionCost'].sort_index()

        self.info['depth'] = data['Level']

        self.V = set(data.index.get_level_values('AgentName'))
        self.K = set(data.index.get_level_values('ProductType'))
        self.info['demand'] = data.loc[pd.notna(data['Demand'])]
        self.info['prodLine'] = data.index.tolist()

        self.link = pd.read_excel(filename, sheet_name='Link', index_col=[0, 1])
        self.E = set(self.link.index)
        self.e = {(v, k): stageCost.loc[v, k] for v, k in self.info['prodLine']}
        self.c = {link: self.link.loc[link, 'TransportCost'] for link in self.E}
        self.u = {link: self.link.loc[link, 'TransportCapacity'] for link in self.E}
        self.Lmax = {v: data.loc[v, 'ProductionCapacity'].values[0] for v in self.V}

        conversion = pd.read_excel(filename, sheet_name='ProductStructure', index_col=[1, 0])
        self.r = {pair: conversion.loc[pair] for pair in conversion.index}
        self.info['conversion'] = conversion.reset_index()

        
        ## Parameters for lead time incorporation ##

        #Type of agent
        self.info['V_type'] = data['AgentType'].to_dict()
        self.info['V_type'] = {key[0]: val for key, val in self.info['V_type'].items()}

        nx.set_node_attributes(self.G, self.info['V_type'], name='type')
        nx.set_node_attributes(self.G, self.info['depth'], name='subset')
        
        #leadTime
        self.info['lead_time'] = data['LeadTime'].to_dict()
        self.info['lead_time'] = {key[0]: val for key, val in self.info['lead_time'].items()}
        
        #dueDate
        self.info['due_date'] = data['DueDate'].to_dict()
        self.info['due_date'] = {key[0]: val for key, val in self.info['due_date'].items()}
        

    def get(self, param, index):
        try:
            return getattr(self, param)[index]
            # return float(getattr(my_params, 'r').loc[('rawBeef', 'groundBeef'), :])
        except:
            return 0

    # create the instance from distribution
    def create_instance(self, sample=True):
        for v, k in self.info['prodLine']:
            if (v, k) in self.info['demand'].index:
                self.d[v, k] = int(self.info['demand'].loc[(v, k), 'Demand'])
                # self.d[v, k] = int(self.sample_demand(v, k)) if sample else int(self.info['d_dist'].loc[(v, k), 'avgDemand'])
            else:
                self.d[v, k] = 0
            # self.st[v, k] = np.ceil(self.sample_stageTime(v, k)) if sample else self.info['st_dist'].loc[(v, k), 'stageTime']
        self.instantiated = True
        self.sampled = sample


    def to_json(self):

        data = {
            'V': [v for v in self.V - self._disabled_V],
            'K': [k for k in self.K],
            'E': [[i, j] for i, j in self.E - self._disabled_E],
            'u_mix': [{'index': [i, j], 'value': float(self.u[i, j])} for i, j in self.E - self._disabled_E],
            'u_ind': [{'index': [i, j,k], 'value': float(self.u[i, j])} for i, j in self.E - self._disabled_E for k in self.K],
            'f': [{'index': [i, j,k], 'value': 1e4} for i, j in self.E - self._disabled_E for k in self.K],
            'c': [{'index': [i, j, k], 'value': float(self.c[i, j])} for i, j in self.E - self._disabled_E for k in self.K],
            'phi': [{'index': v, 'value': 1e4} for v in self.V - self._disabled_V],
            'p': [{'index': [v, k], 'value': 1 if (v, k) in self.info['prodLine'] else 0} for v in self.V - self._disabled_V for k in self.K],
            'Lmax': [{'index': v, 'value': int(self.Lmax[v])} for v in self.V - self._disabled_V],
            'e': [{'index': [v, k], 'value': float(self.get('e', (v, k)))} for v in self.V - self._disabled_V for k in self.K],
            'r': [{'index': [k1, k2], 'value': float(self.get('r', (k1, k2)))} for k1 in self.K for k2 in self.K],
            'd': [{'index': [v, k], 'value': -self.d[v, k] if (v, k) in self.info['prodLine'] else 0} for v in self.V - self._disabled_V for k in self.K],
            'h': [{'index': [v, k], 'value': 1} for v in self.V - self._disabled_V for k in self.K],
            'I_0': [{'index': [v, k], 'value': 0} for v in self.V - self._disabled_V for k in self.K],
            'I_s': [{'index': [v, k], 'value': 0} for v in self.V - self._disabled_V for k in self.K],
            'rho_d': [{'index': [v, k], 'value': 1e5} for v in self.V - self._disabled_V for k in self.K],
            'rho_I': [{'index': [v, k], 'value': 1e5} for v in self.V - self._disabled_V for k in self.K],
            'v_type': [{'index': v, 'value':self.info['V_type'][v]} for v in self.V],
            'l': [{'index':[i,j,k],'value':self.info['lead_time'][i]} for i, j in self.E - self._disabled_E for k in self.K],
            't': [{'index': [v, k], 'value': self.info['due_date'][v]} for v in self.V - self._disabled_V for k in self.K],
            'conv':self.info['conversion'].to_dict(),
            'depth':self.info['depth'].reset_index().to_dict()
        }
        with open('data_1new.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)



