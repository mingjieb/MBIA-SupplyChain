#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""


import json
from Distributed.functions.metrics_output import flow_difference, production_difference

def check_centralized_difference(initial_flows, initial_productions, result_file_name, agent_network):

    with open(result_file_name) as f:
        data = json.load(f)

    flows = {}
    for fl in data['Flows']:
        flows[(fl['Source'], fl['Dest'], fl['Product'])] = fl["Value"]

    productions = {}
    for prod in data['Productions']:
        productions[(prod['Agent'], prod['Product'])] = prod["Value"]


