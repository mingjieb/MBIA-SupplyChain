#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi
@Contact :   mingjieb@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

import info
class StateModel():

    def __init__(self):
        self.Y = []
        self.E = []
        self.Tr = []
        self.y0 = type(info)
        self.Y_m = []
        self.attribute = None
