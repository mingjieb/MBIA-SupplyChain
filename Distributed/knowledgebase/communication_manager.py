#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

class CommunicationManager():

    def __init__(self):
        self.delivered_request = {}
        self.received_request = {}
        self.delivered_response = {}
        self.received_response = {}

    def clear_message(self):
        self.delivered_request.clear()
        self.received_request.clear()
        self.delivered_response.clear()
        self.received_response.clear()
