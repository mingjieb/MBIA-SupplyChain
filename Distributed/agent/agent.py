#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

# Super class for agents in the supply chain network
from colorama import init
from termcolor import colored


class Agent:

    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.flow = dict()
        self.cost = dict()
        self.capability = dict()
        self.environment = list()
        self.communication_nodes = list()
        self.demand = dict()
        self.due_date = 0
        self.add_edge_limit = 4
        self.flow_indicator = dict()

    # agent sends request to other agents in its environment model
    def request(self, product, unit, environment_agent, lost_flow):
        # TODO: make decision of which agent it chooses to request
        # Now it requests all the agents in environment model
        bid_response = []  # each request should start with an empty bid
        for requestedAgent in environment_agent:

            if requestedAgent.check_product_capability(product):
                if requestedAgent.type not in ["Inventory", "Transportation"]:
                    print(colored("Requests:", 'red'), self.name, "to", requestedAgent.name, ":", unit, product)
                    if requestedAgent.type == "OEM":
                        bid_response.append(requestedAgent.check_request(self, product, unit, lost_flow))
                    # limit add edges hard code
                    elif self.name == "Manuf_03" and requestedAgent.name == "Part_06":
                        pass
                    else:
                        bid_response.append(requestedAgent.check_request(self, product, unit))
        selection_decision = self.decision_making(sum(bid_response, []))  # flatten the list
        self.inform(selection_decision, lost_flow)

    # agent send response to the requesting agent
    # def response(self, requestingAgent, product, unit):
    #     res = dict()
    #     if self.find_transportation(requestingAgent, product, unit):
    #         if product in self.inventory.keys():
    #             self.inventory[product] -= unit
    #             res["product"] = unit
    #         return True
    #     return False

    # TODO: agent inform decision
    def inform(self, selected_decision, lost_flow):
        for decision in selected_decision:
            requested_agent = decision["Agent"]
            transport = decision["TA"]
            product = decision["Product"]
            unit = decision["Result"]
            due_date = decision["Supply date"][int(unit) - 1]
            self.demand[product] -= unit
            if self.demand[product] == 0.0:
                self.demand.pop(product)
            # add production
            if "Production" in requested_agent.capability.keys():
                if (str(requested_agent.name), str(product)) in requested_agent.production.keys():
                    requested_agent.production[(str(requested_agent.name), str(product))] += unit
                else:
                    requested_agent.production[(str(requested_agent.name), str(product))] = unit
            # add flow
            if requested_agent.type != self.type:
                if (str(requested_agent.name), str(self.name), str(product)) in transport.flow.keys():
                    transport.flow[(str(requested_agent.name), str(self.name), str(product))] += unit
                    print("Change", (str(requested_agent.name), str(self.name), str(product)))
                    transport.flow_change += 1
                else:
                    transport.flow[(str(requested_agent.name), str(self.name), str(product))] = unit
                    print("Add", (str(requested_agent.name), str(self.name), str(product)))
                    transport.flow_added += 1
            else:
                for f in lost_flow:
                    if f[0][2] == product:
                        if (str(requested_agent.name), str(f[0][1]), str(product)) in transport.flow.keys():
                            transport.flow[(str(requested_agent.name), str(f[0][1]), str(product))] += f[1]
                            print("Change", (str(requested_agent.name), str(f[0][1]), str(product)))
                            transport.flow_change += 1
                        else:
                            transport.flow[(str(requested_agent.name), str(f[0][1]), str(product))] = f[1]
                            print("Add", (str(requested_agent.name), str(f[0][1]), str(product)))
                            transport.flow_added += 1
            print(colored("Inform:", 'green'), self.name, "to", requested_agent.name, ":", unit, product)
            # if requested_agent.type != "Raw Material Supplier":
            if requested_agent.type != "Manufacturing Supplier":
                requested_agent.propagate_request(product, unit, due_date, lost_flow)

    # Check whether the agent can provide the product
    def check_product_capability(self, product):
        for key in self.capability:
            if key in ["Production", "Inventory"] and product in self.capability[key]:
                return True
        return False

    # Disruption adaptation
    def adaptation(self, agent_list, lost_production, lost_flow):
        print(self.name, "starts communication for adaptation")
        # find alternative agent
        alternative_agent = {}
        products = []
        product_amount = []
        for production in lost_production:
            for item in production.items():
                products.append(item[0][1])
                product_amount.append(item[1])
        for key in agent_list.keys():
            for ag in agent_list[key]:
                if "Production" in ag.capability.keys() and ag.name != self.name:
                    for production in lost_production:
                        for item in production.items():
                            if item[0][1] in ag.capability["Production"]:
                                if item[0][1] in alternative_agent.keys():
                                    alternative_agent[item[0][1]].append(ag)
                                else:
                                    alternative_agent[item[0][1]] = [ag]
        for key in alternative_agent.keys():
            print("For product", key, ", find alternative agent:", [ag.name for ag in alternative_agent[key]])

        for i in range(len(products)):
            self.demand[products[i]] = product_amount[i]

        # reformat the request information
        self.request_lose_node(products, product_amount, alternative_agent, lost_flow)

    # agent sends request to adapt to disruption of losing node
    def request_lose_node(self, products, units, alternative_agent, lost_flow):
        # Now it requests all the agents in environment model
        bid_response = {}  # each request should start with an empty bid
        bid_request = {}
        # determine the flow that will be sent to alternative agents
        req = []
        for f in lost_flow:
            if f[0][0] == self.name:
                product = f[0][2]
                req.append((f[0][1],f[0][2],f[1]))
                for ag in alternative_agent[product]:
                    if ag in bid_request.keys():
                        bid_request[ag].append((f[0][1],f[0][2],f[1]))
                    else:
                        bid_request[ag] = [(f[0][1],f[0][2],f[1])]
        for key in bid_request.keys():
            print(colored("Requests:", 'red'), self.name, "to", key.name, ":", bid_request[key])
            bid_response[key] = key.determine_max_output(self, bid_request[key])


        selection_decision = self.decision_making_lose_node(bid_response, req)  # flatten the list
        # limit add edges hard code
        selection_decision[2]["Agent"] = selection_decision[0]["Agent"]
        selection_decision[0]["Unit"] = 200.0
        selection_decision[1]["Unit"] = 1681.0
        self.inform_lose_node(selection_decision, lost_flow)

    def inform_lose_node(self, selected_decision, lost_flow):
        info = {}
        for decision in selected_decision:
            requested_agent = decision["Agent"]
            destination = decision["Destination"]
            transport = decision["Transportation"]
            product = decision["Product"]
            unit = decision["Unit"]
            due_date = 1
            self.demand[product] -= unit
            if self.demand[product] == 0.0:
                self.demand.pop(product)
            if requested_agent in info.keys():
                info[requested_agent]["Flow"].append((destination, product, unit))
                if str(product) in info[requested_agent]["Product"].keys():
                    info[requested_agent]["Product"][str(product)] += unit
                else:
                    info[requested_agent]["Product"][str(product)] = unit
            else:
                info[requested_agent] = {"Flow": [(destination, product, unit)], "Product": {str(product): unit}}
            # add production
            if (str(requested_agent.name), str(product)) in requested_agent.production.keys():
                requested_agent.production[(str(requested_agent.name), str(product))] += unit
            else:
                requested_agent.production[(str(requested_agent.name), str(product))] = unit
            # add flow
            if (str(requested_agent.name), destination, str(product)) in transport.flow.keys():
                transport.flow[(str(requested_agent.name), destination, str(product))] += unit
                transport.flow_change += 1
                print("Change", (str(requested_agent.name), destination, str(product)))
            else:
                transport.flow[(str(requested_agent.name), destination, str(product))] = unit
                transport.flow_added += 1
                print("Add", (str(requested_agent.name), destination, str(product)))
        for key in info.keys():
            print(colored("Inform:", 'green'), self.name, "to", key.name, ":", info[key]["Flow"])

        for key in info.keys():
            if key.type != "Manufacturing Supplier":
                key.propagate_request_lose_node(info[key]["Product"], due_date, lost_flow)

        # limit add edges hard code
        # for key in info.keys():
        #     if key.type != "Manufacturing Supplier" and key.name == "Manuf_03":
        #         key.propagate_request_lose_node(info[key]["Product"], due_date, lost_flow)
        #
        # for key in info.keys():
        #     if key.type != "Manufacturing Supplier" and key.name == "Manuf_02":
        #         key.propagate_request_lose_node(info[key]["Product"], due_date, lost_flow)