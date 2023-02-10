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
    def __init__(self, scid=0):
        self.V, self.E, self.K = (set() for i in range(3))
        self.V_customer = set()
        self.c, self.due_date = (type(None)() for i in range(2))
        self.info = {}
        self.read_msom(scid=scid)
        self.d  = {(v, k): 0 for v in self.V for k in self.K}
        self.st = {(v, k): 0 for v in self.V for k in self.K}
        self.stageTypes = ['Manuf', 'Part']
        self.instantiated = False
        self._disabled_V = set()
        self._disabled_E = set()
        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.V)
        self.G.add_edges_from(self.E)
        nx.set_node_attributes(self.G, self.info['V_type'], name='type')
        nx.set_node_attributes(self.G, self.info['depth'], name='subset')

    def read_msom(self, filename='Distributed/initialization/TASE_Setup.xlsx',  scid=0):
        # filename = 'MSOM-06-038-R2 Data Set in Excel Enhanced.xls'
        # filename = 'Conference Case - New.xlsx'
        # filename = 'Summer Case.xlsx'
        data = pd.read_excel(filename, sheet_name='Agent', index_col=[0, 4]).sort_index()
        stageCost = data['ProductionCost'].sort_index()

        self.info['depth'] = data['Level']
        # self.K = list(set(self.info['depth']))

        self.V = set(data.index.get_level_values('AgentName'))
        self.V_customer = set(v for v in self.V if "Customer" in v)
        self.K = set(data.index.get_level_values('ProductType'))
        self.info['demand'] = data.loc[pd.notna(data['Demand'])]
        # self.info['d_dist'] = data.loc[pd.notna(data['avgDemand']), ['avgDemand', 'stdDevDemand']]
        # self.info['st_dist'] = data[['stageTime', 'stdDev stageTime']]
        self.info['prodLine'] = data.index.tolist()
        # self.due_date = data.loc[pd.notna(data['avgDemand']), 'maxServiceTime']

        self.link = pd.read_excel(filename, sheet_name='Link', index_col=[0, 1])
        # self.E = self.link[['sourceStage', 'destinationStage']].to_records(index=False).tolist()
        self.E = set(self.link.index)
        self.e = {(v, k): stageCost.loc[v, k] for v, k in self.info['prodLine']}
        self.c = {link: self.link.loc[link, 'TransportCost'] for link in self.E}
        self.u = {link: self.link.loc[link, 'TransportCapacity'] for link in self.E}
        self.Lmax = {v: data.loc[v, 'ProductionCapacity'].values[0] for v in self.V}

        conversion = pd.read_excel(filename, sheet_name='ProductStructure', index_col=[1, 0])
        self.r = {pair: conversion.loc[pair] for pair in conversion.index}
        self.info['conversion'] = conversion.reset_index()

        # self.info['pos'] = data[['xPosition', 'yPosition']].apply(tuple, axis=1).to_dict()
        self.info['V_type'] = data['AgentType'].to_dict()
        self.info['V_type'] = {key[0]: val for key, val in self.info['V_type'].items()}

    def to_initializationFiles(self):
        Manuf, Dist, Part, Retail = {}, {}, {}, {}

        conversion = self.info['conversion']
        for node in self.V:
            prodLine = [prod for v, prod in self.info['prodLine'] if v == node]
            production = {
                    prod: {
                        'Cost': float(self.e[node, prod]),
                        'Maximum': float(self.Lmax[node]),
                    }
                    for prod in prodLine
            }

            if self.info['V_type'][node] == 'Manuf':
                for prod in prodLine:
                    production[prod]['Material'] = {
                            up_prod: float(self.r[up_prod, prod])
                            for up_prod in conversion[conversion['downstream'] == prod]['upstream']
                        }
                Manuf[node] = {
                    "Production": production,
                    "Inventory": {
                        prod: 0 for prod in prodLine
                    },
                    "CommunicationNodes": {
                        "Upstream": [u for u, _ in self.G.in_edges(node)],
                        "Downstream": [v for _, v in self.G.out_edges(node)],
                        "Transportation": ["Transportation"],
                    }
                }
            elif self.info['V_type'][node] == 'Part':
                Part[node] = {
                    "Production": production,
                    "Inventory": {
                        prod: 0 for prod in prodLine
                    },
                    "CommunicationNodes": {
                        # "Upstream": [u for u, _ in self.G.in_edges(node)],
                        "Downstream": [v for _, v in self.G.out_edges(node)],
                        "Transportation": ["Transportation"],
                    }
                }
            elif self.info['V_type'][node] == 'Dist':
                Dist[node] = {
                    "Inventory": {
                        prod: 0 for prod in prodLine
                    },
                    "CommunicationNodes": {
                        "Upstream": [u for u, _ in self.G.in_edges(node)],
                        "Downstream": [v for _, v in self.G.out_edges(node)],
                        "Transportation": ["Transportation"],
                    }
                }
            elif self.info['V_type'][node] == 'Retail':
                Retail[node] = {
                    "Demand": {
                        prod: float(self.d[node, prod]) for prod in prodLine
                    },
                    "CommunicationNodes": {
                        "Upstream": [u for u, _ in self.G.in_edges(node)],
                        # "Downstream": [v for _, v in self.G.out_edges(node)],
                        "Transportation": ["Transportation"],
                    }
                }
            else:
                print(f"Unidentified node type for {node}")
                return -1
        for vType in set(self.info['V_type'].values()):
            with open(f'{vType}.json', 'w', encoding='utf-8') as f:
                json.dump(locals()[vType], f, ensure_ascii=False, indent=4)
        return 0

    def get(self, param, index):
        try:
            return getattr(self, param)[index]
            # return float(getattr(my_params, 'r').loc[('rawBeef', 'groundBeef'), :])
        except:
            return 0

    def sample_demand(self, vertex, product):
        try:
            mean = self.info['d_dist'].loc[(vertex, product), 'avgDemand']
            std = self.info['d_dist'].loc[(vertex, product), 'stdDevDemand']
            if pd.isna(std):
                return mean
            return truncnorm.rvs(-mean / std, np.inf, loc=mean, scale=std)
        except:
            return 0

    def sample_cost(self, link):
        mean = self.c[link]
        std = 0.1 * mean
        return truncnorm.rvs(-mean / std, np.inf, loc=mean, scale=std)

    def sample_stageTime(self, vertex, product):
        mean = self.info['st_dist'].loc[(vertex, product), 'stageTime']
        std = self.info['st_dist'].loc[(vertex, product), 'stdDev stageTime']
        if abs(mean) < 1e-9 or pd.isna(mean):
            return 0
        if pd.isna(std):
            # return mean
            std = 0.1 * mean
            return truncnorm.rvs(-mean / std, np.inf, loc=mean, scale=std)
        return truncnorm.rvs(-mean / std, np.inf, loc=mean, scale=std)

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


    def show_graph(self):
        # self.G = nx.Graph()
        # self.G.add_nodes_from(self.V)
        # self.G.add_edges_from(self.E)
        # nx.set_node_attributes(self.G, self.info['V_type'], name='type')

        fig, ax = plt.subplots(dpi=1200)
        cmap = plt.get_cmap()
        ColorLegend = {'Dist': 1, 'Manuf': 2, 'Part': 3, 'Retail': 4}
        values = [ColorLegend[type] for type in nx.get_node_attributes(self.G, 'type').values()]
        cNorm = colors.Normalize(vmin=0, vmax=max(values))
        scalarMap = cm.ScalarMappable(norm=cNorm, cmap=cmap)
        handler = []
        for label in ColorLegend:
            handler.append(
                mlines.Line2D([], [], color=scalarMap.to_rgba(ColorLegend[label]), marker='o', linestyle='None',
                              label=label))
            # ax.plot([0], [0], color=scalarMap.to_rgba(ColorLegend[label]), label=label)

        nx.draw_networkx(self.G,
                         pos=nx.multipartite_layout(self.G),
                         cmap=cmap, vmin=0, vmax=max(values),
                         node_color=values,
                         with_labels=True,
                         node_size=50,
                         font_size=4,
                         ax=ax)
        plt.axis('off')
        plt.legend(handles=handler, loc="lower left", ncol=len(handler))
        fig.tight_layout()
        plt.show()

    def disable(self, vertex_list=[], edge_list=[]):
        self._disabled_V.update(vertex_list)
        for i, j in self.E:
            if i in vertex_list or j in vertex_list:
                self._disabled_E.add((i, j))
        self._disabled_E.update(edge_list)

    def enable(self,  vertex_list=[], edge_list=[]):
        for i, j in edge_list:
            self._disabled_E.discard((i, j))
        for i in vertex_list:
            self._disabled_V.discard(i)
        for i, j in self.E:
            if i in vertex_list or j in vertex_list:
                self._disabled_E.discard((i, j))

    def enable_all(self):
        self._disabled_V = set()
        self._disabled_E = set()

    def to_json(self):
        data = {
            'V': [v for v in self.V - self._disabled_V],
            'V_mfg': [v for v in self.V - self.V_customer - self._disabled_V],
            'K': [k for k in self.K],
            'E': [[i, j] for i, j in self.E - self._disabled_E],
            # 'u': [{'index': [i, j], 'value': 1e6} for i, j in self.E - self._disabled_E],
            'u': [{'index': [i, j], 'value': float(self.u[i, j])} for i, j in self.E - self._disabled_E],
            'f': [{'index': [i, j], 'value': 1} for i, j in self.E - self._disabled_E],
            # 'c': [{'index': [i, j, k], 'value': float(self.sample_cost((i, j)))} for i, j in self.E for k in self.K],
            'c': [{'index': [i, j, k], 'value': float(self.c[i, j])} for i, j in self.E - self._disabled_E for k in self.K],
            'phi': [{'index': v, 'value': 1} for v in self.V - self._disabled_V],
            'p': [{'index': [v, k], 'value': 1 if (v, k) in self.info['prodLine'] else 0} for v in self.V - self._disabled_V for k in
                  self.K],
            # 'Lmax': [{'index': v, 'value': 1e6 if self.info['V_type'][v] in self.stageTypes else 0} for v in self.V - self._disabled_V],
            'Lmax': [{'index': v, 'value': int(self.Lmax[v])} for v in self.V - self._disabled_V],
            'e': [{'index': [v, k], 'value': float(self.get('e', (v, k)))} for v in self.V - self._disabled_V for k in self.K],
            'r': [{'index': [k1, k2], 'value': float(self.get('r', (k1, k2)))} for k1 in self.K for k2 in self.K],
            'd': [{'index': [v, k], 'value': -self.d[v, k]} for v in self.V - self._disabled_V for k in self.K],
            'h': [{'index': [v, k], 'value': 0} for v in self.V - self._disabled_V for k in self.K],
            'I_0': [{'index': [v, k], 'value': 0} for v in self.V - self._disabled_V for k in self.K],
            'I_s': [{'index': [v, k], 'value': 0} for v in self.V - self._disabled_V for k in self.K],
            'rho_d': [{'index': [v, k], 'value': 1e8} for v in self.V - self._disabled_V for k in self.K],
            'rho_I': [{'index': [v, k], 'value': 1e8} for v in self.V - self._disabled_V for k in self.K]
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def network_to_json(self, network, penalty, added_edges=0):
        data = {
            'exist_z': [{'index': [i, j], 'value': int(network['z'][i, j])} for i, j in self.E - self._disabled_E],
            'exist_zeta': [{'index': i, 'value': int(network['zeta'][i])} for i in self.V - self._disabled_V],
            'Rho': penalty,
            'Emax': added_edges
        }
        with open('network.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    sys.path.append('../')
    import pyomoModel

    # generate initial flow
    # comment it when running when enabling disruptions
    # my_params = Params(scid=0)
    # my_params.create_instance(sample=False)
    # my_params.enable_all()
    # my_params.to_json()
    # model = pyomoModel.SinglePeriod()
    # model.create_instance(filenames=['data.json'])
    # model.solve(tee=False)

    # get all the agents that have production
    with open('Distributed/initialization/InitialPlans.json') as f:
        initial_plan = json.load(f)
    agent_with_productions = set()
    for prod in initial_plan['Productions']:
        agent_with_productions.add(prod['Agent'])

    # invoke disable function to run cases with agent loss
    my_params = Params(scid=0)
    my_params.create_instance(sample=False)
    centralized_run_time = {}
    # for agent in agent_with_productions:
    for agent in ["HVAC_sup_3"]:
        my_params.enable_all()

        # uncomment for penalty of adding agents and edges
        my_params.to_json()
        model = pyomoModel.SinglePeriod()
        model.create_instance(filenames=['data.json'])
        model.solve(tee=False)


        my_params.disable(vertex_list=[agent])
        my_params.to_json()

        # no penalty for changing agents and edges
        # model = pyomoModel.SinglePeriod(reschedule=True)
        # model.create_instance(filenames=['data.json'])
        # start_time = time.time()
        # model.solve(tee=False, case_name=agent)
        # end_time = time.time()

        # penalty for changing agents and edges
        network = model.get(["z", "zeta"])
        my_params.network_to_json(network, penalty=1e4)
        model_networkChange = pyomoModel.SinglePeriod(exist_G=True, reschedule=True)
        model_networkChange.create_instance(filenames=['data.json', 'network.json'])
        start_time = time.time()
        model_networkChange.solve(tee=False, case_name=agent)
        end_time = time.time()


        centralized_run_time[agent] = end_time - start_time

    with open("CentralizedResults/runtime.json", 'w', encoding='utf-8') as f:
        json.dump(centralized_run_time, f, ensure_ascii=False, indent=4)


    # network = model.get(["z", "zeta"])

    # print("Disable Part_04")
    # my_params.enable_all()
    # my_params.disable(vertex_list=['Part_04'])
    # my_params.to_json()
    # my_params.network_to_json(network, penalty=1)
    #
    # model_networkChange = pyomoModel.SinglePeriod(exist_G=True)
    # model_networkChange.create_instance(filenames=['data.json', 'network.json'])
    # model_networkChange.solve(tee=False)
