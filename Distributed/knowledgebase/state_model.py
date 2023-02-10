#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

class StateModel():

    def __init__(self):
        self.inflow = {}
        self.outflow = {}
        self.inventory = {}
        self.production = {}
        self.over_production = {}

    def update_prod_inv(self, key, product, change):
        # if key == "inventory":
        #     self.inventory[product] = amount
        #     if amount - 0 < 0.01:
        #         self.inventory.pop(product)
        if key == "production":
            try:
                self.production[product] += change
            except:
                self.production[product] = change
            if self.production[product] - 0 < 0.1:
                self.production.pop(product)

    def update_flow(self, key, agent, product, change):
        if key == "inflow":
            try:
                self.inflow[(agent, product)] += change
            except:
                self.inflow[(agent, product)] = change
            if self.inflow[(agent, product)] - 0 < 0.1:
                self.inflow.pop((agent, product))
        if key == "outflow":
            try:
                self.outflow[(agent, product)] += change
            except:
                self.outflow[(agent, product)] = change
            if self.outflow[(agent, product)] - 0 < 0.1:
                self.outflow.pop((agent, product))

    def update_over_prod(self, key, product, change):
        # if key == "inventory":
        #     self.inventory[product] = amount
        #     if amount - 0 < 0.01:
        #         self.inventory.pop(product)
        if key == "production":
            try:
                self.over_production[product] += change
            except:
                self.over_production[product] = change
            if self.over_production[product] - 0 < 0.1:
                self.over_production.pop(product)


    def clear_state(self):
        self.inflow.clear()
        self.outflow.clear()
        self.inventory.clear()
        self.production.clear()
        self.over_production.clear()
