#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@Author  :   Mingjie Bi and Gongyu Chen
@Contact :   mingjieb@umich.edu, chgongyu@umich.edu
@Desc    :   Model Based Intelligent Agent (MBIA) supply chain project

"""

# Super class for agents in the supply chain network
from Distributed.initialization import network
from Distributed.knowledgebase import capability_model, environment_model, state_model, communication_manager
from termcolor import colored
import gurobipy as gp
from gurobipy import GRB, max_, min_, and_
import numpy as np
from scipy.stats import truncnorm
from statistics import mean
import math

class Agent:

    def __init__(self, name, type):
        # knowledge base
        self.name = name
        self.type = type
        self.flow = dict()
        self.capability = capability_model.CapabilityModel()
        self.environment = environment_model.EnvironmentModel()
        self.state = state_model.StateModel()
        self.communication_manager = communication_manager.CommunicationManager()
        self.down = False
        self.demand = dict()
        self.due_date = dict()
        self.risk_averse = False

    # disrupted agent identifies demand agents and their demands
    def find_demand_agents(self, agent_network, lost_production, lost_flow):
        # find demand agents
        demand_agents = []
        for f in lost_flow:
            if f[0][0] == self.name:
                ag = agent_network.find_agent_by_name(agent_network, f[0][1])
                if ag not in demand_agents:
                    demand_agents.append(ag)
                # identify demand
                ag.demand[f[0][2]] = f[1]
        # for ag in demand_agents:
        #     for d in ag.demand.keys():
        #         print(ag.name, "has demand for", d, ":", ag.demand[d])
        return demand_agents

    # demand agent explores supplier agents to request
    def exploration(self, agent_network):
<<<<<<< Updated upstream
=======
        # current_inflow_agents = []
        # for flow_key in self.state.inflow.keys():
        #     if flow_key[0] not in current_inflow_agents:
        #         current_inflow_agents.append(flow_key[0])
        trans = network.find_agent_by_name(agent_network, "Transportation")
>>>>>>> Stashed changes
        supplier_agents = {}
        for product in self.demand.keys():
            flag = False
            supplier_agents[product] = []
            for upstream_agent in self.environment.upstream_agent[product]:
                if not upstream_agent.down:
                    supplier_agents[product].append(upstream_agent)
<<<<<<< Updated upstream
        # TODO: explore other agent in network but not in environment
=======
            #         # only check agents that are currently in its environment model
            #         if not self.explore and upstream_agent.used:
            #             supplier_agents[product].append(upstream_agent)
            # for ag in supplier_agents[product]:
            #     if ag.have_remaining_capacity() and trans.have_capacity(ag.name, self.name):
            #         flag = True
            # if len(supplier_agents[product]) == 0 or not flag:
            #     self.explore = True
            #     # explore other agent in network but not in environment
            #     for upstream_agent in self.environment.upstream_agent[product]:
            #         if not upstream_agent.down and self.explore and not upstream_agent.used:
            #             supplier_agents[product].append(upstream_agent)

>>>>>>> Stashed changes
        return supplier_agents

    # demand agent sends request to supplier agents
    def send_request(self, supplier_agents):
        for product in supplier_agents.keys():
            # req = {product: self.demand[product]}
            for sup_ag in supplier_agents[product]:
                # Store the request information
                # try:
                #     self.communication_manager.delivered_request[sup_ag.name].update({product: self.demand[product]})
                #     sup_ag.communication_manager.received_request[self.name].update({product: self.demand[product]})
                # except:
                #     self.communication_manager.delivered_request[sup_ag.name] = {product: self.demand[product],
                #                                                                  "reqToAgent": sup_ag}
                #     sup_ag.communication_manager.received_request[self.name] = {product: self.demand[product],
                #                                                                 "reqFromAgent": self}

                try:
                    self.communication_manager.delivered_request[sup_ag.name].update(
                            {product: {"Amount": self.demand[product], "Time": self.due_date[product], "Price": 1.1}})
                    sup_ag.communication_manager.received_request[self.name].update({product: {"Amount": self.demand[product], "Time": self.due_date[product], "Price": 1.1}})
                except:
                    self.communication_manager.delivered_request[sup_ag.name] = {product: {"Amount": self.demand[product], "Time": self.due_date[product], "Price": 1.1},
                                                                                     "reqToAgent": sup_ag}
                    sup_ag.communication_manager.received_request[self.name] = {product: {"Amount": self.demand[product], "Time": self.due_date[product], "Price": 1.1},
                                                                                    "reqFromAgent": self}

                    # supplier agent determines its response to request

    # supplier agent determine response
    def response_optimizer(self, transportation):
        demand_agents = self.communication_manager.received_request.keys()
        product_set = {}
        demands = {}
        flow_limit = {}
        overcapacity_multiplier = 1.3

        # Computes the flow limit and production limit
        for ag_name in demand_agents:
            for product in self.communication_manager.received_request[ag_name].keys():
                if product != "reqFromAgent":
                    try:
                        product_set[ag_name].append(product)
                    except:
                        product_set[ag_name] = [product]
                    demands[(ag_name, product)] = self.communication_manager.received_request[ag_name][product]

            flow_limit[ag_name] = transportation.get_available_capacity(self.name, ag_name, overcapacity_multiplier)

        current_production = 0
        for key in self.state.production.keys():
            current_production += self.state.production[key]
        production_limit = self.capability.get_capacity() * overcapacity_multiplier - current_production

        # MILP gurobi model
        model = gp.Model('response_optimizer')
        model.Params.LogToConsole = 0
        pairs = [(j, k) for j in demand_agents for k in product_set[j]]
        y = model.addVars(pairs, vtype=GRB.INTEGER, name="max_flow")

        obj = model.setObjective(gp.quicksum(demands[j, k] - y[j, k]
                                             for j in demand_agents for k in product_set[j]), GRB.MINIMIZE)

        tp_constrs = model.addConstrs((gp.quicksum(y[j, k] for k in product_set[j]) <= flow_limit[j]
                                       for j in demand_agents), name="tp_limit")
        pd_constrs = model.addConstr(gp.quicksum(y[j, k] for j in demand_agents for k in product_set[j])
                                     <= production_limit, name="pd_limit")
        demand_constrs = model.addConstrs((y[j, k] <= demands[j, k] for j in demand_agents for k in product_set[j]),
                                          name="demand_limit")

        model.optimize()
        xsol = model.getAttr('x', y)
        response_decisions = {}
        for j in demand_agents:
            response = {}
            for k in product_set[j]:
                if xsol[j, k] > 0.1:
                    cost_pd = self.capability.characteristics["Production"][k]["Cost"]
                    cost_tp = transportation.capability.characteristics["Transportation"][(self.name, j)]["Cost"]
                    response.update({k: {"amount": xsol[j, k],
                                         "cost_pd": cost_pd,
                                         "remaining_cap_pd": self.get_normal_remaining_capacity(),
                                         "cost_tp": cost_tp,
                                         "remaining_cap_tp": transportation.get_normal_available_capacity(self.name,
                                                                                                          ag_name),
                                         "lead_time": self.capability.characteristics["Production"][k]["LeadTime"],
                                         "sigma": self.capability.characteristics["Production"][k]["Sigma"]
                                         }
                                     })
            response_decisions[j] = {"demandAgent": self.communication_manager.received_request[j]["reqFromAgent"],
                                     "response": response}

        # response_decisions["agentname"] = {"demandAgent": 1,
        #                                    "response":
        #                                        {"k1": {"amount": 1, "unit_cost": 1},
        #                                         "k2": {"amount": 1, "unit_cost": 1}}}
        return response_decisions

    # supplier agent sends response to demand agents
    def send_response(self, response_decision):
        for name in response_decision.keys():
            ag_dm = response_decision[name]["demandAgent"]
            resp = response_decision[name]["response"]
            self.communication_manager.delivered_response[ag_dm.name] = {"response": resp, "respToAgent": ag_dm}
            ag_dm.communication_manager.received_response[self.name] = {"response": resp, "reqFromAgent": self}

    # demand agent selects suppliers
    def supplier_selector(self):
        model = gp.Model('Supplier_selector')
        model.Params.LogToConsole = 0
        supplier_agents = self.communication_manager.received_response.keys()
        response = {}
        for ag_name in supplier_agents:
            response[ag_name] = self.communication_manager.received_response[ag_name]["response"]

        pairs = [(i, k) for i in supplier_agents for k in response[i].keys()]
        # separate the production and flow that are within capacity and over capacity
        x_pd = model.addVars(pairs, vtype=GRB.INTEGER, name="pd")
        x_tp = model.addVars(pairs, vtype=GRB.INTEGER, name="flow")
        x_over_pd = model.addVars(pairs, vtype=GRB.INTEGER, name="over_pd")
        x_over_tp = model.addVars(pairs, vtype=GRB.INTEGER, name="over_tp")

        obj = model.setObjective(gp.quicksum(response[i][k]["cost_pd"] * x_pd[i, k] + 2 * response[i][k]["cost_pd"] * x_over_pd[i, k]
                                             + response[i][k]["cost_tp"] * x_tp[i, k] + 2 * response[i][k]["cost_tp"] * x_over_tp[i, k]
                                             - 1e8*(x_pd[i, k]+x_over_pd[i, k])
                                             for i in supplier_agents for k in response[i].keys()), GRB.MINIMIZE)

<<<<<<< Updated upstream
        resp_constrs_pd = model.addConstrs((x_pd[i, k]+x_over_pd[i, k] <= response[i][k]["amount"]
                                       for i in supplier_agents for k in response[i].keys()), name="resp_limit_pd")
=======
        used_agent = []
        for ag_sup in self.communication_manager.received_response.keys():
            if self.communication_manager.received_response[ag_sup]["reqFromAgent"].used:
                used_agent.append(ag_sup)

        zeta = model.addVars(supplier_agents, vtype=GRB.BINARY, name="used_supplier")

        if self.explore:
            obj = model.setObjective(
                gp.quicksum(response[i][k]["cost_pd"] * x_pd[i, k] + 2 * response[i][k]["cost_pd"] * x_over_pd[i, k]
                            + response[i][k]["cost_tp"] * x_tp[i, k] + 2 * response[i][k]["cost_tp"] * x_over_tp[i, k]
                            - 1e8 * (x_pd[i, k] + x_over_pd[i, k]) + 1e4 * zeta[i]
                            for i in supplier_agents for k in response[i].keys()), GRB.MINIMIZE)
        else:
            obj = model.setObjective(
                gp.quicksum(response[i][k]["cost_pd"] * x_pd[i, k] + 2 * response[i][k]["cost_pd"] * x_over_pd[i, k]
                            + response[i][k]["cost_tp"] * x_tp[i, k] + 2 * response[i][k]["cost_tp"] * x_over_tp[i, k]
                            - 1e8 * (x_pd[i, k] + x_over_pd[i, k])
                            for i in supplier_agents for k in response[i].keys()), GRB.MINIMIZE)

        resp_constrs_pd = model.addConstrs((x_pd[i, k] + x_over_pd[i, k] <= response[i][k]["amount"] * zeta[i]
                                            for i in supplier_agents for k in response[i].keys()), name="resp_limit_pd")
>>>>>>> Stashed changes

        resp_constrs_tp = model.addConstrs((x_tp[i, k] + x_over_tp[i, k] <= response[i][k]["amount"]
                                            for i in supplier_agents for k in response[i].keys()), name="resp_limit_tp")

<<<<<<< Updated upstream
        capacity_constrs_pd = model.addConstrs((gp.quicksum(x_pd[i, k] for k in response[i].keys()) <= response[i][k]["remaining_cap_pd"]
                                         for i in supplier_agents for k in response[i].keys()), name="capacity_limit_pd")
=======
        capacity_constrs_pd = model.addConstrs(
            (gp.quicksum(x_pd[i, k] for k in response[i].keys()) <= response[i][k]["remaining_cap_pd"] * zeta[i]
             for i in supplier_agents for k in response[i].keys()), name="capacity_limit_pd")
>>>>>>> Stashed changes

        capacity_constrs_tp = model.addConstrs(
            (gp.quicksum(x_tp[i, k] for k in response[i].keys()) <= response[i][k]["remaining_cap_tp"]
             for i in supplier_agents for k in response[i].keys()), name="capacity_limit_tp")

        balance = model.addConstrs((x_tp[i, k] + x_over_tp[i, k] == x_pd[i, k] + x_over_pd[i, k]
<<<<<<< Updated upstream
             for i in supplier_agents for k in response[i].keys()), name="capacity_limit_tp")

        demand_constrs = model.addConstrs((gp.quicksum(x_pd[i, k]+x_over_pd[i, k] for i in supplier_agents if k in response[i]) <= self.demand[k]
                                           for k in self.demand.keys()), name="demand_limit")
=======
                                    for i in supplier_agents for k in response[i].keys()), name="balance")

        demand_constrs = model.addConstrs(
            (gp.quicksum(x_pd[i, k] + x_over_pd[i, k] for i in supplier_agents if k in response[i]) <= self.demand[k]
             for k in self.demand.keys()), name="demand_limit")

        priority_constrs = model.addConstrs((zeta[i] == 1 for i in used_agent), name="demand_limit")
>>>>>>> Stashed changes

        model.optimize()
        xsol = model.getAttr('x', x_pd)
        x_over_sol = model.getAttr('x', x_over_pd)
        selection_decision = {}
        for i in supplier_agents:
            selection_decision[i] = {}
            for k in response[i].keys():
<<<<<<< Updated upstream
                if xsol[i, k]+x_over_sol[i, k] > 0.1:
                    selection_decision[i].update({k: xsol[i, k]+x_over_sol[i, k]})
=======
                if xsol[i, k] + x_over_sol[i, k] > 0.1:
                    selection_decision[i].update({k: xsol[i, k] + x_over_sol[i, k]})
                if x_over_sol[i, k] > 0.1:
                    over_production[(i, k)] = x_over_sol[i, k]
                if x_over_sol_tp[i, k] > 0.1:
                    over_flow[(i, self.name, k)] = x_over_sol_tp[i, k]
>>>>>>> Stashed changes
            if len(selection_decision[i].keys()) == 0:
                selection_decision.pop(i)

        # selection_decision["supplier_name"] = {"k1": 1, "k2": 1}
        new_flows = {}
        for sup_name in selection_decision.keys():
            for product in selection_decision[sup_name]:
                new_flows[(sup_name, self.name, product)] = selection_decision[sup_name][product]
<<<<<<< Updated upstream
        
        return selection_decision, new_flows
=======

        return selection_decision, new_flows, over_production, over_flow
>>>>>>> Stashed changes

    # demand agent check demand
    def check_demand(self, new_flows):
        flag = True
        for product in list(self.demand.keys()):
            actual_get = 0
            for flow in new_flows.items():
                if self.name == flow[0][1] and product == flow[0][2]:
                    actual_get += flow[1]
<<<<<<< Updated upstream
            if actual_get >= self.demand[product]:
=======
            if abs(actual_get - self.demand[product]) <= 1:
>>>>>>> Stashed changes
                self.demand.pop(product)
                self.due_date.pop(product)
            else:
                self.demand[product] -= actual_get
                flag = False
        return flag

    # supplier agent find needed materials based on the required production
    def find_needed_materials(self, needed_production):
        needed_materials = {}
        for product in needed_production.keys():
            product_structure = self.capability.characteristics["Production"][product]["Material"]
            amount = needed_production[product]
            for material in product_structure.keys():
                try:
                    needed_materials[material] += product_structure[material] * amount
                except:
                    needed_materials[material] = product_structure[material] * amount

        return needed_materials

    # calculate the total flow in this edge
    def get_transportaion_amount(self, source, dest):
        amount = 0
        for flow in self.flow.keys():
            if flow[0] == source and flow[1] == dest:
                amount += self.flow[flow]
        return amount

    # check whether the network has remaining related agents the this agent has not explored
    def check_possible_iteration(self, agent_network):
        flag = False
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
        supplier_agents = self.exploration(agent_network)
        for product in self.demand.keys():
            if len(supplier_agents[product]) != 0:
                for ag_sup in supplier_agents[product]:
                    if ag_sup.have_remaining_capacity():
                        flag = True
                        break
        return flag

    # check whether the agent has remaining production capacity
    def have_remaining_capacity(self):
        if len(self.capability.knowledge["Production"]) == 0:
            return False
        total_production = 0
        for product in self.state.production.keys():
            total_production += self.state.production[product]
<<<<<<< Updated upstream
        if self.capability.get_capacity() - total_production > 0:
=======
        if 1.3 * self.capability.get_capacity() - total_production > 0:
>>>>>>> Stashed changes
            return True
        else:
            return False

    # get the remaining capacity considering over capacity
    def get_remaining_capacity(self):
        total_production = 0
        for product in self.state.production.keys():
            total_production += self.state.production[product]
        return 1.3 * self.capability.get_capacity() - total_production

    # get the remaining capacity without over capacity
    def get_normal_remaining_capacity(self):
        total_production = 0
        for product in self.state.production.keys():
            total_production += self.state.production[product]
        return max(0, self.capability.get_capacity() - total_production)

    # determine which downstream agents are affected and cancel their related production
    def cancel_downstream_production(self, agent_network):
        model = gp.Model('Cancel_downstream_production')
        model.Params.LogToConsole = 0

        # Get the downstream products that might be affected
        potential_affected_product = set()
        potential_affected_outflow = set()
        for outflow in self.state.outflow.keys():
            for component in self.demand.keys():
                if component in self.capability.characteristics["Production"][outflow[1]]["Material"].keys():
                    potential_affected_outflow.add(outflow)
                    potential_affected_product.add(outflow[1])

        K = potential_affected_product
        product_structure = {}
        for component in self.demand.keys():
            product_structure[component] = []
            for final_prod in K:
                if component in self.capability.characteristics["Production"][final_prod]["Material"].keys():
                    product_structure[component].append(final_prod)
        # Identify the affected downstream agent
        downstream = {}
        for final_prod in K:
            downstream[final_prod] = []
            for flow in potential_affected_outflow:
                if flow[1] == final_prod:
                    downstream[final_prod].append(flow[0])

        pairs = [(j, k) for k in K for j in downstream[k]]
        x = model.addVars(pairs, vtype=GRB.INTEGER, name="cancelled_production")
        # minimize the total cancelled production
        obj = model.setObjective(gp.quicksum(x[j, k] for k in K for j in downstream[k]), GRB.MINIMIZE)

        demand_constrs = model.addConstrs((gp.quicksum(
            gp.quicksum(x[j, k] for j in downstream[k]) * self.capability.characteristics["Production"][k]["Material"][
                c] for k in product_structure[c]) >= self.demand[c]
                                           for c in self.demand.keys()), name="demand_limit")
        flow_constrs = model.addConstrs((x[j, k] <= self.state.outflow[(j, k)] for k in K for j in downstream[k]),
                                        name="downflow_limit")

        model.optimize()
        status = model.status
        if status == GRB.Status.INFEASIBLE:
            print("Model is infeasible")
        xsol = model.getAttr('x', x)

        reduced_outflow = {}
        for k in K:
            for j in downstream[k]:
                if xsol[j, k] > 0.1:
                    reduced_outflow[(j, k)] = xsol[j, k]

        reduced_production = {}
        for flow in reduced_outflow:
            try:
                reduced_production[flow[1]] += reduced_outflow[flow]
            except:
                reduced_production[flow[1]] = reduced_outflow[flow]

        # update the flow and production in the network
        transportation = network.find_agent_by_name(agent_network, "Transportation")
        for prod in reduced_production:
            self.state.update_prod_inv("production", prod, -reduced_production[prod])
            # ripple effects to other upstream agents of the cancelled-production agents
            self.cancel_upstream_production(agent_network)
            self.demand.clear()
        outflow_agents = set()
        for flow in reduced_outflow.keys():
            self.state.update_flow("outflow", flow[0], flow[1], -reduced_outflow[flow])

            downstream_agent = network.find_agent_by_name(agent_network, flow[0])
            downstream_agent.state.update_flow("inflow", self.name, flow[1], -reduced_outflow[flow])
            transportation.update_flow((self.name, flow[0], flow[1]), -reduced_outflow[flow])
            agent_network.occurred_communication += 1
            if "Customer" not in downstream_agent.name:
                downstream_agent.demand[flow[1]] = reduced_outflow[flow]
                outflow_agents.add(downstream_agent)
        # ripple effects to the downstream agents of the cancelled-production agents
        for downstream_agent in outflow_agents:
            downstream_agent.cancel_downstream_production(agent_network)

    # determine which upstream agents are affected and cancel their related production
    def cancel_upstream_production(self, agent_network):
        model = gp.Model('Cancel_upstream_production')
        model.Params.LogToConsole = 0

        # identify the upstream agents
        upstream = {}
        up_agent = set()
        for flow in self.state.inflow.keys():
            up_agent.add(flow[0])
            try:
                upstream[flow[1]].append(flow[0])
            except:
                upstream[flow[1]] = [flow[0]]

        product_structure = {}
        for component in upstream.keys():
            product_structure[component] = []
            for final_prod in self.state.production.keys():
                if component in self.capability.characteristics["Production"][final_prod]["Material"].keys():
                    product_structure[component].append(final_prod)

        # identify the current needs for upstream agents depending on the current production
        total_need = {}
        for component in upstream.keys():
            total_need[component] = 0
            for prod in product_structure[component]:
                total_need[component] += self.state.production[prod] * \
                                         self.capability.characteristics["Production"][prod]["Material"][component]

        pairs = [(i, k) for k in upstream.keys() for i in upstream[k]]
        x = model.addVars(pairs, vtype=GRB.INTEGER, name="remaining_production")
        # minimize the total cancelled flow
        obj = model.setObjective(
            gp.quicksum(self.state.inflow[(i, k)] - x[i, k] for k in upstream.keys() for i in upstream[k]),
            GRB.MINIMIZE)

        demand_constrs = model.addConstrs(
            (gp.quicksum(x[i, k] for i in upstream[k]) <= total_need[k] for k in upstream.keys()), name="demand_limit")

        model.optimize()
        xsol = model.getAttr('x', x)

        # update the production and flow in the network
        transportation = network.find_agent_by_name(agent_network, "Transportation")
        for k in upstream.keys():
            for i in upstream[k]:
                initial_flow = self.state.inflow[(i, k)]
                self.state.update_flow("inflow", i, k, xsol[i, k] - initial_flow)
                transportation.update_flow((i, self.name, k), xsol[i, k] - initial_flow)
                ag = network.find_agent_by_name(agent_network, i)
                ag.state.update_prod_inv("production", k, xsol[i, k] - initial_flow)
                ag.state.update_flow("outflow", self.name, k, xsol[i, k] - initial_flow)
                # ripple effects
                if len(ag.state.inflow.keys()) != 0:
                    ag.cancel_upstream_production(agent_network)

        agent_network.occurred_communication += len(up_agent)

    def response_stochastic(self, transportation):
        # model parameter setting
        sce_num = 50
        overprod_alpha = 0.3
        overtime_beta = 1.5
        overcost = 10
        weight_t = 1e5
        weight_p = 1e5

        # constraint parameter setting
        demand_agents = self.communication_manager.received_request.keys()
        product_set = {}
        demands = {}
        time_req = {}
        flow_limit = {}
        price = {}
        gain_p = {}
        gain_t = {}
        # Computes the flow limit and production limit
        for ag_name in demand_agents:
            for product in self.communication_manager.received_request[ag_name].keys():
                if product != "reqFromAgent":
                    try:
                        product_set[ag_name].append(product)
                    except:
                        product_set[ag_name] = [product]
                    demands[(ag_name, product)] = self.communication_manager.received_request[ag_name][product]["Amount"]
                    time_req[(ag_name, product)] = self.communication_manager.received_request[ag_name][product]["Time"]
                    price[(ag_name, product)] = self.communication_manager.received_request[ag_name][product]["Price"]
            gain_p[ag_name] = 100  # TODO: need to be added
            gain_t[ag_name] = 100

            flow_limit[ag_name] = transportation.get_available_capacity(self.name, ag_name, 1+overprod_alpha)

        current_production = 0
        for key in self.state.production.keys():
            current_production += self.state.production[key]
        production_limit = self.get_normal_remaining_capacity()
        prod_sigma = self.capability.get_capacity() * overprod_alpha/3
        # production_limit = self.capability.get_capacity() * (1+overprod_alpha) - current_production

        # uncertain parameters sampling
        b = (production_limit + 3 * prod_sigma - production_limit) / prod_sigma
        prod_est = truncnorm.rvs(0, b, loc=production_limit, scale=prod_sigma, size=sce_num)
        prod_est = prod_est.round().astype(int)
        # prod_est = self.truncated_normal_distribution(production_limit, prod_sigma, sce_num)
        leadtime_est = {}
        prodtime_est = {}
        for j in demand_agents:
            for k in product_set[j]:
                mean_lt = self.capability.characteristics["Production"][k]["LeadTime"]
                std_lt = self.capability.characteristics["Production"][k]["Sigma"]
                leadtime_est[(j, k)] = self.truncated_normal_distribution(mean_lt, std_lt, sce_num)

                try:
                    mean_pt = self.state.prod_time[k]
                    std_pt = 0.1 * self.state.prod_time[k]
                except:
                    mean_pt = self.capability.characteristics["Production"][k]["NominalTime"]
                    std_pt = 0.1 * self.capability.characteristics["Production"][k]["NominalTime"]
                if mean_pt == 0: std_pt = 0.1
                prodtime_est[k] = self.truncated_normal_distribution(mean_pt, std_pt, sce_num)

        # MILP gurobi model
        model = gp.Model('response_optimizer')
        model.Params.LogToConsole = 0
        pairs = [(j, k, s) for j in demand_agents for k in product_set[j] for s in range(sce_num)]

        # decision variables
        y_u = model.addVars(pairs, vtype=GRB.INTEGER, name="y_u")
        y_o = model.addVars(pairs, vtype=GRB.INTEGER, name="y_o")
        v_u = model.addVars(pairs, vtype=GRB.INTEGER, name="v_u")
        v_o = model.addVars(pairs, vtype=GRB.INTEGER, name="v_o")
        gamma_u = model.addVars(pairs, vtype=GRB.BINARY, name="gamma_u")
        gamma_o = model.addVars(pairs, vtype=GRB.BINARY, name="gamma_o")
        eta_t = model.addVars(pairs, vtype=GRB.BINARY, name="eta_t")
        eta_p = model.addVars(pairs, vtype=GRB.BINARY, name="eta_p")
        rew_t = model.addVars([s for s in range(sce_num)], vtype=GRB.BINARY, name="r_t")
        rew_p = model.addVars([s for s in range(sce_num)], vtype=GRB.BINARY, name="r_p")

        y = model.addVars([(j, k) for j in demand_agents for k in product_set[j]], vtype=GRB.INTEGER, name="y")

        # objective
        # obj = model.setObjective(1 / sce_num *
        #     (gp.quicksum(0.8*price[j, k] * y_o[j, k, s] + price[j, k]*y_u[j, k, s] for j, k, s in pairs)
        #     + gp.quicksum(weight_t * rew_t[s]*100 + weight_p * rew_p[s]*100 for s in range(sce_num))), GRB.MAXIMIZE)

        # obj = model.setObjective(1 / sce_num *
        #                          (gp.quicksum(0.5 * price[j, k] * y_o[j, k, s] + price[j, k] * y_u[j, k, s]
        #                                       for j, k, s in pairs) + gp.quicksum(weight_p * rew_p[s]*100 for s in range(sce_num))), GRB.MAXIMIZE)
        obj = model.setObjective(1 / sce_num *
                                 (gp.quicksum(0.5 * price[j, k] * y_o[j, k, s] + price[j, k] * y_u[j, k, s]
                                              for j, k, s in pairs)), GRB.MAXIMIZE)

        # constraints
        # result_constrs = model.addConstrs(
        #     (y[j, k] == y_o[j, k, s] + y_u[j, k, s] for j, k, s in pairs),
        #     name="result")
        # delay_constrs = model.addConstrs(
        #     (time_req[j, k] <= overtime_beta * v_o[j, k, s] + 10000 * eta_t[j, k, s] for
        #      j, k, s in pairs), name="time_limit")
        # demand_constrs = model.addConstrs(
        #     (y_o[j, k, s] + y_u[j, k, s] <= demands[j, k] + 10000 * eta_p[j, k, s] for j, k, s in pairs),
        #     name="demand_limit")
        demand_constrs = model.addConstrs(
            (y_o[j, k, s] + y_u[j, k, s] <= demands[j, k] for j, k, s in pairs),
            name="demand_limit")
        # demand_constrs2 = model.addConstrs(
        #     ((y_o[j, k, s] + y_u[j, k, s] - demands[j, k]) * eta_p[j, k, s] == 0 for j, k, s in pairs),
        #     name="demand_limit2")

        # tp_constrs = model.addConstrs((gp.quicksum(y_u[j, k, s] + y_o[j, k, s] for k in product_set[j]) <= flow_limit[j]
        #                                for j in demand_agents for s in range(sce_num)), name="tp_limit")
        # yu_constrs = model.addConstrs((gp.quicksum(y_u[j, k, s] for j in demand_agents for k in product_set[j])
        #                                <= prod_est[s] for s in range(sce_num)), name="yu_limit")
        # yo_constrs = model.addConstrs((gp.quicksum(y_o[j, k, s] for j in demand_agents for k in product_set[j])
        #                                <= overprod_alpha * prod_est[s] for s in range(sce_num)), name="yo_limit")

        yu_constrs = model.addConstrs((gp.quicksum(y_u[j, k, s] for j in demand_agents for k in product_set[j])
                                       <= production_limit for s in range(sce_num)), name="yu_limit")
        yo_constrs = model.addConstrs((gp.quicksum(y_o[j, k, s] + y_u[j, k, s] for j in demand_agents for k in product_set[j])
                                       <= prod_est[s] for s in range(sce_num)), name="yo_limit")

        # u_indicator = model.addConstrs((y_u[j, k, s] <= 10000 * gamma_u[j, k, s] for j, k, s in pairs), name="gamma_u_c")
        # o_indicator = model.addConstrs((y_o[j, k, s] <= 10000 * gamma_o[j, k, s] for j, k, s in pairs), name="gamma_o_c")

        # vu_constrs = model.addConstrs(
        #     (v_u[j, k, s] == (leadtime_est[j, k][s] + prodtime_est[k][s]) * gamma_u[j, k, s] for j, k, s in pairs),
        #     name="v_u_c")
        # vo_constrs = model.addConstrs(
        #     (v_o[j, k, s] == overtime_beta * v_u[j, k, s] * gamma_o[j, k, s] for j, k, s in pairs), name="v_o_c")

        # rew_p_constrs = model.addConstrs((rew_p[s] == and_([eta_p[j, k, s] for k in product_set[j]])
        #                                   for j in demand_agents for s in range(sce_num)), name="rew_p_c")
        # rew_t_constrs = model.addConstrs((rew_t[s] == and_([eta_t[j, k, s] for k in product_set[j]])
        #                                   for j in demand_agents for s in range(sce_num)), name="rew_t_c")


        # over_constrs = model.addConstrs((gamma_o[j, k, s] <= gamma_u[j, k, s] for j, k, s in pairs), name="demand_limit")

        # if self.name == "wire_sup_1":
        #     print("debug")

        model.optimize()

        status = model.status
        if status == GRB.Status.INFEASIBLE:
            print("Model is infeasible")

        y_u_sol = model.getAttr('X', y_u)
        y_o_sol = model.getAttr('X', y_o)
        v_u_sol = model.getAttr('X', v_u)
        v_o_sol = model.getAttr('X', v_o)
        y_sol = model.getAttr('X', y)
        response_decisions = {}
        for j in demand_agents:
            response = {}
            for k in product_set[j]:
                # amount_u = min(production_limit, y_sol[j, k])
                # amount_o = max(0, y_sol[j, k]-production_limit)
                time_u = round(mean([leadtime_est[j, k][s] + prodtime_est[k][s] for s in range(sce_num)]))
                time_o = round(overtime_beta * time_u)
                amount_u = round(mean([y_u_sol[j, k, s] for s in range(sce_num)]))
                amount_o = round(mean([y_o_sol[j, k, s] for s in range(sce_num)]))
                # time_u = round(mean([v_u_sol[j, k, i] for i in range(sce_num) if y_u_sol[j, k, i]>0.1]))
                # time_o = round(mean([v_o_sol[j, k, i] for i in range(sce_num) if y_o_sol[j, k, i]>0.1]))
                if amount_u + amount_o > 0.1:
                    cost_pd = self.capability.characteristics["Production"][k]["Cost"]
                    cost_tp = transportation.capability.characteristics["Transportation"][(self.name, j)]["Cost"]
                    response.update({k: {"amount_u": amount_u,
                                         "amount_o": amount_o,
                                         "time_u": time_u,
                                         "time_o": time_o,
                                         "cost_pd": cost_pd,
                                         "remaining_cap_pd": self.get_normal_remaining_capacity(),
                                         "cost_tp": cost_tp,
                                         "remaining_cap_tp": transportation.get_normal_available_capacity(self.name,
                                                                                                          ag_name)}})
            response_decisions[j] = {"demandAgent": self.communication_manager.received_request[j]["reqFromAgent"],
                                     "response": response}

        # response_decisions["agentname"] = {"demandAgent": 1,
        #                                    "response":
        #                                        {"k1": {"amount": 1, "unit_cost": 1},
        #                                         "k2": {"amount": 1, "unit_cost": 1}}}
        return response_decisions

    def supplier_selector_stochastic(self):

        # model parameter setting
        sce_num = 50
        overprod_alpha = 1.3
        overtime_beta = 1.5
        overcost_coeff = 1.5
        weight_t = 1e5
        weight_p = 1e5

        supplier_agents = self.communication_manager.received_response.keys()
        response = {}
        for ag_name in supplier_agents:
            response[ag_name] = self.communication_manager.received_response[ag_name]["response"]
        pairs = [(z, k, s) for z in supplier_agents for k in response[z].keys() for s in range(sce_num)]

        # uncertain parameters sampling: y is product quantity, v is arrival time
        # samples are truncated from 0 to mean+3sigma
        y_u_est, y_o_est, v_u_est, v_o_est = {}, {}, {}, {}

        for z in supplier_agents:
            for k in response[z].keys():
                trust_level = self.communication_manager.received_response[z]["reqFromAgent"].capability.characteristics["Production"][k]["TrustLevel"]

                y_u_est[z, k] = self.truncated_normal_distribution(response[z][k]["amount_u"], trust_level * response[z][k]["amount_u"], sce_num)
                # check whether there is y_o
                if response[z][k]["amount_o"] > 0.1:
                    y_o_est[z, k] = self.truncated_normal_distribution(response[z][k]["amount_o"], trust_level * response[z][k]["amount_o"], sce_num)
                else:
                    y_o_est[z, k] = [0] * sce_num
                v_u_est[z, k] = self.truncated_normal_distribution(response[z][k]["time_u"], trust_level * response[z][k]["time_u"], sce_num)
                v_o_est[z, k] = self.truncated_normal_distribution(response[z][k]["time_o"], trust_level * response[z][k]["time_o"], sce_num)

        # build the model
        model = gp.Model('Supplier_selector')
        model.Params.LogToConsole = 0

        # separate the production and flow that are within capacity and over capacity
        x_pd = model.addVars(pairs, vtype=GRB.INTEGER, name="pd")
        x_tp = model.addVars(pairs, vtype=GRB.INTEGER, name="flow")
        x_over_pd = model.addVars(pairs, vtype=GRB.INTEGER, name="over_pd")
        x_over_tp = model.addVars(pairs, vtype=GRB.INTEGER, name="over_tp")
        y_u = model.addVars([(z, k) for z in supplier_agents for k in response[z].keys()], vtype=GRB.INTEGER, name="y_u")
        y_o = model.addVars([(z, k) for z in supplier_agents for k in response[z].keys()], vtype=GRB.INTEGER, name="y_o")

        delta_pair = [(k, s) for k in self.demand.keys() for s in range(sce_num)]
        delta_t = model.addVars(delta_pair, vtype=GRB.INTEGER, name="delta_t")
        delta_p = model.addVars(delta_pair, vtype=GRB.INTEGER, name="delta_p")

        lam_u = model.addVars(pairs, vtype=GRB.BINARY, name="lam_u")
        lam_o = model.addVars(pairs, vtype=GRB.BINARY, name="lam_o")

        # auxiliary variables to help construct the constraints
        aux_var00 = model.addVars(pairs, lb=-math.inf, vtype=GRB.INTEGER, name="aux00")
        aux_var01 = model.addVars(pairs, lb=-math.inf, vtype=GRB.INTEGER, name="aux01")
        aux_var1 = model.addVars(pairs, lb=-math.inf, vtype=GRB.INTEGER, name="aux1")
        aux_var2 = model.addVars(pairs, lb=-math.inf, vtype=GRB.INTEGER, name="aux2")
        aux_var3 = model.addVars(delta_pair, vtype=GRB.INTEGER, name="aux3")

        # risk neutral objective: minimize expected value
        obj = model.setObjective(1 / sce_num * gp.quicksum(
            gp.quicksum(response[z][k]["cost_pd"] * x_pd[z, k, s] +
                        overcost_coeff * response[z][k]["cost_pd"] * x_over_pd[z, k, s] +
                        response[z][k]["cost_tp"] * x_tp[z, k, s] +
                        overcost_coeff * response[z][k]["cost_tp"] * x_over_tp[z, k, s]
                        for z in supplier_agents for k in response[z].keys()) +
            gp.quicksum(weight_t * delta_t[k, s] for k in self.demand.keys()) +
            gp.quicksum(weight_p * delta_p[k, s] for k in self.demand.keys())
            for s in range(sce_num)), GRB.MINIMIZE)


        # risk averse objective: minimize maximal value
        if self.risk_averse:
            max_value = model.addVar(lb=-math.inf, ub=math.inf, obj=1, name="worst")
            obj_value = model.addVars([s for s in range(sce_num)], lb=-math.inf, ub=math.inf, name="obj")
            obj = model.setObjective(max_value, GRB.MINIMIZE)
            worst_case_constrs = model.addConstrs((max_value >= obj_value[s] for s in range(sce_num)), name="worst_case")
            obj_value_constrs = model.addConstrs((obj_value[s] == gp.quicksum(response[z][k]["cost_pd"] * x_pd[z, k, s] +
                        overcost_coeff * response[z][k]["cost_pd"] * x_over_pd[z, k, s] +
                        response[z][k]["cost_tp"] * x_tp[z, k, s] +
                        overcost_coeff * response[z][k]["cost_tp"] * x_over_tp[z, k, s]
                        for z in supplier_agents for k in response[z].keys()) +
                        gp.quicksum(weight_t * delta_t[k, s] for k in self.demand.keys()) +
                        gp.quicksum(weight_p * delta_p[k, s] for k in self.demand.keys())
                        for s in range(sce_num)), name="obj_case")

        # auxiliary variables for
        auxiliary00 = model.addConstrs((aux_var00[z, k, s] == v_u_est[z, k][s] - self.due_date[k] for z, k, s in pairs), name="aux00")
        auxiliary01 = model.addConstrs((aux_var01[z, k, s] == v_o_est[z, k][s] - self.due_date[k] for z, k, s in pairs), name="aux01")

        auxiliary1 = model.addConstrs((aux_var1[z, k, s] == max_([aux_var00[z, k, s], 0]) for z, k, s in pairs), name="aux1")
        auxiliary2 = model.addConstrs((aux_var2[z, k, s] == max_([aux_var01[z, k, s], 0]) for z, k, s in pairs), name="aux2")
        auxiliary3 = model.addConstrs(
                (aux_var3[k, s] == self.demand[k]-gp.quicksum(x_pd[z, k, s] + x_over_pd[z, k, s] for z in supplier_agents if k in response[z]) for k, s in delta_pair),
                name="aux3")
        auxiliary4 = model.addConstrs((aux_var3[k, s] >= 0 for k, s in delta_pair), name="aux4")

        delta_t_constrs = model.addConstrs((delta_t[k, s] == gp.quicksum(lam_u[z, k, s] * aux_var1[z, k, s] +
                                                                       lam_o[z, k, s] * aux_var2[z, k, s]
                                                                       for z in supplier_agents if k in response[z]) for k, s in delta_pair), name="delta_t")
        delta_p_constrs = model.addConstrs((delta_p[k, s] == max_([aux_var3[k, s], 0])
                                                for k, s in delta_pair), name="delta_p")

        resp_constrs_pd = model.addConstrs((x_pd[z, k, s] + x_over_pd[z, k, s] <= (y_u_est[z, k][s] + y_o_est[z, k][s]) * lam_u[z, k, s]
                                                                                    for z, k, s in pairs), name="resp_limit_pd")
        resp_constrs_pd_over = model.addConstrs((x_over_pd[z, k, s] <= y_o_est[z, k][s] * lam_o[z, k, s] for z, k, s in pairs), name="resp_limit_pd_over")

        capacity_constrs_tp = model.addConstrs(
                (gp.quicksum(x_tp[z, k, s] for k in response[z].keys()) <= response[z][k]["remaining_cap_tp"]+0.1
                 for z, k, s in pairs), name="capacity_limit_tp")

        demand_constrs = model.addConstrs(
            (gp.quicksum(x_pd[z, k, s] + x_over_pd[z, k, s] for z in supplier_agents if k in response[z]) <= self.demand[k]
             for k, s in delta_pair), name="demand_limit")

        balance = model.addConstrs((x_tp[z, k, s] + x_over_tp[z, k, s] == x_pd[z, k, s] + x_over_pd[z, k, s]
                                        for z, k, s in pairs), name="balance")

        # result_constrs1 = model.addConstrs((y_u[z, k] == x_pd[z, k, s] for z, k, s in pairs), name="result_constrs1")
        #
        # result_constrs2 = model.addConstrs((y_o[z, k] == x_over_pd[z, k, s] for z, k, s in pairs), name="result_constrs2")


        model.optimize()
        status = model.status
        if status == GRB.Status.INFEASIBLE:
            print("Model is infeasible")
        # status = model.status
        # if status == GRB.Status.INFEASIBLE:
        #     print("Model is infeasible. Removing infeasible constraints and re-optimizing...")
        #
        #     # Identify infeasible constraints
        #     model.computeIIS()
        #     infeasible_constraints = [constr.constrName for constr in model.getConstrs() if constr.IISConstr]
        #
        #     # Remove infeasible constraints from the model
        #     model.remove(infeasible_constraints)
        #
        #     # Re-optimize the model
        #     model.optimize()

        x_u_sol = model.getAttr('x', x_pd)
        x_o_sol = model.getAttr('x', x_over_pd)
        x_o_sol_tp = model.getAttr('x', x_over_tp)
        y_u_sol = model.getAttr("x", y_u)
        y_o_sol = model.getAttr("x", y_o)
        selection_decision = {}
        over_flow, over_production = {}, {}
        for j in supplier_agents:
            selection_decision[j] = {}
            for k in response[j].keys():
                amount_u = round(mean([x_u_sol[j, k, s] for s in range(sce_num)]))
                amount_o = round(mean([x_o_sol[j, k, s] for s in range(sce_num)]))
                # amount_u = y_u_sol[j, k]
                # amount_o = y_o_sol[j, k]
                if amount_u + amount_o > 0.1:
                    selection_decision[j].update({k: amount_u + amount_o})
                if amount_o > 0.1:
                    over_production[(j, k)] = amount_o
                amount_o_tp = round(mean([x_o_sol_tp[j, k, s] for s in range(sce_num)]))
                if amount_o_tp > 0.1:
                    over_flow[(j, self.name, k)] = amount_o_tp

            if len(selection_decision[j].keys()) == 0:
                selection_decision.pop(j)

        # selection_decision["supplier_name"] = {"k1": 1, "k2": 1}
        new_flows = {}
        for sup_name in selection_decision.keys():
            for product in selection_decision[sup_name]:
                new_flows[(sup_name, self.name, product)] = selection_decision[sup_name][product]

        return selection_decision, new_flows, over_production, over_flow

    def truncated_normal_distribution(self, mean_value, std_value, sample_num):
        # samples are truncated from 0 to mean+3std
        if std_value == 0:
            return [mean_value] * sample_num

        a = (0 - mean_value) / std_value
        b = (mean_value + 3 * std_value - mean_value) / std_value
        samples = truncnorm.rvs(a, b, loc=mean_value, scale=std_value, size=sample_num)
        samples = samples.round().astype(int)

        return samples