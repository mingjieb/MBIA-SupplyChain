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
from gurobipy import GRB


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
        self.explore = False
        self.used = False
        self.depth = 0
        self.demand = dict()

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
        # current_inflow_agents = []
        # for flow_key in self.state.inflow.keys():
        #     if flow_key[0] not in current_inflow_agents:
        #         current_inflow_agents.append(flow_key[0])

        supplier_agents = {}
        for product in self.demand.keys():
            supplier_agents[product] = []
            for upstream_agent in self.environment.upstream_agent[product]:
                if not upstream_agent.down:
                    # only check current in-network agents
                    if not self.explore and upstream_agent.used:
                        supplier_agents[product].append(upstream_agent)
                    # explore other agent in network but not in environment
                    elif self.explore and not upstream_agent.used:
                        supplier_agents[product].append(upstream_agent)

        return supplier_agents

    # demand agent sends request to supplier agents
    def send_request(self, supplier_agents):
        for product in supplier_agents.keys():
            # req = {product: self.demand[product]}
            for sup_ag in supplier_agents[product]:
                # Store the request information
                try:
                    self.communication_manager.delivered_request[sup_ag.name].update({product: self.demand[product]})
                    sup_ag.communication_manager.received_request[self.name].update({product: self.demand[product]})
                except:
                    self.communication_manager.delivered_request[sup_ag.name] = {product: self.demand[product],
                                                                                 "reqToAgent": sup_ag}
                    sup_ag.communication_manager.received_request[self.name] = {product: self.demand[product],
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
                                         "remaining_cap_tp": transportation.get_normal_available_capacity(self.name, ag_name)}})
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
            ag_dm.communication_manager.received_response[self.name] = {"response": resp,  "reqFromAgent": self}

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

        delta = model.addVars(self.demand.keys(), vtype=GRB.INTEGER, name="delta")

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
            obj = model.setObjective(gp.quicksum(response[i][k]["cost_pd"] * x_pd[i, k] + 2 * response[i][k]["cost_pd"] * x_over_pd[i, k]
                                                 + response[i][k]["cost_tp"] * x_tp[i, k] + 2 * response[i][k]["cost_tp"] * x_over_tp[i, k]
                                                 - 1e8*(x_pd[i, k]+x_over_pd[i, k])
                                                 for i in supplier_agents for k in response[i].keys()), GRB.MINIMIZE)

        resp_constrs_pd = model.addConstrs((x_pd[i, k]+x_over_pd[i, k] <= response[i][k]["amount"] * zeta[i]
                                       for i in supplier_agents for k in response[i].keys()), name="resp_limit_pd")

        resp_constrs_tp = model.addConstrs((x_tp[i, k] + x_over_tp[i, k] <= response[i][k]["amount"]
                                         for i in supplier_agents for k in response[i].keys()), name="resp_limit_tp")

        capacity_constrs_pd = model.addConstrs((gp.quicksum(x_pd[i, k] for k in response[i].keys()) <= response[i][k]["remaining_cap_pd"] * zeta[i]
                                         for i in supplier_agents for k in response[i].keys()), name="capacity_limit_pd")

        capacity_constrs_tp = model.addConstrs(
            (gp.quicksum(x_tp[i, k] for k in response[i].keys()) <= response[i][k]["remaining_cap_tp"]
             for i in supplier_agents for k in response[i].keys()), name="capacity_limit_tp")

        balance = model.addConstrs((x_tp[i, k] + x_over_tp[i, k] == x_pd[i, k] + x_over_pd[i, k]
             for i in supplier_agents for k in response[i].keys()), name="balance")

        demand_constrs = model.addConstrs((gp.quicksum(x_pd[i, k]+x_over_pd[i, k] for i in supplier_agents if k in response[i]) <= self.demand[k]
                                           for k in self.demand.keys()), name="demand_limit")

        priority_constrs = model.addConstrs((zeta[i] == 1  for i in used_agent), name="demand_limit")


        model.optimize()
        xsol = model.getAttr('x', x_pd)
        x_over_sol = model.getAttr('x', x_over_pd)
        x_over_sol_tp = model.getAttr('x', x_over_tp)
        selection_decision = {}
        over_flow, over_production = {}, {}
        for i in supplier_agents:
            selection_decision[i] = {}
            for k in response[i].keys():
                if xsol[i, k]+x_over_sol[i, k] > 0.1:
                    selection_decision[i].update({k: xsol[i, k]+x_over_sol[i, k]})
                if x_over_sol[i, k] > 0.1:
                    over_production[(i, k)] = x_over_sol[i, k]
                if x_over_sol_tp[i, k] > 0.1:
                    over_flow[(i, self.name, k)] = x_over_sol_tp[i, k]
            if len(selection_decision[i].keys()) == 0:
                selection_decision.pop(i)

        # selection_decision["supplier_name"] = {"k1": 1, "k2": 1}
        new_flows = {}
        for sup_name in selection_decision.keys():
            for product in selection_decision[sup_name]:
                new_flows[(sup_name, self.name, product)] = selection_decision[sup_name][product]
        
        return selection_decision, new_flows, over_production, over_flow

    # demand agent check demand
    def check_demand(self, new_flows):
        flag = True
        for product in list(self.demand.keys()):
            actual_get = 0
            for flow in new_flows.items():
                if self.name == flow[0][1] and product == flow[0][2]:
                    actual_get += flow[1]
            if abs(actual_get- self.demand[product]) < 0.1:
                self.demand.pop(product)
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
        self.explore = True
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
        if 1.3*self.capability.get_capacity() - total_production > 0:
            return True
        else:
            return False

    # get the remaining capacity considering over capacity
    def get_remaining_capacity(self):
        total_production = 0
        for product in self.state.production.keys():
            total_production += self.state.production[product]
        return 1.3*self.capability.get_capacity() - total_production

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

        demand_constrs = model.addConstrs((gp.quicksum(gp.quicksum(x[j, k] for j in downstream[k]) * self.capability.characteristics["Production"][k]["Material"][c] for k in product_structure[c]) >= self.demand[c]
                                           for c in self.demand.keys()), name="demand_limit")
        flow_constrs = model.addConstrs((x[j, k] <= self.state.outflow[(j, k)] for k in K for j in downstream[k]), name="downflow_limit")

        model.optimize()
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
        obj = model.setObjective(gp.quicksum(self.state.inflow[(i, k)] - x[i, k] for k in upstream.keys() for i in upstream[k]), GRB.MINIMIZE)

        demand_constrs = model.addConstrs((gp.quicksum(x[i, k] for i in upstream[k]) <= total_need[k] for k in upstream.keys()), name="demand_limit")

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
