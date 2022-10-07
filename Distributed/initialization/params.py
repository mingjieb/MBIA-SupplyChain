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


class Params:
    def __init__(self, scid=0):
        self.V, self.E, self.K = (set() for i in range(3))
        self.c, self.due_date = (type(None)() for i in range(2))
        self.info = {}
        self.read_msom(scid=scid)
        self.d  = {(v, k): 0 for v in self.V for k in self.K}
        self.st = {(v, k): 0 for v in self.V for k in self.K}
        # self.st = {v: 0 for v in self.V}
        # self.K = ['Product']
        # self.create_instance()
        self.stageTypes = ['Manuf', 'Part']
        self.instantiated = False
        self._disabled_V = set()
        self._disabled_E = set()
        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.V)
        self.G.add_edges_from(self.E)
        nx.set_node_attributes(self.G, self.info['V_type'], name='type')
        nx.set_node_attributes(self.G, self.info['depth'], name='subset')

    def read_msom(self, filename='Conference Case - New.xlsx',  scid=0):
        # filename = 'MSOM-06-038-R2 Data Set in Excel Enhanced.xls'
        # filename = 'Conference Case - New.xlsx'
        # filename = 'Summer Case.xlsx'
        data = pd.read_excel(filename, sheet_name=str(scid).zfill(2) + '_SD', index_col=[0, 1])
        stageCost = data['stageCost']

        self.info['depth'] = data['relDepth']
        # self.K = list(set(self.info['depth']))

        self.V = set(data.index.get_level_values('StageName'))
        self.K = set(data.index.get_level_values('prodType'))
        self.info['d_dist'] = data.loc[pd.notna(data['avgDemand']), ['avgDemand', 'stdDevDemand']]
        self.info['st_dist'] = data[['stageTime', 'stdDev stageTime']]
        self.info['prodLine'] = data.index.tolist()
        self.due_date = data.loc[pd.notna(data['avgDemand']), 'maxServiceTime']

        self.link = pd.read_excel(filename, sheet_name=str(scid).zfill(2) + '_LL', index_col=[0, 1])
        # self.E = self.link[['sourceStage', 'destinationStage']].to_records(index=False).tolist()
        self.E = set(self.link.index)
        self.e = {(v, k): stageCost.loc[v, k] for v, k in self.info['prodLine']}
        self.c = {link: self.link.loc[link, 'transportCost'] for link in self.E}
        self.u = {link: self.link.loc[link, 'transportCap'] for link in self.E}
        self.Lmax = {v: data.loc[v, 'maxProdLength'].values[0] for v in self.V}

        conversion = pd.read_excel(filename, sheet_name=str(scid).zfill(2) + '_R', index_col=[0, 1])
        self.r = {pair: conversion.loc[pair] for pair in conversion.index}
        self.info['conversion'] = conversion.reset_index()

        self.info['pos'] = data[['xPosition', 'yPosition']].apply(tuple, axis=1).to_dict()
        self.info['V_type'] = data['stageClassification'].to_dict()
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
            if (v, k) in self.info['d_dist'].index:
                self.d[v, k] = int(self.sample_demand(v, k)) if sample else int(self.info['d_dist'].loc[(v, k), 'avgDemand'])
            else:
                self.d[v, k] = 0
            self.st[v, k] = np.ceil(self.sample_stageTime(v, k)) if sample else self.info['st_dist'].loc[(v, k), 'stageTime']
        self.instantiated = True
        self.sampled = sample

    # DISABLED BECAUSE OF NEW FEATURES ADDED
    def duplicate_vertex(self, vertex, new_v):
        print("Disabled function.")
        return -1

        if vertex not in self.V:
            raise ValueError("No such vertex exists.")
        if new_v in self.V:
            raise ValueError("Existing vertex name; use a different one.")
        self.V.add(new_v)
        old_E = self.E.copy()
        for i, j in old_E:
            if vertex == i:
                self.E.add((new_v, j))
                self.c[new_v, j] = self.c[i, j]
            elif vertex == j:
                self.E.add((i, new_v))
                self.c[i, new_v] = self.c[i, j]
        self.e[new_v, self.info['prodLine'][vertex]] = self.e[vertex, self.info['prodLine'][vertex]]
        # self.e[new_v, self.info['prodLine'][vertex]] = 0.8
        self.Lmax[new_v] = self.Lmax[vertex]

        self.info['V_type'][new_v] = self.info['V_type'][vertex]
        self.info['pos'][new_v] = (self.info['pos'][vertex][0], min(dict(self.info['pos'].values()).values())-50)

        self.info['st_dist'] = pd.concat([self.info['st_dist'], self.info['st_dist'].loc[[vertex]].rename(index={vertex: new_v})])
        self.info['prodLine'] = pd.concat([self.info['prodLine'], self.info['prodLine'].loc[[vertex]].rename(index={vertex: new_v})])

        if vertex in self.due_date.index:
            self.info['d_dist'] = pd.concat([self.info['d_dist'], self.info['d_dist'].loc[[vertex]].rename(index={vertex: new_v})])
            self.due_date = pd.concat([self.due_date, self.due_date.loc[[vertex]].rename(index={vertex: new_v})])

        if self.instantiated:
            for k in self.K:
                if new_v in self.info['d_dist'].index and self.info['prodLine'].loc[new_v] == k:
                    self.d[new_v, k] = int(self.sample_demand(new_v, k)) if self.sampled else int(
                        self.info['d_dist'].loc[(new_v, k), 'avgDemand'])
                else:
                    self.d[new_v, k] = 0
            self.st[new_v] = np.ceil(self.sample_stageTime(new_v)) if self.sampled else self.info['st_dist'].loc[new_v, 'stageTime']


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
            'K': [k for k in self.K],
            'E': [[i, j] for i, j in self.E - self._disabled_E],
            # 'u': [{'index': [i, j], 'value': 1e6} for i, j in self.E - self._disabled_E],
            'u': [{'index': [i, j], 'value': float(self.u[i, j])} for i, j in self.E - self._disabled_E],
            'f': [{'index': [i, j], 'value': 1e-2} for i, j in self.E - self._disabled_E],
            # 'c': [{'index': [i, j, k], 'value': float(self.sample_cost((i, j)))} for i, j in self.E for k in self.K],
            'c': [{'index': [i, j, k], 'value': float(self.c[i, j])} for i, j in self.E - self._disabled_E for k in self.K],
            'phi': [{'index': v, 'value': 1e-2} for v in self.V - self._disabled_V],
            'p': [{'index': [v, k], 'value': 1 if (v, k) in self.info['prodLine'] else 0} for v in self.V - self._disabled_V for k in
                  self.K],
            # 'Lmax': [{'index': v, 'value': 1e6 if self.info['V_type'][v] in self.stageTypes else 0} for v in self.V - self._disabled_V],
            'Lmax': [{'index': v, 'value': int(self.Lmax[v])} for v in self.V - self._disabled_V],
            'e': [{'index': [v, k], 'value': self.get('e', (v, k))} for v in self.V - self._disabled_V for k in self.K],
            'r': [{'index': [k1, k2], 'value': float(self.get('r', (k1, k2)))} for k1 in self.K for k2 in self.K],
            'd': [{'index': [v, k], 'value': -self.d[v, k]} for v in self.V - self._disabled_V for k in self.K],
            'h': [{'index': [v, k], 'value': 1} for v in self.V - self._disabled_V for k in self.K],
            'I_0': [{'index': [v, k], 'value': 0} for v in self.V - self._disabled_V for k in self.K],
            'I_s': [{'index': [v, k], 'value': 0} for v in self.V - self._disabled_V for k in self.K],
            'rho_d': [{'index': [v, k], 'value': 1e8} for v in self.V - self._disabled_V for k in self.K],
            'rho_I': [{'index': [v, k], 'value': 1e8} for v in self.V - self._disabled_V for k in self.K]
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # print(data_json)

    def network_to_json(self, network, penalty, added_edges=0):
        data = {
            'exist_z': [{'index': [i, j], 'value': int(network['z'][i, j])} for i, j in self.E - self._disabled_E],
            'exist_zeta': [{'index': i, 'value': int(network['zeta'][i])} for i in self.V - self._disabled_V],
            'Rho': penalty,
            'Emax': added_edges
        }
        with open('network.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    sys.path.append('../')
    import pyomoModel
    my_params = Params(scid=0)
    # my_params.duplicate_vertex('Part_10', 'Part_11')
    my_params.create_instance(sample=False)
    my_params.to_initializationFiles()
    # my_params.disable(vertex_list=['Manuf_01'])

    # my_params.show_graph()
    my_params.to_json()
    model = pyomoModel.SinglePeriod()
    model.create_instance(filenames=['data.json'])
    model.solve(tee=False)
    network = model.get(["z", "zeta"])

    print("Disable Part_04")
    my_params.enable_all()
    my_params.disable(vertex_list=['Part_04'])
    my_params.to_json()
    my_params.network_to_json(network, penalty=1)

    model_networkChange = pyomoModel.SinglePeriod(exist_G=True)
    model_networkChange.create_instance(filenames=['data.json', 'network.json'])
    model_networkChange.solve(tee=False)

    print("Disable Part_06")
    my_params.enable_all()
    my_params.disable(vertex_list=['Part_06'])
    my_params.to_json()
    my_params.network_to_json(network, penalty=1)

    model_networkChange = pyomoModel.SinglePeriod(exist_G=True)
    model_networkChange.create_instance(filenames=['data.json', 'network.json'])
    model_networkChange.solve(tee=False)

    print("Disable Part_03")
    my_params.enable_all()
    my_params.disable(vertex_list=['Part_03'])
    my_params.to_json()
    my_params.network_to_json(network, penalty=1)

    model_networkChange = pyomoModel.SinglePeriod(exist_G=True)
    model_networkChange.create_instance(filenames=['data.json', 'network.json'])
    model_networkChange.solve(tee=False)

    print("Disable Part_08")
    my_params.enable_all()
    my_params.disable(vertex_list=['Part_08'])
    my_params.to_json()
    my_params.network_to_json(network, penalty=1)

    model_networkChange = pyomoModel.SinglePeriod(exist_G=True)
    model_networkChange.create_instance(filenames=['data.json', 'network.json'])
    model_networkChange.solve(tee=False)

    print("Disable Manuf_02")
    my_params.enable_all()
    my_params.disable(vertex_list=['Manuf_02'])
    my_params.to_json()
    my_params.network_to_json(network, penalty=1)

    model_networkChange = pyomoModel.SinglePeriod(exist_G=True)
    model_networkChange.create_instance(filenames=['data.json', 'network.json'])
    model_networkChange.solve(tee=False)

    print("Disable Manuf_01")
    my_params.enable_all()
    my_params.disable(vertex_list=['Manuf_01'])
    my_params.to_json()
    my_params.network_to_json(network, penalty=1)

    model_networkChange = pyomoModel.SinglePeriod(exist_G=True)
    model_networkChange.create_instance(filenames=['data.json', 'network.json'])
    model_networkChange.solve(tee=False)

    # print("Add Retail_05 demand")
    # my_params.enable_all()
    # my_params.d['Retail_05', 'marinatedBeef'] = 300
    # my_params.to_json()
    # my_params.network_to_json(network, penalty=1)
    #
    # model_networkChange = pyomoModel.SinglePeriod(exist_G=True)
    # model_networkChange.create_instance(filenames=['data.json', 'network.json'])
    # model_networkChange.solve(tee=True)



    return 0


if __name__ == "__main__":
    main()
# previous version
# # file name
#        parameter_file = "Parameters/Parameter_ToyCaseStudy3.xlsx"
#
#        # product set
#        self.K = list(pd.read_excel(parameter_file, sheet_name='d', index_col=0).columns)
#
#        # vertices
#        self.V = list(pd.read_excel(parameter_file, sheet_name='d', index_col=0).index)
#
#        # links, mixed-flow capacity, and fixed link cost
#        self.E, self.u, self.f = self.pdDFToMultidict_l(parameter_file, 'uf')
#
#        # demand (negative; indexed by vertex x product)
#        self.d = ParamDict(self.pdDFToDict_v_k(parameter_file, 'd'),
#                           default=-0.0)
#
#        # revenue (indexed by vertex x product)
#        self.Pi = ParamDict(self.pdDFToDict_v_k(parameter_file, 'Pi'),
#                            default=0.0)
#
#        # transport cost (indexed by source_vertex x dest_vertex x product)
#        self.c = ParamDict(self.pdDFToDict_l_k(parameter_file, 'c'),
#                           default=0.0)
#
#        # production rate (indexed by vertex x product)
#        # set default to 0 for all vertex i that does not produce some product k
#        self.p = ParamDict(self.pdDFToDict_v_k(parameter_file, 'p'),
#                           default=0.0)
#
#        # mixed-product maximum run length (indexed by vertex)
#        # set default to float('inf') to indicate unrestricted production
#        self.Lmax = ParamDict(self.pdDFToDict_v_k(parameter_file, 'Lmax'),
#                              default=0.0)
#
#        # production cost (indexed by vertex x product)
#        self.e = ParamDict(self.pdDFToDict_v_k(parameter_file, 'e'),
#                           default=0.0)
#
#        # product conversion rate (r unit of product k to produce 1 unit of product k')
#        self.r = ParamDict(self.pdDFToDict_k_k(parameter_file, 'r'),
#                           default=0.0)
#
#        # fixed production line opening cost (indexed by vertex)
#        self.phi = ParamDict(self.pdDFToDict_v_k(parameter_file, 'phi'),
#                             default=0.0)
#
#        # initial inventory (vertex x product)
#        self.I_0 = ParamDict(self.pdDFToDict_v_k(parameter_file, 'I_0'),
#                             default=0.0)
#
#        # safety target inventory (vertex x product)
#        self.I_s = ParamDict(self.pdDFToDict_v_k(parameter_file, 'I_s'),
#                             default=0.0)
#
#        # holding cost (vertex x product)
#        self.h = ParamDict(self.pdDFToDict_v_k(parameter_file, 'h'),
#                           default=0.0)
#
#        # penalty cost for demand (vertex x product)
#        self.rho_d = ParamDict(self.pdDFToDict_v_k(parameter_file, 'rho_d'),
#                               default=0.0)
#
#        # penalty cost for inventory (vertex x product)
#        self.rho_I = ParamDict(self.pdDFToDict_v_k(parameter_file, 'rho_I'),
#                               default=0.0)
#
#
#    # transfer pd dataframe to dictionary (vertex x product)
#    def pdDFToDict_v_k(self, file, sheet):
#        pdDF = pd.read_excel(file, sheet_name=sheet, index_col=0)
#        var_dict = {}
#        for v in list(pdDF.index):
#            for k in list(pdDF.columns):
#                if not math.isnan(pdDF.loc[v, k]):
#                    var_dict[tuple((v, k))] = pdDF.loc[v, k]
#        return var_dict
#
#    # transfer pd dataframe to dictionary (source_vertex x dest_vertex x product)
#    def pdDFToDict_l_k(self, file, sheet):
#        pdDF = pd.read_excel(file, sheet_name=sheet, index_col=0)
#        var_dict = {}
#        for i in range(len(list(pdDF.index))):
#            source_vertex = pdDF.index[i]
#            dest_vertex = pd.DataFrame(pdDF.iloc[[0]])['dest'].iloc[0]
#            for k in list(pd.DataFrame(pdDF.iloc[[0], 1:]).columns):
#                c = pd.DataFrame(pdDF.iloc[[0]])[k].iloc[0]
#                if not math.isnan(c):
#                    var_dict[tuple((source_vertex, dest_vertex, k))] = c
#        return var_dict
#
#    # transfer pd dataframe to Multidictionary (source_vertex x dest_vertex)
#    def pdDFToMultidict_l(self, file, sheet):
#        pdDF = pd.read_excel(file, sheet_name=sheet, index_col=0)
#        var_dict = {}
#        for i in range(len(list(pdDF.index))):
#            source_vertex = pdDF.index[i]
#            dest_vertex = pd.DataFrame(pdDF.iloc[[0]])['dest'].iloc[0]
#            params = []
#            # p: all the parameters in the multidict
#            for p in list(pd.DataFrame(pdDF.iloc[[0], 1:]).columns):
#                params.append(pd.DataFrame(pdDF.iloc[[0]])[p].iloc[0])
#            var_dict[tuple((source_vertex, dest_vertex))] = params
#        var_dict = gp.multidict(var_dict)
#        return var_dict
#
#    # transfer pd dataframe to dictionary (product x product)
#    def pdDFToDict_k_k(self, file, sheet):
#        pdDF = pd.read_excel(file, sheet_name=sheet, index_col=0)
#        var_dict = {}
#        for k in list(pdDF.index):
#            for k1 in list(pdDF.columns):
#                if not math.isnan(pdDF.loc[k, k1]):
#                    var_dict[tuple((k, k1))] = pdDF.loc[k, k1]
#        return var_dict

# class ParamDict(dict):
#     # def __init__(self, *args, **kwargs):
#     #     self.default = kwargs.pop('default', 0.0)
#     #     super().__init__(*args, **kwargs)
#
#     # Usage: param = ParamDict({index: value}, default=float('inf'));
#     #        for any index such that the parameter is not specified, the default value is assigned to it;
#     #        'default' should be set 0.0  of float('inf') depending on application;
#     #        e.g., default = 0.0 for link capacity or float('inf') for link cost that both indicates infeasibility.
#     def __init__(self, *args, default=0.0):
#         self.default = default
#         super().__init__(*args)
#
#     # Effect: get the value of the parameter for given indices;
#     #         if no value is associated with the provided indices,
#     #         then get the predefined default value
#     def get(self, key):
#         return super().get(key, self.default)
#
#     def __getitem__(self, key):
#         return super().get(key, self.default)
