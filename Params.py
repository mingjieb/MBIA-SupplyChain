import gurobipy as gp
import pandas as pd
import math


class ParamDict(dict):
    # def __init__(self, *args, **kwargs):
    #     self.default = kwargs.pop('default', 0.0)
    #     super().__init__(*args, **kwargs)

    # Usage: param = ParamDict({index: value}, default=float('inf'));
    #        for any index such that the parameter is not specified, the default value is assigned to it;
    #        'default' should be set 0.0  of float('inf') depending on application;
    #        e.g., default = 0.0 for link capacity or float('inf') for link cost that both indicates infeasibility.
    def __init__(self, *args, default=0.0):
        self.default = default
        super().__init__(*args)

    # Effect: get the value of the parameter for given indices;
    #         if no value is associated with the provided indices,
    #         then get the predefined default value
    def get(self, key):
        return super().get(key, self.default)

    def __getitem__(self, key):
        return super().get(key, self.default)


class Params:
    def __init__(self):

        # file name
        parameter_file = "Parameters/Parameter_ToyCaseStudy3.xlsx"

        # product set
        self.K = list(pd.read_excel(parameter_file, sheet_name = 'd', index_col = 0).columns)

        # vertices
        self.V = list(pd.read_excel(parameter_file, sheet_name = 'd', index_col = 0).index)

        # links, mixed-flow capacity, and fixed link cost
        self.E, self.u, self.f = self.pdDFToMultidict_l(parameter_file, 'uf')

        # demand (negative; indexed by vertex x product)
        self.d = ParamDict(self.pdDFToDict_v_k(parameter_file, 'd'),
                           default=-0.0)

        # revenue (indexed by vertex x product)
        self.Pi = ParamDict(self.pdDFToDict_v_k(parameter_file, 'Pi'),
                            default=0.0)

        # transport cost (indexed by source_vertex x dest_vertex x product)
        self.c = ParamDict(self.pdDFToDict_l_k(parameter_file, 'c'),
                           default=0.0)

        # production rate (indexed by vertex x product)
        # set default to 0 for all vertex i that does not produce some product k
        self.p = ParamDict(self.pdDFToDict_v_k(parameter_file, 'p'),
                           default=0.0)

        # mixed-product maximum run length (indexed by vertex)
        # set default to float('inf') to indicate unrestricted production
        self.Lmax = ParamDict(self.pdDFToDict_v_k(parameter_file, 'Lmax'),
                              default=0.0)

        # production cost (indexed by vertex x product)
        self.e = ParamDict(self.pdDFToDict_v_k(parameter_file, 'e'),
                           default=0.0)

        # product conversion rate (r unit of product k to produce 1 unit of product k')
        self.r = ParamDict(self.pdDFToDict_k_k(parameter_file, 'r'),
                           default=0.0)

        # fixed production line opening cost (indexed by vertex)
        self.phi = ParamDict(self.pdDFToDict_v_k(parameter_file, 'phi'),
                             default=0.0)

        # initial inventory (vertex x product)
        self.I_0 = ParamDict(self.pdDFToDict_v_k(parameter_file, 'I_0'),
                             default=0.0)

        # safety target inventory (vertex x product)
        self.I_s = ParamDict(self.pdDFToDict_v_k(parameter_file, 'I_s'),
                             default=0.0)

        # holding cost (vertex x product)
        self.h = ParamDict(self.pdDFToDict_v_k(parameter_file, 'h'),
                           default=0.0)

        # penalty cost for demand (vertex x product)
        self.rho_d = ParamDict(self.pdDFToDict_v_k(parameter_file, 'rho_d'),
                               default= 0.0)

        # penalty cost for inventory (vertex x product)
        self.rho_I = ParamDict(self.pdDFToDict_v_k(parameter_file, 'rho_I'),
                               default=0.0)

    # transfer pd dataframe to dictionary (vertex x product)    
    def pdDFToDict_v_k(self, file, sheet):
        pdDF = pd.read_excel(file, sheet_name = sheet, index_col = 0)
        var_dict = {}
        for v in list(pdDF.index):
            for k in list(pdDF.columns):
                if not math.isnan(pdDF.loc[v, k]):
                    var_dict[tuple((v, k))] = pdDF.loc[v, k]
        return var_dict

    # transfer pd dataframe to dictionary (source_vertex x dest_vertex x product)
    def pdDFToDict_l_k(self, file, sheet):
        pdDF = pd.read_excel(file, sheet_name = sheet, index_col = 0)
        var_dict = {}
        for i in range(len(list(pdDF.index))):
            source_vertex = pdDF.index[i]
            dest_vertex = pd.DataFrame(pdDF.iloc[[0]])['dest'].iloc[0]
            for k in list(pd.DataFrame(pdDF.iloc[[0],1:]).columns):
                c = pd.DataFrame(pdDF.iloc[[0]])[k].iloc[0]
                if not math.isnan(c):
                    var_dict[tuple((source_vertex, dest_vertex, k))] = c
        return var_dict

    # transfer pd dataframe to Multidictionary (source_vertex x dest_vertex)
    def pdDFToMultidict_l(self, file, sheet):
        pdDF = pd.read_excel(file, sheet_name = sheet, index_col = 0)
        var_dict = {}
        for i in range(len(list(pdDF.index))):
            source_vertex = pdDF.index[i]
            dest_vertex = pd.DataFrame(pdDF.iloc[[0]])['dest'].iloc[0]
            params = []
            # p: all the parameters in the multidict
            for p in list(pd.DataFrame(pdDF.iloc[[0],1:]).columns):
                params.append(pd.DataFrame(pdDF.iloc[[0]])[p].iloc[0])
            var_dict[tuple((source_vertex, dest_vertex))] = params
        var_dict = gp.multidict(var_dict)
        return var_dict

    # transfer pd dataframe to dictionary (product x product)
    def pdDFToDict_k_k(self, file, sheet):
        pdDF = pd.read_excel(file, sheet_name = sheet, index_col = 0)
        var_dict = {}
        for k in list(pdDF.index):
            for k1 in list(pdDF.columns):
                if not math.isnan(pdDF.loc[k, k1]):
                    var_dict[tuple((k, k1))] = pdDF.loc[k, k1]
        return var_dict

        ####### Previous version

        # # product range
        # self.K = ['car', 'transmission', 'engine']

        # # vertices
        # self.V = ['Car', 'Dl1', 'Dl2', 'Tm2', 'Eg2']

        # param_link = ['u', 'f']
        # # links, mixed-flow capacity, and fixed link cost
        # self.E, self.u, self.f = gp.multidict({
        #     ('Tm2', 'Car'): [100, 1],
        #     ('Eg2', 'Car'): [100, 1],
        #     ('Car', 'Dl1'): [100, 1],
        #     ('Car', 'Dl2'): [100, 1]
        # })

        # # demand (negative; indexed by vertex x product)
        # self.d = ParamDict({
        #     ('Dl1', 'car'): -15,
        #     ('Dl2', 'car'): -10},
        #     default=-0.0)

        # # revenue (indexed by vertex x product)
        # self.Pi = ParamDict({
        #     ('Dl1', 'car'): 100,
        #     ('Dl2', 'car'): 150},
        #     default=0.0)

        # # transport cost (indexed by source_vertex x dest_vertex x product)
        # self.c = ParamDict({
        #     ('Car', 'Dl1', 'car'): 10,
        #     ('Car', 'Dl2', 'car'): 10,
        #     ('Tm2', 'Car', 'transmission'): 2,
        #     ('Eg2', 'Car', 'engine'): 2},
        #     default=0.0)

        # # production rate (indexed by vertex x product)
        # # set default to 0 for all vertex i that does not produce some product k
        # self.p = ParamDict({
        #     ('Car', 'car'): 1,
        #     ('Tm2', 'transmission'): 10,
        #     ('Eg2', 'engine'): 6},
        #     default=0.0)

        # # mixed-product maximum run length (indexed by vertex)
        # # set default to float('inf') to indicate unrestricted production
        # self.Lmax = ParamDict({
        #     'Car': 24,
        #     'Tm2': 24,
        #     'Eg2': 24},
        #     default=0.0)

        # # production cost (indexed by vertex x product)
        # self.e = ParamDict({
        #     ('Car', 'car'): 10,
        #     ('Tm2', 'transmission'): 5,
        #     ('Eg2', 'engine'): 5},
        #     default=0.0)

        # # product conversion rate (r unit of product k to produce 1 unit of product k')
        # self.r = ParamDict({
        #     ('transmission', 'car'): 3,
        #     ('engine', 'car'): 4},
        #     default=0.0)

        # # fixed production line opening cost (indexed by vertex)
        # self.phi = ParamDict({
        #     'Car': 1,
        #     'Tm2': 1,
        #     'Eg2': 1},
        #     default=0.0)

        # # initial inventory (vertex x product)
        # self.I_0 = ParamDict({
        #     ('Car', 'car'): 2,
        #     ('Tm2', 'transmission'): 0,
        #     ('Eg2', 'engine'): 0},
        #     default=0.0)

        # # safety target inventory (vertex x product)
        # self.I_s = ParamDict({
        #     ('Car', 'car'): 2,
        #     ('Tm2', 'transmission'): 5,
        #     ('Eg2', 'engine'): 5},
        #     default=0.0)

        # # holding cost (vertex x product)
        # self.h = ParamDict({
        #     ('Car', 'car'): 5,
        #     ('Tm2', 'transmission'): 2,
        #     ('Eg2', 'engine'): 1},
        #     default=0.0)

        # # penalty cost for demand (vertex x product)
        # self.rho_d = ParamDict({
        #     ('Dl1', 'car'): 100,
        #     ('Dl1', 'car'): 100},
        #     default= 0.0)

        # # penalty cost for inventory (vertex x product)
        # self.rho_I = ParamDict({
        #     ('Car', 'car'): 5,
        #     ('Tm2', 'transmission'): 5,
        #     ('Eg2', 'engine'): 5},
        #     default=0.0)

