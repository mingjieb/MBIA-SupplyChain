#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

class CapabilityModel():

    def __init__(self):
        # Initialize capability model from initialization file
        self.knowledge = {
            "Production": [],
            "Inventory": [],
            "Transportation": []
        }
        self.characteristics = {
            "Production": {},
            "Inventory": {},
            "Transportation": {}
        }
        # Read initialization file


    # Functions for updating capability model

    def add_capability(self, key, product, info):
        # Add a product type to a capability 'key'
        # info = {"char1": x1, "char2": x2}
        if product not in self.knowledge[key]:
            self.knowledge[key].append(product)
            self.characteristics[key][product] = {}
        for char in info.keys():
            self.characteristics[key][product][char] = info[char]

    def does_need_materials(self):
        # assume all the products that the agent can make need (or do not need) materials
        for product in self.characteristics["Production"].keys():
            if len(self.characteristics["Production"][product]["Material"].keys()) != 0:
                return True
        return False

    def need_materials(self, product, component):

        for product in self.characteristics["Production"].keys():
            if len(self.characteristics["Production"][product]["Material"].keys()) != 0:
                return True
        return False

    def get_capacity(self):
        if len(self.knowledge["Production"]) == 0:
            return 0
        for product in self.characteristics["Production"].keys():
            return self.characteristics["Production"][product]["Capacity"]

    def get_ave_cost(self):
        ave_cost = 0
        for product in self.characteristics["Production"].keys():
            ave_cost += self.characteristics["Production"][product]["Cost"]
        ave_cost /= len(self.characteristics["Production"].keys())
        return ave_cost

    # def remove_capability(self, key, product):
    #     # Remove a product type to a capability 'key'
    #     if product in self.knowledge[key]:
    #         self.knowledge[key].remove(product)
    #     for char in self.characteristics[key].keys():
    #         if product in self.characteristics[key][char].keys():
    #             self.characteristics[key][char].remove(product)

    # def update_characteristic(self, key, product, info):
    #     # Update characteristic for existing product type
    #     # info = {"char1": x1, "char2": x2}
    #     for char in info.keys():
    #         if product in self.characteristics[key][char].keys():
    #             self.characteristics[key][char][product] = info[char]

    # Functions for obtaining information from capability model

    def have_capability(self, key, product):
        # Check whether the agent has capability 'key' for 'product'
        if product in self.knowledge[key]:
            return True
        return False

    def get_characteristic(self, key, product, char):
        # Get the characteristic value for capability 'key' of 'product'
        if key in self.characteristics.keys():
            if product in self.characteristics[key].keys():
                if char in self.characteristics[key][product].keys():
                    return self.characteristics[key][product][char]
        return None

