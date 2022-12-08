#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

class EnvironmentModel():

    def __init__(self):
        # Initialize environment model from initialization file
        self.upstream_agent = {}
        self.downstream_agent = {}
        self.transport_agent = {}
        self.clustering_agent = {}
        # Read initialization file


    # Functions for updating environment model


    def add_environment(self, key, product, agent):
        if key == 'upstream':
            if product not in self.upstream_agent.keys():
                self.upstream_agent[product] = [agent]
            elif agent not in self.upstream_agent[product]:
                self.upstream_agent[product].append(agent)

        if key == 'downstream':
            if product not in self.downstream_agent.keys():
                self.downstream_agent[product] = [agent]
            elif agent not in self.downstream_agent[product]:
                self.downstream_agent[product].append(agent)

        if key == 'clustering':
            if product not in self.clustering_agent.keys():
                self.clustering_agent[product] = [agent]
            elif agent not in self.clustering_agent[product]:
                self.clustering_agent[product].append(agent)


    def remove_environment(self, key, product):
        # Remove a product type to a capability 'key'
        if product in self.knowledge[key]:
            self.knowledge[key].remove(product)
        for char in self.characteristics[key].keys():
            if product in self.characteristics[key][char].keys():
                self.characteristics[key][char].remove(product)


    # Functions for obtaining information from environment model

    def is_in_environment(self, key, product):
        # Check whether the agent has capability 'key' for 'product'
        if product in self.knowledge[key]:
            return True
        return False
