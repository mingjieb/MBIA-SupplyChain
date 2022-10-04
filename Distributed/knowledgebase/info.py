#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

class State():

    def __init__(self, product, attribute, unit):
        self.product = product
        self.attribute = attribute
        self.unit = unit










class Event():

    def __init__(self, start, end):
        self.start_state = start
        self.end_state = end
        self.cost = None
