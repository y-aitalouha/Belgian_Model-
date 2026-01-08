# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 14:01:12 2021

@author: Jocelyn Mbenoun
"""

# =============================================================================
# Post processor file for the 3 cluster model. This file is created based on the 
# post processor file of the one cluster model. underneath, additional code and/or 
# function needs are highlighted. All code should be applicable to the 3 cluster model, 
# since only adapted code, ready for the 3 cluster model is pasted in this file.
# =============================================================================


# =============================================================================
# 
# =============================================================================

import os
import sys
import json
import csv
import calendar
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as mpatches
from termcolor import colored
from gboml import GbomlGraph
from gboml.compiler.classes import Expression 
import argparse 
from statistics import mean
import seaborn  as sns
import matplotlib.colors as mcolors 
import matplotlib 
import GBOML_function as gf

#%% N°1 : def get_cluster_variable(node,variable,dictionary): 


def get_cluster_variable(node,variable,dictionary): 
    # get value of "variable" from "cluster" as a list in "node" from data in "dictionary"  
    return dictionary["solution"]["elements"][node]["variables"][variable]



#%% N°2 : def get_cluster_element_variable(cluster,element,variable,dictionary): 

def get_cluster_element_variable(cluster,element,variable,dictionary): 
    # get value of "variable" from "cluster" as a list in "node" from data in "dictionary"  
    if "variables" in dictionary["solution"]["elements"][cluster]["sub_elements"][element]:
        if variable in dictionary["solution"]["elements"][cluster]["sub_elements"][element]["variables"]:
            return dictionary["solution"]["elements"][cluster]["sub_elements"][element]["variables"][variable]
        else:
            return 0
    else:
        return 0

#%% N°3 : def get_cluster_parameter(node,parameter,dictionary):

def get_cluster_parameter(node,parameter,dictionary):
    # get value of "parameter" as a list in "node" from data in "dictionary" 
    return dictionary["model"]["nodes"][node]["parameters"][parameter]

#%% N°4 : def get_cluster_element_parameter(cluster,element,parameter,dictionary):

def get_cluster_element_parameter(cluster,element,parameter,dictionary):
    # get value of "parameter" as a list in "node" from data in "dictionary" 
    if "parameters" in dictionary["model"]["nodes"][cluster]["sub_nodes"][element]:
        if parameter in dictionary["model"]["nodes"][cluster]["sub_nodes"][element]["parameters"]:
            return dictionary["model"]["nodes"][cluster]["sub_nodes"][element]["parameters"][parameter]
        else:
            return [0]
    else:
        return [0]

#%% N°5 : def get_all_cluster_names(dictionary): 

def get_all_cluster_names(dictionary): 
    # get the names of all nodes as a list from data in "dictionary"
    dic_nodes = dictionary["model"]["nodes"]
    nodes_name = []
    for node in dic_nodes:
        nodes_name.append(node)
    return nodes_name

#%% N°6 : def get_all_cluster_subnodes_names(cluster,dictionary): 

def get_all_cluster_subnodes_names(cluster,dictionary): 
    # get the names of all nodes as a list from data in "dictionary"
    dic_nodes = dictionary["model"]["nodes"][cluster]["sub_nodes"]
    nodes_name = []
    for node in dic_nodes:
        nodes_name.append(node)
    return nodes_name

#%% N°7 : def get_cluster_names_from_variable(variable,dictionary): 
def get_cluster_names_from_variable(variable,dictionary): 
    # get the names of nodes as a list in which the variable named "variable" is used
    dic_nodes = dictionary["model"]["nodes"]
    nodes_name = []
    for node in dic_nodes:
        if variable in dic_nodes[node]["variables"]:
            nodes_name.append(node)
    return nodes_name

#%% N°8 : def get_cluster_subnodes_names_from_variable(variable,cluster,dictionary): 

def get_cluster_subnodes_names_from_variable(variable,cluster,dictionary): 
    # get the names of nodes as a list in which the variable named "variable" is used
    dic_nodes = dictionary["solution"]["elements"][cluster]["sub_elements"]
    nodes_name = []
    for node in dic_nodes:
        if "variables" in dic_nodes[node]:
            if variable in dic_nodes[node]["variables"]:
                nodes_name.append(node)
    return nodes_name

#%% N°9 : def get_cluster_names_from_parameter(parameter,dictionary):

def get_cluster_names_from_parameter(parameter,dictionary):
    # get the names of global nodes as a list in which the "parameter" is used
    dic_nodes = dictionary["model"]["nodes"]
    nodes_name = []
    for node in dic_nodes:
        if parameter in dic_nodes[node]["parameters"]:
            nodes_name.append(node)
    return nodes_name

#%% N°10 : def get_cluster_subnodes_names_from_parameter(cluster,parameter,dictionary):

def get_cluster_subnodes_names_from_parameter(cluster,parameter,dictionary):
    # get the names of nodes as a list in which the "parameter" is used
    dic_nodes = dictionary["model"]["nodes"][cluster]["sub_nodes"]
    nodes_name = []
    for node in dic_nodes:
        if parameter in dic_nodes[node]["parameters"]:
            nodes_name.append(node)
    return nodes_name
#%% N°11 : def get_cluster_capacities_from_nodes(nodes,name_capacity,name_capacity_0,name_capacity_max,dictionary):

def get_cluster_capacities_from_nodes(nodes,dictionary,name_capacity="new_capacity",
                                      name_capacity_0="pre_installed_capacity",name_capacity_max="max_capacity"):
    # Create a dictionary with the capacity, the limit on the capacity and the preinstalled capacity for each node in the list
    # "nodes". "new_capacity" is the name of the variable corresponding to the capacity, "name_capacity_0" is the name used for
    # parameter corresponding to the preinstalled capacity and "name_capacity_max" is the parameter corresponding to the maximum 
    # capacity that can be installed
    # if no preinstalled capacity or max capacity used in the code, just insert a empty char for those inputs like that: ''
    capacities = {}
    dic_nodes_var = dictionary["solution"]["elements"]
    dic_nodes_par = dictionary["model"]["nodes"]
    for node in nodes:  
        if name_capacity in dic_nodes_var[node]["variables"]:
            capacity = get_cluster_variable(node,name_capacity,dictionary)
            capacity = capacity['values'][0]
        else:
            capacity = 0
        if name_capacity_0 in dic_nodes_par[node]["parameters"]:
            capacity_0 = get_cluster_parameter(node,name_capacity_0,dictionary)
            capacity_0 = capacity_0[0]
        else:
            capacity_0 = 0
        if name_capacity_max in dic_nodes_par[node]["parameters"]:
            capacity_max = get_cluster_parameter(node,name_capacity_max,dictionary)
            capacity_max = capacity_max[0]
        else:
            capacity_max = 'Not given'
        total_capacity = capacity_0 + capacity
        key = node
        capacities[key] = {"Preinstalled capacity":capacity_0,"Added capacity":capacity, "Total capacity":total_capacity, "Max capacity": capacity_max}
    return capacities

#%% N°12 : def get_cluster_subnodes_capacities_from_nodes(nodes,cluster,name_capacity,name_capacity_0,name_capacity_max,dictionary):

def get_cluster_subnodes_capacities_from_nodes(nodes,cluster,dictionary,name_capacity="new_capacity",
                                               name_capacity_0="pre_installed_capacity",name_capacity_max="max_capacity"):
    # Create a dictionary with the capacity, the limit on the capacity and the preinstalled capacity for each node in the list
    # "nodes". "new_capacity" is the name of the variable corresponding to the capacity, "name_capacity_0" is the name used for
    # parameter corresponding to the preinstalled capacity and "name_capacity_max" is the parameter corresponding to the maximum 
    # capacity that can be installed
    # if no preinstalled capacity or max capacity used in the code, just insert a empty char for those inputs like that: ''
    capacities = {}
    dic_nodes_var = dictionary["solution"]["elements"][cluster]["sub_elements"]
    dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]
    for node in nodes:  
        if name_capacity in dic_nodes_var[node]["variables"]:
            capacity = get_cluster_element_variable(cluster,node,name_capacity,dictionary)
            capacity = capacity['values'][0]
        else:
            capacity = 0
        if name_capacity_0 in dic_nodes_par[node]["parameters"]:
            capacity_0 = get_cluster_element_parameter(cluster,node,name_capacity_0,dictionary)
            capacity_0 = capacity_0[0]
        else:
            capacity_0 = 0
        if name_capacity_max in dic_nodes_par[node]["parameters"]:
            capacity_max = get_cluster_element_parameter(cluster,node,name_capacity_max,dictionary)
            capacity_max = capacity_max[0]
        else:
            capacity_max = 'Not given' 
            
        total_capacity = capacity_0 + capacity
        key = node
        capacities[key] = {"Preinstalled capacity":capacity_0,"Added capacity":capacity, "Total capacity":total_capacity, "Max capacity": capacity_max}
        
    return capacities 


#%% N°12 bis: def get_cluster_subnodes_total_capacities_from_nodes(nodes,cluster,name_capacity,name_capacity_0,name_capacity_max,dictionary):

def get_cluster_subnodes_total_capacities_from_nodes(nodes,cluster,dictionary,name_capacity="new_capacity",
                                                     name_capacity_0="pre_installed_capacity",name_capacity_max="max_capacity"):
    # Create a dictionary with the capacity, the limit on the capacity and the preinstalled capacity for each node in the list
    # "nodes". "new_capacity" is the name of the variable corresponding to the capacity, "name_capacity_0" is the name used for
    # parameter corresponding to the preinstalled capacity and "name_capacity_max" is the parameter corresponding to the maximum 
    # capacity that can be installed
    # if no preinstalled capacity or max capacity used in the code, just insert a empty char for those inputs like that: ''
    capacities = {}
    dic_nodes_var = dictionary["solution"]["elements"][cluster]["sub_elements"]
    dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]
    for node in nodes:  
        if name_capacity in dic_nodes_var[node]["variables"]:
            capacity = get_cluster_element_variable(cluster,node,name_capacity,dictionary)
            capacity = capacity['values'][0]
        else:
            capacity = 0
        if name_capacity_0 in dic_nodes_par[node]["parameters"]:
            capacity_0 = get_cluster_element_parameter(cluster,node,name_capacity_0,dictionary)
            capacity_0 = capacity_0[0]
        else:
            capacity_0 = 0
        if name_capacity_max in dic_nodes_par[node]["parameters"]:
            capacity_max = get_cluster_element_parameter(cluster,node,name_capacity_max,dictionary)
            capacity_max = capacity_max[0]
        else:
            capacity_max = 'Not given'
        total_capacity = capacity_0 + capacity
        key = node
        capacities[key] = {"Total capacity":total_capacity}
    return capacities

#%% N°13 : def get_cluster_subnodes_capacities_from_storage(nodes,cluster,name_capacity_power,name_capacity_0_power,name_capacity_max_power,name_capacity_energy,name_capacity_0_energy,name_capacity_max_energy,dictionary):

def get_cluster_subnodes_capacities_from_storage(nodes,cluster,dictionary,name_capacity_power= "new_power_capacity",
                                                name_capacity_0_power= "pre_installed_capacity_power",
                                                name_capacity_max_power= "max_capacity_power",
                                                name_capacity_energy= "new_energy_capacity",
                                                name_capacity_0_energy= "pre_installed_capacity_energy",
                                                name_capacity_max_energy= "max_capacity_energy"):
    # Create a dictionary with the capacity of energy and power, the limit on those capacities and their preinstalled capaciies 
    # for each node in the list "nodes". "new_capacity" is the name of the variable corresponding to the capacity, "name_capacity_0" 
    # is the name used for parameter corresponding to the preinstalled capacity and "name_capacity_max" is the parameter
    # corresponding to the maximum capacity that can be installed
    # if no preinstalled capacity or max capacity used in the code, just insert a empty char for those inputs like that ''
    
    cap_storage = {}
    dic_nodes_var = dictionary["solution"]["elements"][cluster]["sub_elements"]
    for node in nodes:

        # for power
        if name_capacity_power in dic_nodes_var[node]["variables"]:
            capacity = get_cluster_element_variable(cluster,node,name_capacity_power,dictionary)
            capacity = capacity['values'][0]
        else:
            capacity = 0
        if name_capacity_0_power in dictionary["model"]["nodes"][cluster]["sub_nodes"][node]["parameters"]:
            capacity_0 = get_cluster_element_parameter(cluster,node,name_capacity_0_power,dictionary)
            capacity_0 = capacity_0[0]
        else:
            capacity_0 = 0
        if name_capacity_max_power in dictionary["model"]["nodes"][cluster]["sub_nodes"][node]["parameters"]:
            capacity_max = get_cluster_element_parameter(cluster,node,name_capacity_max_power,dictionary)
            capacity_max = capacity_max[0]
        else:
            capacity_max = 'Not given'
        total_capacity = capacity_0 + capacity 
        key = node + ' power'
        cap_storage[key] = {"Preinstalled capacity":capacity_0,"Added capacity":capacity, "Total capacity":total_capacity, "Max capacity": capacity_max}
        
        # for energy
        if name_capacity_energy in dic_nodes_var[node]["variables"]:
            capacity = get_cluster_element_variable(cluster,node,name_capacity_energy,dictionary)
            capacity = capacity['values'][0]
        else:
            capacity = 0
        if name_capacity_0_energy in dictionary["model"]["nodes"][cluster]["sub_nodes"][node]["parameters"]:
            capacity_0 = get_cluster_element_parameter(cluster,node,name_capacity_0_energy,dictionary)
            capacity_0 = capacity_0[0]
        else:
            capacity_0 = 0
        if name_capacity_max_energy in dictionary["model"]["nodes"][cluster]["sub_nodes"][node]["parameters"]:
            capacity_max = get_cluster_element_parameter(cluster,node,name_capacity_max_energy,dictionary)
            capacity_max = capacity_max[0]
        else:
            capacity_max = 'Not given'
        total_capacity = capacity_0 + capacity 
        key = node + ' energy'
        cap_storage[key] = {"Preinstalled capacity":capacity_0,"Added capacity":capacity, "Total capacity":total_capacity, "Max capacity": capacity_max}
    return cap_storage

#%% N°14 : def get_cluster_subnodes_technology_costs_from_nodes(nodes,cluster,e_produced,conversion_efficiency,fuel_cost,dictionary):

def get_cluster_subnodes_technology_costs_from_nodes(nodes,cluster,variable,conversion_efficiency,fuel_cost,dictionary):
    # Create a dictionary with the capacity, the limit on the capacity and the preinstalled capacity for each node in the list
    # "nodes". "new_capacity" is the name of the variable corresponding to the capacity, "name_capacity_0" is the name used for
    # parameter corresponding to the preinstalled capacity and "name_capacity_max" is the parameter corresponding to the maximum 
    # capacity that can be installed
    # if no preinstalled capacity or max capacity used in the code, just insert a empty char for those inputs like that: ''
    capacities = {}
    dic_nodes_var = dictionary["solution"]["elements"][cluster]["sub_elements"]
    dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]
    for node in nodes:  
        if variable in dic_nodes_var[node]["variables"]:
            var = sum(get_cluster_element_variable(cluster,node,variable,dictionary)['values'])
        else:
            capacity = 0
            var = 0
        if conversion_efficiency in dic_nodes_par[node]["parameters"]:
            eff = get_cluster_element_parameter(cluster,node,conversion_efficiency,dictionary)[0]
        else:
            eff = 'Not given'
        if fuel_cost in dic_nodes_par[node]["parameters"]:
            fu_cost = get_cluster_element_parameter(cluster,node,fuel_cost,dictionary)[0]
        else:
            fu_cost = 'Not given'
        key = node
        if fu_cost == 'Not given' or eff == 'Not given':
            capacities[key] = {"conversion_efficiency":eff,variable:var, "fuel_price": fu_cost, "total_fuel_cost":'Not given'}
        else:
            capacities[key] = {"conversion_efficiency":eff,variable:var, "fuel_price": fu_cost, "total_fuel_cost":fu_cost*var/eff}
    return capacities

#%% N°15 : def get_total_value_of_variables_in_cluster_subnodes(variables,cluster,nodes,dictionary):

def get_total_value_of_variables_in_cluster_subnodes(variables,cluster,nodes,dictionary):
    # create a dictionary with sum of of all elements of each vectorial variable in the list "variables" for each node in the list "nodes"
    total_variables = {}
    dic_nodes = dictionary["solution"]["elements"][cluster]["sub_elements"]
    for node in nodes:
        total_variables[node] = {} # initialization
        for variable in variables:
            if variable in dic_nodes[node]["variables"]:
                total = sum(dic_nodes[node]["variables"][variable]['values'])
            else:
                total = 0
            total_variables[node][variable] = total
    return total_variables

#%% N°16 : def get_total_value_of_global_parameters(parameters,dictionary):

def get_total_value_of_global_parameters(parameters,dictionary):
    total_parameters = {}
    dic_nodes = dictionary["model"]["global_parameters"]
    for parameter in parameters:
        if parameter in dic_nodes:
            total = sum(dic_nodes[parameter])
        else:
            total = 0
        total_parameters[parameter] = {"Total value":total}
    return total_parameters

#%% N°16bis : def get_timeseries_of_global_parameters(dictionary, parameters):

def get_timeseries_of_global_parameters(dictionary, parameters):
    global_parameter = {}
    dic_nodes = dictionary["model"]["global_parameters"]
    if isinstance(parameters, list):
        for parameter in parameters:
            if parameter in dic_nodes:
                global_parameter[parameter] = dic_nodes[parameter]
            else:
                pass
    else:
        if parameters in dic_nodes:
            global_parameter = dic_nodes[parameter]
    return global_parameter
#%% N°17 : def get_capacity_factors_from_capacity(variable,cluster,nodes,capacities,dictionary):

def get_capacity_factors_from_capacity(variable,cluster,nodes,capacities,dictionary):
    # create a dictionary calculating the capacity factor of each node in the list "nodes" using the dictionary "capacities" 
    # created by the function "get_capacities_from_nodes" and "get_capacities_from_storage" and the name of variable "variable"
    # as references for the capacity factor
    capacity_factors = {}
    dic_nodes = dictionary["solution"]["elements"][cluster]["sub_elements"]
    for node in nodes:
        if node in capacities:
            capacity = capacities[node]["Total capacity"]
            if capacities[node]["Total capacity"] > 0:
                total_production = sum(dic_nodes[node]["variables"][variable]['values'])
                capacity_factor = sum(dic_nodes[node]["variables"][variable]['values'])/(capacities[node]["Total capacity"]*len(dic_nodes[node]["variables"][variable]['values']))
            else:
                total_production = 0
                capacity_factor = "No capacity installed"
            capacity_factors[node] = {"Capacity": capacity, "Total production": total_production, "Capacity factor": capacity_factor}   
    return capacity_factors


#%% N°24 : def get_capex_from_cluster_subnodes_capacity(cluster,capex_name,capacities,dictionary):

def get_capex_from_cluster_subnodes_capacity(cluster, capex_name, capacities, dictionary):
    capex_all = {}
    dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]

    for node in capacities:
        # Nettoyage du nom s’il est mal formé
        clean_node = node.replace(" power", "").strip()
        if clean_node not in dic_nodes_par:
            print(f"[Warning] Node '{clean_node}' not found in cluster '{cluster}' → skipped.")
            continue

        capex = 0
        if isinstance(capex_name, str):
            if capex_name in dic_nodes_par[clean_node]["parameters"]:
                capex = dic_nodes_par[clean_node]["parameters"][capex_name][0]
        elif isinstance(capex_name, list):
            for capex_buffer in capex_name:
                if capex_buffer in dic_nodes_par[clean_node]["parameters"]:
                    capex = dic_nodes_par[clean_node]["parameters"][capex_buffer][0]
                    break

        try:
            add_cap = capacities[node]["Added capacity"]
        except KeyError:
            print(f"[Warning] 'Added capacity' not found for node '{node}' → set to 0.")
            add_cap = 0

        capex_all[node] = {
            "Capex": round(capex, 3),
            "Added capacity": round(add_cap, 3),
        }

    return capex_all

#%% N°25 : def get_fom_from_cluster_subnodes_capacity(cluster,fom_name,capacities,dictionary):

def get_fom_from_cluster_subnodes_capacity(cluster,fom_name,capacities,dictionary):
    # create a dictionary calculating the total fixed operation and maintenance cost of each node where 
    # a capacity is calculated from the name used for the fom in node and the dictionary of capacity
    fom_all = {}
    dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]
    for node in capacities: 
        if isinstance(fom_name, str):
            if fom_name in dic_nodes_par[node]["parameters"]:
                fom = dic_nodes_par[node]["parameters"][fom_name][0]
            else:
                fom = 0
        elif isinstance(fom_name, list):
            for fom_buffer in fom_name:
                if fom_buffer in dic_nodes_par[node]["parameters"]:
                    fom += dic_nodes_par[node]["parameters"][fom_buffer][0]
                    break
                else:
                    fom = 0
        tot_cap = capacities[node]["Total capacity"]
        fom_cost = fom * tot_cap 
        fom_all[node] = {
            "Fom": round(fom, 3),
            "Total capacity": round(tot_cap, 3),
            "tot fom cost": round(fom_cost, 3)
        }
    return fom_all    

#%% N°26 : def get_vom_from_cluster_subnodes_variable(cluster,vom_name,variable,nodes,dictionary):

def get_vom_from_cluster_subnodes_variable(cluster,vom_name,variable,nodes,dictionary):
    vom_all = {}
    dic_nodes_var = dictionary["solution"]["elements"][cluster]["sub_elements"]
    dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]
    for node in nodes:
        total_prod = sum(dic_nodes_var[node]["variables"][variable]['values'])
        if isinstance(vom_name, str):
            if vom_name in dic_nodes_par[node]["parameters"]:
                vom = dic_nodes_par[node]["parameters"][vom_name][0]
            else:
                vom = 0
        elif isinstance(vom_name, list):
            for vom_buffer in vom_name:
                if vom_buffer in dic_nodes_par[node]["parameters"]:
                    vom += dic_nodes_par[node]["parameters"][vom_buffer][0]
                    break
                else:
                    vom = 0
        vom_cost = total_prod * vom
        vom_all[node] = {
            "Vom": round(vom, 3),
            "Total production": round(total_prod, 3),
            "tot vom cost": round(vom_cost, 3)
        }
    return vom_all



def get_vom_from_cluster_storage_variable(cluster, vom_name, variable, nodes, dictionary):
    """
    Calcule le VOM total pour chaque noeud de stockage (power/energy) en fonction de leur production.
    """
    vom_all = {}
    dic_nodes_var = dictionary["solution"]["elements"][cluster]["sub_elements"]
    dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]

    for node in nodes:
        # Extraire le nom réel du sous-noeud
        if " power" in node:
            base_node = node.replace(" power", "")
        elif " energy" in node:
            base_node = node.replace(" energy", "")
        else:
            base_node = node

        if base_node not in dic_nodes_par or base_node not in dic_nodes_var:
            print(f"[Warning] Node '{base_node}' not found in cluster '{cluster}' → skipped.")
            continue

        try:
            if 'discharged' in variable[0]:
                total_charged = sum(dic_nodes_var[base_node]["variables"][variable[1]]['values'])
                total_discharged = sum(dic_nodes_var[base_node]["variables"][variable[0]]['values'])
                state_of_charge = sum(dic_nodes_var[base_node]["variables"]['state_of_charge']['values'])
                
            else: 
                total_charged = sum(dic_nodes_var[base_node]["variables"][variable[0]]['values'])
                total_discharged = sum(dic_nodes_var[base_node]["variables"][variable[1]]['values']) 
                state_of_charge = sum(dic_nodes_var[base_node]["variables"]['state_of_charge']['values'])
                
        except KeyError:
            # print(f"[Warning] Variable '{variable}' not found for node '{base_node}' → set to 0.")
            total_charged = 0
            total_discharged = 0
            state_of_charge = 0
            
            vom_all[node] = {
            "Total charged": round(total_charged, 3),
            "Total discharged": round(total_discharged, 3), 
            'State of charge': round(state_of_charge, 3)
        }

        vom = 0
        if isinstance(vom_name, str):
            if vom_name in dic_nodes_par[base_node]["parameters"]:
                vom = dic_nodes_par[base_node]["parameters"][vom_name][0]
        elif isinstance(vom_name, list):
            for vom_buffer in vom_name:
                if vom_buffer in dic_nodes_par[base_node]["parameters"]:
                    vom = dic_nodes_par[base_node]["parameters"][vom_buffer][0]
                    break

        vom_all[node] = {
            "Vom": round(vom, 3),
            "Total charged": round(total_charged, 3),
            "Total discharged": round(total_discharged, 3),
            "State of charge": round(state_of_charge, 3)
        }

    return vom_all


#%% N°27 : def get_total_cluster_storage_cost(capex_dict,fom_dict,vom_dict):


def get_total_cluster_storage_cost(capex_dict,fom_dict,vom_dict, obj_dict, all_var = 'yes', type_node = None):
    
    total_cost = {}
    for node in capex_dict: 
        if ' power' in node:
            capacity_power = fom_dict[node]["Total capacity"]
            continue
            
        elif ' energy' in node:
            capacity_energy = fom_dict[node]["Total capacity"]
        
        else:
            capacity_power = 0
            capacity_energy = 0
        
        capex = capex_dict[node]["Capex"]
        if node in fom_dict: 
            fom = fom_dict[node]["Fom"]
        else: 
            fom = 0
        if node in vom_dict:
            total_charged = vom_dict[node]["Total charged"]
            vom = vom_dict[node]["Vom"]
            total_discharged = vom_dict[node]["Total discharged"] 
            state_of_charge = vom_dict[node]["State of charge"]
        else: 
            vom = 0  
            total_discharged = 0
            total_charged = 0
            state_of_charge = 0
            
        # Remove ' power' or ' energy' suffix from node for lookup
        base_node = node.replace(' power', '').replace(' energy', '')
        
        if base_node in obj_dict:
            tot_cost = obj_dict[base_node]['Total cost [M€]'] 
            energy_cost = obj_dict[base_node]['Cost energy [M€]'] 
            power_cost = obj_dict[base_node]['Cost power [M€]'] 
            
        else:
            tot_cost = 0 
            energy_cost = 0
            power_cost = 0
        
        
        
        if all_var == 'yes':
            if type_node is None:
                metrics = {
                    "CAPEX [M€/Gw]":      round(capex, 3),
                    "FOM [M€/Gw]":        round(fom, 3),
                    "VOM [M€/(Gw.y)]":    round(vom, 3),   
                    'State of charge [TWh/y]': round(state_of_charge, 3),
                    "Total capacity energy [GWh]":      round(capacity_energy, 3),
                    'Cost energy [M€]':         round(energy_cost, 3),
                    'Total discharged [TWh/y]': round(total_discharged/1000, 3),
                    'Total charged [TWh/y]': round(total_charged/1000, 3),
                    "Total capacity power [GW]":      round(capacity_power, 3),
                    'Cost power [M€]':         round(power_cost, 3),
                    'Total Cost [M€]':         round(tot_cost, 3),
                    # on retire la clé "Total Cost [€/MWh]" ici
                }
            else:
                metrics = {
                    "CAPEX [M€/(kton/h)]":    round(capex, 3),
                    "FOM [M€/(kton/h)]":      round(fom, 3),
                    "VOM [M€/(kton/h).y]":    round(vom, 3),   
                    'State of charge [kton/y]': round(state_of_charge, 3),
                    "Total capacity energy [kton/h]":      round(capacity_energy, 3),
                    'Cost energy [M€]':         round(energy_cost, 3),
                    'Total discharged [kton/y]': round(total_discharged/1000, 3),
                    'Total charged [kton/y]': round(total_charged/1000, 3),
                    "Total capacity power":      round(capacity_power, 3),
                    'Cost power [M€]':         round(power_cost, 3),
                    'Total Cost [M€]':         round(tot_cost, 3),
                    # on retire la clé "Total Cost [€/ton]" ici
                }
        else:
            # même structure, juste sans CAPEX/FOM/VOM
            if type_node is None:
                metrics = {   
                    'State of charge [TWh/y]': round(state_of_charge/1000, 3),
                    "Total capacity energy [GWh]":      round(capacity_energy, 3),
                    'Total discharged [TWh/y]': round(total_discharged/1000, 3),
                    'Total charged [TWh/y]': round(total_charged/1000, 3),
                    "Total capacity power [GW]":      round(capacity_power, 3),
                    'Cost energy [M€]':         round(energy_cost, 3),
                    'Cost power [M€]':         round(power_cost, 3),
                    'Total Cost [M€]':         round(tot_cost, 3),
                }
            else:
                metrics = {   
                    'State of charge [kton/y]': round(state_of_charge/1000, 3),
                    "Total capacity energy":      round(capacity_energy, 3), 
                    'Total discharged [kton/y]': round(total_discharged/1000, 3),
                    'Total charged [kton/y]': round(total_charged/1000, 3),
                    "Total capacity power":      round(capacity_power, 3),
                    'Cost energy [M€]':         round(energy_cost, 3),
                    'Cost power [M€]':         round(power_cost, 3),
                    'Total Cost [M€]':         round(tot_cost, 3),
                }
                    
                    
        # Affectation finale
        total_cost[base_node] = metrics
                        
    return total_cost

#%% N°28 : def get_cluster_objective(cluster, objective_elem,dictionary):

def get_cluster_objective(cluster, objective_elem,dictionary):
    # Get the element "objective_elem from the objective results of subnode in cluster
    if "objectives" in dictionary["solution"]["elements"][cluster]:
        if "named" not in dictionary["solution"]["elements"][cluster]["objectives"]:
            return 'check this subnodes objective'
        elif objective_elem in dictionary["solution"]["elements"][cluster]["objectives"]["named"]:
                return dictionary["solution"]["elements"][cluster]["objectives"]['named'][objective_elem]
        else:
            return 0
    else:
        return 0

#%% N°29 : def get_objective_element(cluster,subnode,objective_elem,dictionary):

def get_objective_element(cluster,subnode,objective_elem,dictionary):
    # Get the element "objective_elem from the objective results of subnode in cluster
    if "objectives" in dictionary["solution"]["elements"][cluster]["sub_elements"][subnode]:
        if "named" not in dictionary["solution"]["elements"][cluster]["sub_elements"][subnode]["objectives"]:
            return 'check this subnodes objective'
        elif objective_elem in dictionary["solution"]["elements"][cluster]["sub_elements"][subnode]["objectives"]["named"]:
                return dictionary["solution"]["elements"][cluster]["sub_elements"][subnode]["objectives"]['named'][objective_elem]
        else:
            return 0
    else:
        return 0

    
#%% N°33 : def merge_dictionaries(*dictionaries):

def merge_dictionaries(*dictionaries, name=None):
  
    dict_merged = {}

    for idx, data in enumerate(dictionaries):
        suffix = f" ({name[idx]})" if name and idx < len(name) else ""

        if isinstance(data, dict):
            # chaque (clé, valeur) devient (clé + suffix)→valeur
            for k, v in data.items():
                dict_merged[f"{k}{suffix}"] = v

        elif isinstance(data, list):
            # on encapsule la liste sous la clé "Value"
            dict_merged[f"Value{suffix}"] = data

        else:
            # scalaire, on l’encapsule aussi
            dict_merged[f"Value{suffix}"] = data

    return dict_merged

def merge_dictionaries_replace_keys(*dictionaries, name=None):
    """
    Fusionne les dictionnaires et remplace leurs clés internes par les noms fournis.
    Format final : { 'DENMARK': valeur, 'FRANCE': valeur, ... }
    """
    merged = {}

    for idx, data in enumerate(dictionaries):
        key = name[idx] if name and idx < len(name) else f"Value{idx+1}"

        if isinstance(data, dict):
            # On prend la première valeur du dict
            value = next(iter(data.values()))
        else:
            value = data

        merged[key] = value

    return merged


#%% N°34 : def merge_lists(*lists):

def merge_lists(*lists):
    # merge dictionaries together
    list_merged = []
    for list in lists:
        list_merged += list
    return list_merged


def remove_keys(d: dict, keys: list) -> dict:
   
    return {k: v for k, v in d.items() if k not in keys}

def remove_string(data: dict, substring: str) -> dict:
    return {k.replace(substring, ''): v for k, v in data.items()}

def merge_dicts_same_keys(d1: dict, d2: dict) -> dict:
 
    if set(d1.keys()) != set(d2.keys()):
        raise ValueError("Dictionaries have different keys")
    return {k: [d1[k], d2[k]] for k in d1.keys()}


def merge_dicts_union(*dicts):
    """
    Merges multiple dictionaries (keys may overlap or not):
    - If a key appears multiple times, the last value takes precedence.
    """
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged

def build_metrics_dataframe(cluster_metrics: dict):
    """
    Transforms a dictionary of dictionaries (cluster → metrics) into a DataFrame:
    - index = metric names
    - columns = cluster names
    """
    df = pd.DataFrame(cluster_metrics)
    return df

 
def merge_dicts_same_keys(*dicts):
    """
    Merges multiple dictionaries with strictly the same keys into a dictionary of lists:
    {
        key1: [val1_dict1, val1_dict2, ...],
        key2: [val2_dict1, val2_dict2, ...],
        ...
    }
    """
    if not dicts:
        return {}
    # Check keys
    keys = set(dicts[0].keys())
    for d in dicts[1:]:
        if set(d.keys()) != keys:
            raise ValueError("All dictionaries must share the same keys.")
    # Merge values into lists
    merged = {
        key: [d[key] for d in dicts]
        for key in keys
    }
    return merged


def merge_dicts_same_keys_sum(*dicts):
    """
    Merges multiple dictionaries with the same keys by summing their numeric values:
    {
        key1: sum(val1_dict1, val1_dict2, ...),
        key2: sum(val2_dict1, val2_dict2, ...),
        ...
    }
    """
    if not dicts:
        return {}
    # Check keys
    keys = set(dicts[0].keys())
    for d in dicts[1:]:
        if set(d.keys()) != keys:
            raise ValueError("All dictionaries must share the same keys.")
    # Sum values
    merged = {}
    for key in keys:
        total = dicts[0][key]
        for d in dicts[1:]:
            total += d[key]
        merged[key] = total
    return merged


#%% N°35 : def transform_dict_into_table(data):

def transform_dict_into_table(data, column_name=None, zero_print="yes"):
    
    if column_name is None and zero_print == "yes": 
        # Convert dictionary into dataframe table
        table = pd.DataFrame.from_dict(data, orient='index')
        return table

    elif column_name is not None and zero_print == "yes":
        # Convert dictionary into dataframe table with specified column name
        table = pd.DataFrame.from_dict(data, orient='index', columns=[column_name])
        return table
    
    elif column_name is None and zero_print == "no":
        # Convert dictionary into dataframe table without zero print
        table = pd.DataFrame.from_dict(data, orient='index')
        table = table[table.sum(axis=1) != 0]
        return table
    
    elif column_name is not None and zero_print == "no":
        # Convert dictionary into dataframe table with specified column name and without zero print
        table = pd.DataFrame.from_dict(data, orient='index', columns=[column_name])
        table = table[table.sum(axis=1) != 0]
        return table

#%% N°35bis : def transform_dict_into_table(data):

def transform_dict_into_table_several_column(data, zero_print='yes', show='yes'):
    # Sort keys alphabetically
    if isinstance(data, dict):
        data = {k: data[k] for k in sorted(data.keys())}
    # Convert to DataFrame
    table = pd.DataFrame.from_dict(data, orient='columns')
    if zero_print == 'no':
        table = table.loc[:, (table != 0).any(axis=0)]
    if show == 'yes':
        from IPython.display import display
        display(table)
    return table


#%% N°35_bis : def transform_list_into_table(data):

def transform_list_into_table(data, *column_names):
    # Convert dictionary into dataframe table
    table = pd.DataFrame(data, columns=column_names)
    return table
#%% N°36 : def save_table_into_csv(table, table_name, folder=None):

def save_table_into_csv(table, table_name, folder=None):
    # Save dataframe table as a csv file in the specified folder
    if folder:
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, table_name + '.csv')
    else:
        file_path = table_name + '.csv'
    table.to_csv(file_path)

#%% N°37 : def save_table_into_excel(table, table_name, folder=None):

def save_table_into_excel(table, table_name, folder=None):
    # Save dataframe table as an Excel file in the specified folder
    if folder:
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, table_name + '.xlsx')
    else:
        file_path = table_name + '.xlsx'
    table.to_excel(file_path)

#%% N°38 : def zoom_on_variable_in_cluster(cluster,variable,zoom,dictionary): 

def zoom_on_variable_in_cluster(cluster,variable,zoom,dictionary): 
    var = dictionary["solution"]["elements"][cluster]["variables"][variable]['values']
    variable_zoomed = []
    if zoom == 'Hour':
        variable_zoomed = var
    if zoom == 'Day':
        n_hour = 24
        for x in range(0,len(var),n_hour):
            if x + n_hour < len(var):
                variable_zoomed.append(sum(var[x:x+n_hour]))
            else:
                variable_zoomed.append(sum(var[x:]))
    elif zoom == 'Week':
        n_hour = 7 * 24
        for x in range(0,len(var),n_hour):
            if x + n_hour < len(var):
                variable_zoomed.append(sum(var[x:x+n_hour]))
            else:
                variable_zoomed.append(sum(var[x:]))
    elif zoom == 'Month':
        n_hour = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] * int(len(var)/8760)
        n_hour = [x * 24 for x in n_hour] 
        n = 0
        for x in range(0,12 * int(len(var)/8760)):
            variable_zoomed.append(sum(var[n:n+n_hour[x]]))
            n += n_hour[x]
    return variable_zoomed

#%% N°39 : def zoom_on_variable_in_cluster_subnode(cluster,variable,node,zoom,dictionary): 

def zoom_on_variable_in_cluster_subnode(cluster,variable,node,zoom,dictionary): 
    var = dictionary["solution"]["elements"][cluster]["sub_elements"][node]["variables"][variable]['values']
    variable_zoomed = []
    if zoom == 'Hour':
        variable_zoomed = var
    if zoom == 'Day':
        n_hour = 24
        for x in range(0,len(var),n_hour):
            if x + n_hour < len(var):
                variable_zoomed.append(sum(var[x:x+n_hour]))
            else:
                variable_zoomed.append(sum(var[x:]))
    elif zoom == 'Week':
        n_hour = 7 * 24  # 7 jours par semaine, 24 heures par jour
        total_weeks = len(var) / n_hour  # Nombre total de semaines
        total_weeks = round(total_weeks)  # Arrondir le nombre de semaines à l'entier le plus proche, ici 52

        # Diviser la variable en semaines arrondies
        for i in range(total_weeks):
            start_index = i * n_hour
            end_index = (i + 1) * n_hour if (i + 1) * n_hour < len(var) else len(var)
            variable_zoomed.append(sum(var[start_index:end_index]))

    elif zoom == 'Month':
        # Mois avec le nombre d'heures pour chaque mois (en considérant l'année non bissextile)
        n_hour = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] * int(len(var) / 8760)
        n_hour = [x * 24 for x in n_hour]  # Conversion en heures
        n = 0
        for x in range(0, 12 * int(len(var) / 8760)):
            variable_zoomed.append(sum(var[n:n + n_hour[x]]))
            n += n_hour[x]
    return variable_zoomed



#%% N°40 : def zoom_on_global_parameter(global_parameter,zoom,dictionary):

def zoom_on_global_parameter(global_parameter,zoom,dictionary): 
    var = dictionary["model"]["global_parameters"][global_parameter]
    variable_zoomed = []
    if zoom == 'Hour':
        variable_zoomed = var
    if zoom == 'Day':
        n_hour = 24
        for x in range(0,len(var),n_hour):
            if x + n_hour < len(var):
                variable_zoomed.append(sum(var[x:x+n_hour]))
            else:
                variable_zoomed.append(sum(var[x:]))
    elif zoom == 'Week':
        n_hour = 7 * 24
        for x in range(0,len(var),n_hour):
            if x + n_hour < len(var):
                variable_zoomed.append(sum(var[x:x+n_hour]))
            else:
                variable_zoomed.append(sum(var[x:]))
    elif zoom == 'Month':
        n_hour = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] * int(len(var)/8760)
        n_hour = [x * 24 for x in n_hour] 
        n = 0
        for x in range(0, 12*int(len(var)/8760)):
            variable_zoomed.append(sum(var[n:n+n_hour[x]]))
            n += n_hour[x]
    return variable_zoomed

# functions to create graph
def plot_timeseries(axes, x, y, bot, lab):

  # Plot the inputs x,y in the provided color
  axes.bar(x, y, bottom = bot, label = lab)

  # Set the x-axis label
  #axes.set_xlabel(xlabel)

  # Set the y-axis label
  #axes.set_ylabel(ylabel, color=color)

  # Set the colors tick params for y-axis
  #axes.tick_params('y', colors=color)
  

# ---------------------------------------------------------------------------------

#%% N°41 : get_nodes_names_from_parameter_3C(parameter,clusters,dictionary):

#Approach to have the cluster layers inside the end results --> much complication inside functions

"""
def get_nodes_names_from_parameter_3C(parameter,clusters,dictionary):
    # get the names of nodes as a list in which the "parameter" is used
    dic_nodes = dict()
    nodes_name = dict()
    for cluster in clusters:
        dic_nodes[cluster] = dictionary["model"]["nodes"][cluster]["sub_nodes"] 
        nodes_name[cluster] = []
        for node in dic_nodes[cluster]:
            if parameter in dic_nodes[cluster][node]["parameters"]:
                nodes_name[cluster].append(node)

    return nodes_name
"""
def get_nodes_names_from_parameter_3C(parameter,clusters,dictionary):
    # get the names of nodes as a Dictionay in which the "parameter" is used
    dic_nodes = dictionary["model"]["nodes"]
    nodes_name = {'other':[]}
    for node in dic_nodes:
        if node in clusters:
            #dic_nodes[node] = dictionary["model"]["nodes"][node]["sub_nodes"] 
            nodes_name[node] = []
            for sub_node in dic_nodes[node]["sub_nodes"]:
                if parameter in dic_nodes[node]["sub_nodes"][sub_node]["parameters"]:
                    nodes_name[node].append(sub_node)
        else:
            if parameter in dic_nodes[node]["parameters"]:
                nodes_name['other'].append(node)
    return nodes_name



#%% N°42 : get_capacities_from_nodes_3C(nodes,name_capacity,name_capacity_0,name_capacity_max,clusters,dictionary):
    
# def get_capacities_from_nodes_3C(nodes,name_capacity,name_capacity_0,name_capacity_max,clusters,dictionary):
#     # Create a dictionary with the capacity, the limit on the capacity and the preinstalled capacity for each node in the dictionary
#     # "nodes". "new_capacity" is the name of the variable corresponding to the capacity, "name_capacity_0" is the name used for
#     # parameter corresponding to the preinstalled capacity and "name_capacity_max" is the parameter corresponding to the maximum 
#     # capacity that can be installed
#     # if no preinstalled capacity or max capacity used in the code, just insert a empty char for those inputs like that: ''
#     capacities = dict()
#     dic_nodes_var = dictionary["solution"]["elements"]
#     dic_nodes_par = dictionary["model"]["nodes"]
#     for node_category in nodes:
#         if node_category in clusters:
#             for node in nodes[node_category]:
                
#                 if name_capacity in dic_nodes_var[node]["variables"]:
#                     capacity = get_variable(node,name_capacity,dictionary)
#                     capacity = capacity[0]
#                 else:
#                     capacity = 0
#                 if name_capacity_0 in dic_nodes_par[node]["parameters"]:
#                     capacity_0 = get_parameter(node,name_capacity_0,dictionary)
#                     capacity_0 = capacity_0[0]
#                 else:
#                     capacity_0 = 0
#                 if name_capacity_max in dic_nodes_par[node]["parameters"]:
#                     capacity_max = get_parameter(node,name_capacity_max,dictionary)
#                     capacity_max = capacity_max[0]
#                 else:
#                     capacity_max = 'Not given'
#                 total_capacity = capacity_0 + capacity
#                 key = node
#                 capacities[key] = {"Preinstalled capacity":capacity_0,"Added capacity":capacity, "Total capacity":total_capacity, "Max capacity": capacity_max}
#     return capacities
    
# fonctions to convert the type of the data data 


#%% N°52 : functions to have the nodes timeseries directly by giving either variable or parameter 
 
def get_timeseries_dict(dictionary, cluster = None, nodes = None, variable = None, parameter = None):
    
    if nodes is None:
        nodes = {}
        
        if variable is not None:
            nodes = get_cluster_subnodes_names_from_variable(variable = variable, cluster = cluster, dictionary = dictionary)
            var = {}
            for node in nodes:
                v_buffer = get_cluster_element_variable(cluster = cluster, element=node, variable=variable, dictionary=dictionary) 
                var[node] = v_buffer['values']
            return var
        
        if parameter is not None:
            nodes = get_cluster_subnodes_names_from_parameter(parameter=parameter, cluster=cluster, dictionary=dictionary) 
            param = {}
            for node in nodes:
                param[node] = get_cluster_element_parameter(cluster=cluster, element=node, parameter=parameter, dictionary=dictionary) 
            return param
        else: 
            if cluster is not None:
                nodes = get_all_cluster_subnodes_names(cluster, dictionary)
                return nodes
                
            else:
                nodes = get_all_cluster_names(dictionary)
                return nodes
    
def get_total_timeseries_dict(data): 
    total = None

    for key, serie in data.items():
        try: 
            values = list(serie)

            if total is None: 
                total = values
            else: 
                total = [a + b for a, b in zip(total, values)]
        
        except TypeError as e:
            print(f"Error processing key '{key}': {e}")
            continue

    return total


        
    
def get_timeseries_dict_from_all_cluster(dictionary, variable = None, parameter = None, to_print = 'yes', cluster = None): 
        
    if cluster == None:
        cluster = get_all_cluster_names(dictionary)  
        
    var = {}
    par = {}
    
    if variable is not None:
        for v in variable: 
            if to_print == 'yes':
                print(colored(f'Variable: {v}', 'blue'))
            for clust in cluster:
                try:
                    cluster_data = get_timeseries_dict(dictionary, variable=v, cluster = clust) 
                    if cluster_data.keys():
                        if to_print == 'yes':
                            print(f'cluster: {clust}: {cluster_data.keys()}') 
                    var[clust] = cluster_data 
                except:
                    pass  
            if to_print == 'yes': 
                print('')
        return var
        if to_print == 'yes':
            print('/n')
    
    if parameter is not None:
        for p in parameter: 
            if to_print == 'yes':
                print(colored(f'Parameter: {p}', 'blue'))
            for clust in cluster:
                try:
                    cluster_data = get_timeseries_dict(dictionary, parameter=p, cluster = clust) 
                    if cluster_data.keys():
                        if to_print == 'yes':
                            print(f'cluster: {clust}: {cluster_data.keys()}') 
                    par[clust] = cluster_data
                except:
                    pass  
            if to_print == 'yes':
                print('')
        return par
        if to_print == 'yes':
              print('/n')
                
#%% N°41 : functions to reformat a list

def get_new_format(data, start_index, end_index, step, xticks='no'):
    
    abcsisse = np.arange(start_index, end_index, step)

    if abcsisse[-1] != end_index - 1:
        abcsisse = np.append(abcsisse, end_index - 1)

    if isinstance(data, dict):
        new_data = {}
        for key in data:
            try:
                full_values = data[key]
            except:
                full_values = data[key]['values']
            if len(full_values) < end_index:
                raise ValueError(f"La série '{key}' est trop courte ({len(full_values)} éléments) pour end_index={end_index}")
            new_data[key] = [full_values[i] for i in abcsisse]
    
    elif isinstance(data, list):
        if len(data) < end_index:
            raise ValueError(f"La série est trop courte ({len(data)} éléments) pour end_index={end_index}")
        new_data = [data[i] for i in abcsisse]

    else:
        raise TypeError("Input data must be either a list or a dictionary.")

    if xticks == 'yes':
        return new_data, abcsisse
    else:
        return new_data

#%% N°42 : functions to choose the zoom  

def zoom_with_timestep(data, zoom = 'hour', mean_or_sum='mean', zero_nodes='no'): 

    if isinstance(data, dict):
        variable_zoomed = {}
        for key, value in data.items():
            # Vérification du type de la valeur et extraction de la série temporelle
            if isinstance(value, dict):
                try:
                    var = value['values']
                except:
                    var = value
            elif isinstance(value, list):
                var = value
            else:
                raise ValueError("Each value in the dictionary must be a dictionary with a 'values' key or a list.")
            
            # Si zero_nodes == 'no', on ignore les séries de valeurs nulles ou composées uniquement de zéros
            if zero_nodes == 'no' and (not var or all(v == 0 for v in var)):
                continue  # On ignore cette clé si la série est vide ou composée uniquement de zéros

            # Appliquer le zoom à la série
            variable_zoomed[key] = _apply_zoom(var, zoom, mean_or_sum)

    elif isinstance(data, list):
        variable_zoomed = _apply_zoom(data, zoom, mean_or_sum)
    else:
        raise ValueError("Data must be a dictionary or a list.")

    return variable_zoomed


def _apply_zoom(var, zoom, mean_or_sum):
    
    variable_zoomed = []

    if zoom == 'hour':
        variable_zoomed = var

    elif zoom == 'day':
        n_hour = 24
        for x in range(0, len(var), n_hour):
            block = var[x:x+n_hour]
            value = sum(block) if mean_or_sum == 'sum' else np.mean(block)
            variable_zoomed.append(value)

    elif zoom == 'week':
        hours_per_week = 7 * 24
        total_weeks = len(var) // hours_per_week

        for i in range(total_weeks):
            week_data = var[i * hours_per_week : (i + 1) * hours_per_week]
            value = sum(week_data) if mean_or_sum == 'sum' else np.mean(week_data)
            variable_zoomed.append(value)

    elif zoom == 'month':
        month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        total_years = len(var) // 8760
        month_lengths *= total_years
        month_lengths_hours = [d * 24 for d in month_lengths]

        n = 0
        for month_hour in month_lengths_hours:
            month_data = var[n:n + month_hour]
            value = sum(month_data) if mean_or_sum == 'sum' else np.mean(month_data)
            variable_zoomed.append(value)
            n += month_hour
            
    else:  
        variable_zoomed = var    

    return variable_zoomed
    
#%% N°42bis : functions to choose the zoom and the step of the data

import builtins

def precise_zoom_with_timestep(data, zoom, number, step='hour', time_horizon=8760, mean_or_sum='sum', zero_nodes='yes'):
    # If the input data is a dictionary, apply zoom to each key
    if isinstance(data, dict):
        variable_zoomed = {}
        for key, value in data.items():
            # If the value is a dictionary containing the 'values' key
            if isinstance(value, dict) and 'values' in value:
                var = value['values']
            # If the value is a list
            elif isinstance(value, list):
                var = value
            else:
                raise ValueError("Each value must be either a dictionary with a 'values' key or a list.")

            # Apply the zoom
            variable_zoomed[key] = _apply_precise_zoom(var, zoom, step, number, mean_or_sum, zero_nodes)

    # If the data is a list
    elif isinstance(data, list):
        variable_zoomed = _apply_precise_zoom(data, zoom, step, number, mean_or_sum, zero_nodes)
    
    # Unsupported data types
    else:
        raise ValueError("Input data must be either a dictionary or a list.")

    return variable_zoomed


def _apply_precise_zoom(var, zoom, step, number, mean_or_sum, zero_nodes):
    # Skip empty nodes if specified
    if zero_nodes == 'no' and not any(var):
        return []

    variable_zoomed = []

    # Months associated with each season
    seasons_months = {
        'spring': [3, 4, 5],    # March, April, May
        'summer': [6, 7, 8],    # June, July, August
        'fall':   [9, 10, 11],  # September, October, November
        'winter': [12, 1, 2]    # December, January, February
    }

    # If zooming by season
    if zoom in seasons_months:
        months = seasons_months[zoom]
        for month in months:
            start_hour = (month - 1) * 730  # Approx. 730 hours per month
            end_hour = month * 730
            season_data = var[start_hour:end_hour]
            variable_zoomed.extend(_apply_step(season_data, step, mean_or_sum))

    # Zoom by a specific month
    elif zoom == 'month':
        start_hour = (number - 1) * 730
        end_hour = number * 730
        month_data = var[start_hour:end_hour]
        variable_zoomed.extend(_apply_step(month_data, step, mean_or_sum))

    # Zoom by a specific week
    elif zoom == 'week':
        week_data = var[(number - 1) * 168 : number * 168]
        variable_zoomed.extend(_apply_step(week_data, step, mean_or_sum))

    # Zoom by a specific day
    elif zoom == 'day':
        day_data = var[(number - 1) * 24 : number * 24]
        variable_zoomed.extend(_apply_step(day_data, step, mean_or_sum))

    # No zoom, return raw data
    elif zoom == 'hour':
        variable_zoomed = var

    return variable_zoomed


def _apply_step(data, step, mean_or_sum):
    if step == 'hour':
        return data
    elif step == 'day':
        return [
            builtins.sum(data[i:i + 24]) if mean_or_sum == 'sum' else np.mean(data[i:i + 24])
            for i in range(0, len(data), 24)
        ]
    elif step == 'week':
        return [
            builtins.sum(data[i:i + 168]) if mean_or_sum == 'sum' else np.mean(data[i:i + 168])
            for i in range(0, len(data), 168)
        ]
    else:
        raise ValueError(f"Step '{step}' not recognized. Use 'hour', 'day' or 'week'.")


#%% N°43bis : functions to create graph

def plot_maker_new(data, type_var, x_label, y_label, title, save_name, 
                    total_plot='yes', offset='no', plot_show='yes', xticks=None,
                    plot_folder='plots', size=(12, 6), zero_nodes='no', rotation=0, print_skip='yes'):


    plt.figure(figsize=size)
    summed_values = []
    last_values = None  # pour xlim plus tard

    if isinstance(data, (list, np.ndarray)):
        values = data
        if zero_nodes == 'no' and all(v == 0 for v in values):
            if print_skip == 'yes':
                print(f"⚠️ Skipping series because it contains only zeros: {type_var}") 
            return

        if xticks is not None:
            plt.plot(xticks, values, label=f"{type_var}")
        else:
            x_range = np.arange(1, len(values)+1) if offset == 'yes' else np.arange(len(values))
            plt.plot(x_range, values, label=f"{type_var}")

        summed_values.append(values)
        last_values = values

    elif isinstance(data, dict):
        for key, values in data.items():
            if isinstance(values, dict) and 'values' in values:
                values = values['values']

            if not isinstance(values, (list, np.ndarray)) or not values:
                print(f"⚠️ No valid data for key '{key}'. values={values}")
                continue

            if zero_nodes == 'no' and all(v == 0 for v in values):
                if print_skip == 'yes':
                    print(f"⚠️ Skipping series because it contains only zeros: {key}")
                continue

            if xticks is not None:
                plt.plot(xticks, values, label=key)
            else:
                x_range = np.arange(1, len(values)+1) if offset == 'yes' else np.arange(len(values))
                plt.plot(x_range, values, label=key)

            summed_values.append(values)
            last_values = values

        if total_plot == 'yes' and summed_values:
            max_length = max(len(val) for val in summed_values)
            summed_values = [np.pad(val, (0, max_length - len(val)), mode='constant') for val in summed_values]
            total_values = np.sum(summed_values, axis=0)

            if xticks is not None:
                plt.plot(xticks, total_values, label=f'Total {type_var}', linewidth=3, linestyle='--', color='black')
            else:
                x_range = np.arange(1, len(total_values)+1) if offset == 'yes' else np.arange(len(total_values))
                plt.plot(x_range, total_values, label=f'Total {type_var}', linewidth=3, linestyle='--', color='black')

        elif total_plot == 'yes' and not summed_values:
            print("⚠️ No data available to plot total.")

    else:
        print("❌ Unsupported data format. Please provide a list or a dictionary.")
        return

    # X TICKS
    if xticks is not None:
        plt.xticks(xticks, rotation=rotation, fontsize=8)
        plt.xlim(xticks[0], xticks[-1])
    else:
        # if last_values is not None:
        #     n = len(last_values)
        #     first = last_values[0]
        #     if n <= 52:
        #         tick_range = np.arange(first + 1, n + 1, 1) if offset == 'yes' else np.arange(first , n, 1)
        #         plt.xticks(tick_range, rotation=rotation, fontsize=8)
        #     elif n > 52 and n <= 367:
        #         tick_range = np.append(np.arange(first +1, n+1, 10), n+1) if offset == 'yes' else np.append(np.arange(first ,n, 10), n)
        #         plt.xticks(tick_range, rotation=rotation, fontsize=8)
        #     else:
        #         tick_range = np.append(np.arange(first +1, n, 200), n) if offset == 'yes' else np.append(np.arange(first ,n-1, 200), n-1)
        #         plt.xticks(tick_range, rotation=rotation, fontsize=8) 

        #     plt.xlim(first + 1, n) if offset == 'yes' else plt.xlim(first, n-1)
            
            
        if last_values is not None:
            n = len(last_values)
            first = last_values[0]
            if n <= 52:
                tick_range = np.arange(1, n + 1, 1) if offset == 'yes' else np.arange(0 , n, 1)
                plt.xticks(tick_range, rotation=rotation, fontsize=8)
            elif n > 52 and n <= 367:
                tick_range = np.append(np.arange(1, n+1, 10), n+1) if offset == 'yes' else np.append(np.arange(0 ,n, 10), n)
                plt.xticks(tick_range, rotation=rotation, fontsize=8)
            else:
                tick_range = np.append(np.arange(1, n, 200), n) if offset == 'yes' else np.append(np.arange(0 ,n-1, 200), n-1)
                plt.xticks(tick_range, rotation=rotation, fontsize=8) 

            plt.xlim(0 + 1, n) if offset == 'yes' else plt.xlim(0, n-1)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=5, fontsize=8.5)

    os.makedirs(plot_folder, exist_ok=True)
    save_path = os.path.join(plot_folder, f'{save_name}.pdf')
    plt.savefig(save_path)
    print(f"✅ Plot saved: {save_path}")

    if plot_show == 'yes':
        plt.show()
    else:
        plt.close()

    return np.sum(summed_values, axis=0)




#%% N°44 : functions to create graph

def precise_zoom(data, format, number, step='hour', mean_sum='sum'):
    """
    Extracts a specific period (day, week, month, or season) from hourly data and allows data aggregation.

    Parameters:
        data (dict): Dictionary containing the key 'values' with time series data.
        format (str): 'Day', 'Week', 'Month', or 'Season' to select the period type.
        number (int): Day number (1-365), week number (1-52), month number (1-12), or season number (1-4) to extract.
        step (str): 'hour' (default), 'day', or 'week' for aggregation.
        mean_sum (str): 'mean' for averaging, 'sum' for summing (default).

    Returns:
        list: Aggregated values for the selected period.
    """
    if 'values' not in data or not isinstance(data['values'], list):
        raise ValueError("Data must be a dictionary containing a 'values' list.")

    values = data['values']
    total_hours = len(values)  # Adaptation to the actual length of the data

    # Number of hours per month for a standard year
    hours_per_month = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]) * 24

    # Extraction of a day
    if format == 'Day':
        start_idx = (number - 1) * 24
        if start_idx >= total_hours:
            raise ValueError("Requested day exceeds available data range.")
        period_values = values[start_idx:min(start_idx + 24, total_hours)]
        if step == 'hour':
            return period_values
        raise ValueError("For 'Day', only 'hour' step is allowed.")

    # Extraction of a week
    elif format == 'Week':
        start_idx = (number - 1) * 7 * 24
        if start_idx >= total_hours:
            raise ValueError("Requested week exceeds available data range.")
        period_values = values[start_idx:min(start_idx + 7 * 24, total_hours)]
        if step == 'day':
            period_values = [sum(period_values[i:i+24]) if mean_sum == 'sum' else np.mean(period_values[i:i+24]) 
                             for i in range(0, len(period_values), 24)]
        elif step != 'hour':
            raise ValueError("For 'Week', only 'hour' and 'day' steps are allowed.")

    # Extraction of a month
    elif format == 'Month':
        if number < 1 or number > 12:
            raise ValueError("Month number must be between 1 and 12.")
        start_idx = sum(hours_per_month[:number-1])  # Calculate the start index
        if start_idx >= total_hours:
            raise ValueError("Requested month exceeds available data range.")
        period_values = values[start_idx:min(start_idx + hours_per_month[number-1], total_hours)]
        if step == 'day':
            period_values = [sum(period_values[i:i+24]) if mean_sum == 'sum' else np.mean(period_values[i:i+24]) 
                             for i in range(0, len(period_values), 24)]
        elif step == 'week':
            period_values = [sum(period_values[i:i+7*24]) if mean_sum == 'sum' else np.mean(period_values[i:i+7*24]) 
                             for i in range(0, len(period_values), 7*24)]
        elif step != 'hour':
            raise ValueError("For 'Month', only 'hour', 'day', and 'week' steps are allowed.")

    # Extraction of a season
    elif format == 'Season':
        if number < 1 or number > 4:
            raise ValueError("Season number must be between 1 (Winter), 2 (Spring), 3 (Summer), and 4 (Fall).")
        season_hours = {
            1: sum(hours_per_month[:2]) + 31 * 24,  # Winter: Dec (31 days) + Jan + Feb
            2: sum(hours_per_month[2:5]),          # Spring: Mar + Apr + May
            3: sum(hours_per_month[5:8]),          # Summer: Jun + Jul + Aug
            4: sum(hours_per_month[8:11]) + 30 * 24  # Fall: Sep + Oct + Nov
        }
        start_idx = {
            1: total_hours - 31 * 24 - sum(hours_per_month[:2]),  # Winter starts in Dec of the previous year
            2: sum(hours_per_month[:2]),                         # Spring starts in Mar
            3: sum(hours_per_month[:5]),                         # Summer starts in Jun
            4: sum(hours_per_month[:8])                          # Fall starts in Sep
        }[number]
        if start_idx >= total_hours:
            raise ValueError("Requested season exceeds available data range.")
        period_values = values[start_idx:min(start_idx + season_hours[number], total_hours)]
        if step == 'day':
            period_values = [sum(period_values[i:i+24]) if mean_sum == 'sum' else np.mean(period_values[i:i+24]) 
                             for i in range(0, len(period_values), 24)]
        elif step == 'week':
            period_values = [sum(period_values[i:i+7*24]) if mean_sum == 'sum' else np.mean(period_values[i:i+7*24]) 
                             for i in range(0, len(period_values), 7*24)]
        elif step != 'hour':
            raise ValueError("For 'Season', only 'hour', 'day', and 'week' steps are allowed.")

    else:
        raise ValueError("Invalid format. Choose 'Day', 'Week', 'Month', or 'Season'.")

    return period_values


#%% N°45 : functions to create graph

def plot_merge(data, legend, x_label, y_label, title, save_name, plot_folder, is_offset = 'no', rotation=0):
    
    fig, ax = plt.subplots(figsize=(12, 6))

    if isinstance(data, list):
        for index, data_item in enumerate(data):
            if is_offset == 'yes':
                ax.plot(np.arange(1, len(data_item) + 1), data_item, label=legend[index])  # Offset to start at 1
            else:
                ax.plot(np.arange(0, len(data_item)), data_item, label=legend[index])  # Start at 0
    elif isinstance(data, dict):
        for key, values in data.items():
            if is_offset == 'yes':
                ax.plot(np.arange(1, len(values) + 1), values, label=key)  # Offset to start at 1
            else:
                ax.plot(np.arange(0, len(values)), values, label=key)  # Start at 0

    ax.set(xlabel=x_label, ylabel=y_label, title=title)
    ax.grid()

    # Adjust x-axis ticks
    if is_offset == 'yes':
        ax.set_xticks(np.arange(1, len(next(iter(data.values()))) + 1, 1))  # Start at 1 for dict
    else:
        ax.set_xticks(np.arange(0, len(next(iter(data.values()))), 1))  # Start at 0 for dict

    # Adjust font size for x-axis ticks
    x_ticks = ax.get_xticks()
    if len(x_ticks) > 31:
        ax.tick_params(axis='x', labelsize=8.5)  # Reduce font size to 8.5
    else:
        ax.tick_params(axis='x', labelsize=10)  # Default font size

    # Adjust x-axis limits based on is_offset
    min_x = 0 if is_offset == 'no' else 1
    max_x = len(next(iter(data.values()))) - 1 if is_offset == 'no' else len(next(iter(data.values())))
    ax.set_xlim(min_x, max_x)

    # Place legend outside the plot (below x-axis)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=5, fontsize=8.5)

    # Apply tight layout to avoid empty spaces
    plt.tight_layout()

    # Save the plot
    fig.savefig(os.path.join(plot_folder, save_name + '.pdf'))
    print(f"✅ Plot saved")

    # Show the plot
    plt.show()


#%% N°46 : functions to create a color gradient

def generate_gradient(color_palette, num_steps):
        if color_palette in plt.colormaps():  
            cmap = plt.get_cmap(color_palette)  
            color_list = [cmap(1 - i / (num_steps - 1)) for i in range(num_steps)]  
        else:
            base_color = np.array(mcolors.to_rgba(color_palette)[:3])  
            
            if color_palette in ['orange', 'green']:
                light_color = np.clip(base_color + 0.1, 0, 1)  
            elif color_palette in ['gray', 'grey']:
                light_color = np.clip(base_color - 0.5, 0, 1)  
            else:
                light_color = np.clip(base_color + 0.5, 0, 1)  
            
            if color_palette in ['gray', 'grey']:
                dark_color = np.clip(base_color/0.7,0.5, 0, 1)
            else:
                dark_color = np.clip(base_color * 0.7, 0, 1)  

            cmap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", [dark_color, base_color, light_color], N=num_steps)
            color_list = [cmap(i / (num_steps - 1)) for i in range(num_steps)]
        
        return color_list


#%% N°47 : functions to plot stacked bar plots

def bar_ploter_stack(nodes, energy_quantity, total_energy, capacity_quantity, max_capacity, mean_capacity, installed_capacity, cluster, variable,
                     color_palette, text_color, cap_unit, ener_unit, commodity, is_power, is_energy, is_combined, plot_folder):
     
    # Filter nodes that have at least one nonzero capacity
    filtered_nodes = [node for node in nodes if mean_capacity[node] > 0 or max_capacity[node] > 0 or installed_capacity[node] > 0]

    if not filtered_nodes:
        print("No data to display (all capacities are zero).")
        return
    
    "======================="
    "=== Power stack bar plot ==="
    "======================="   
    
    data_power = {"Installed Capacity": [installed_capacity[node] for node in filtered_nodes],
        "Max Capacity": [max_capacity[node] for node in filtered_nodes],
        "Mean Capacity": [mean_capacity[node] for node in filtered_nodes]}

    df_power = pd.DataFrame(data_power, index=filtered_nodes)

    if is_power == 'yes':
        
        fig, ax = plt.subplots(figsize=(10, 6))

        num_steps = 3  # For 3 different capacity types
        gradient_colors = generate_gradient(color_palette, num_steps)
        bar_width = 0.3
        bottom = np.zeros(len(filtered_nodes))  # Initialize bottom

        for i, (capacity_type, color) in enumerate(zip(data_power.keys(), gradient_colors)):
            values = df_power[capacity_type]
            bars = ax.barh(filtered_nodes, values, label=capacity_type, color=color, left=0, height=bar_width)
            
            # Add annotations on bars
            for j, bar in enumerate(bars):
                width = bar.get_width()
                if width > 0:
                    ax.text(bar.get_x() + width * 0.9, bar.get_y() + bar.get_height() / 2,
                            f'{width:.1f}', ha='center', va='center', fontsize=7, color=text_color, weight='bold')

        ax.set_ylabel(f'{cap_unit}')
        ax.set_title(f'{commodity}')
        ax.legend()
        ax.grid(axis='x')
        plt.tight_layout()
        plt.savefig(os.path.join(plot_folder, f'{commodity}_power_bar_plot.pdf'))
        plt.show()
    
    
    "======================="
    "=== Energy bar plot ==="
    "======================="
    
    data_ener = {"Energy or Quantity": [total_energy[node] for node in filtered_nodes]}

    df_ener = pd.DataFrame(data_ener, index=filtered_nodes)

    if is_energy == 'yes':
        
        fig, ax = plt.subplots(figsize=(10, 6))

        bar_width = 0.3
        energy_values = df_ener["Energy or Quantity"]
        bars = ax.barh(filtered_nodes, energy_values, label="Energy or Quantity", color=color_palette, height=bar_width)

        # Add annotations on bars
        for bar in bars:
            width = bar.get_width()
            if width > 0:
                ax.text(width * 0.9, bar.get_y() + bar.get_height() / 2,
                        f'{width:.3f}', ha='center', va='center', fontsize=7, color=text_color, weight='bold')

        # Add labels and title
        ax.set_ylabel(f'{ener_unit}')
        ax.set_title(f'{commodity}')
        # ax.legend()
        ax.grid(axis='x')

        # Display the chart
        plt.tight_layout()
        plt.savefig(os.path.join(plot_folder, f'{commodity}_energy_bar_plot.pdf'))
        plt.show()
        
    
    "========================="
    "=== Combined bar plot ==="
    "========================="
    
    if is_combined == 'yes':
        
        fig, axs = plt.subplots(1, 2, figsize=(14, 6), sharey=True) 

        # 🔹 Génération des couleurs pour les barres de Power
        num_steps = 3  # Trois types de capacités
        gradient_colors = generate_gradient(color_palette, num_steps)

        # 📊 PLOT 1 : POWER (axs[0])
        bar_width = 0.3
        for i, (capacity_type, color) in enumerate(zip(data_power.keys(), gradient_colors)):
            values = df_power[capacity_type]
            bars = axs[0].barh(filtered_nodes, values, label=capacity_type, color=color, height=bar_width)
            for bar in bars:
                width = bar.get_width()
                if width > 0:
                    axs[0].text(width * 0.9, bar.get_y() + bar.get_height() / 2,
                            f'{width:.1f}', ha='center', va='center', fontsize=7, color=text_color, weight='bold')

        # axs[0].set_title('Power')
        axs[0].set_xlabel(f'{cap_unit}')
        axs[0].set_ylabel(f'{commodity}')
        axs[0].legend()
        axs[0].grid(axis='x')

        # 📊 PLOT 2 : ENERGY (axs[1])
        bars = axs[1].barh(filtered_nodes, df_ener["Energy or Quantity"], label="Energy or Quantity", color=color_palette, height=bar_width)
        for bar in bars:
            width = bar.get_width()
            if width > 0:
                axs[1].text(width * 0.9, bar.get_y() + bar.get_height() / 2,
                            f'{width:.3f}', ha='center', va='center', fontsize=7, color=text_color, weight='bold')

        # axs[1].set_title('Energy')
        axs[1].set_xlabel(f'{ener_unit}')
        # axs[1].legend()
        axs[1].grid(axis='x')

        # 📏 Ajustement de l'affichage
        plt.tight_layout()
        plt.savefig(os.path.join(plot_folder, f'{commodity}_power&energy_combined_bar_plot.pdf'))
        plt.show()
        

#%% N°47bis : functions to plot a stacked bar plot from a dict 

import os
import matplotlib.pyplot as plt
import pandas as pd

def generate_gradient(color_palette, num_steps):
    """
    Génère une liste de num_steps couleurs en dégradé à partir d'un colormap ou d'une couleur.
    """
    if color_palette in plt.colormaps():  
        cmap = plt.get_cmap(color_palette)  
        color_list = [cmap(1 - i / (num_steps - 1)) for i in range(num_steps)]  
    else:
        base_color = np.array(mcolors.to_rgba(color_palette)[:3])  
        # création de teintes claires et foncées
        light_color = np.clip(base_color + 0.2, 0, 1)
        dark_color  = np.clip(base_color * 0.6, 0, 1)
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "custom_cmap", [dark_color, base_color, light_color], N=num_steps
        )
        color_list = [cmap(i / (num_steps - 1)) for i in range(num_steps)]
    return color_list

def bar_ploter_stack_dict(data, color_palette, cap_unit, ener_unit, commodity, plot_folder, 
                          to_annotate='yes', text_color='white', weight='bold',
                          bar_width=0.4, rotation=90, percentage=0.92,
                          is_power='yes', is_energy='yes', is_combined='yes',
                          format=(10, 6), format_combined=(15, 6), multiply=1):
    """
    Plot stacked bar charts of capacity and energy metrics with gradient colors for capacity bars.
    """
    # Helper to retrieve a value with multiple possible keys
    def get_val(series, keys):
        for key in keys:
            try:
                return series[key]
            except (KeyError, TypeError):
                continue
        return 0

    inst_keys = [f"Installed capacity {cap_unit}", "Installed capacity", "Installed capacity [kton]"]
    max_keys  = [f"Max capacity {cap_unit}", "Max capacity", "Max capacity [kton]"]
    mean_keys = [f"Mean capacity {cap_unit}", "Mean capacity", "Mean capacity [kton]"]
    ener_keys = [f"Total energy {ener_unit}", "Total energy", "Total energy [TWh]"]

    # Sélection des technologies actives
    filtered_nodes = [
        tech for tech, series in data.items()
        if get_val(series, inst_keys)*multiply > 0 or
           get_val(series, max_keys)*multiply > 0 or
           get_val(series, mean_keys)*multiply > 0
    ]
    if not filtered_nodes:
        print("❌ No data to display (all capacities are zero after scaling).")
        return

    # Ajustement taille figure
    height = min(1.5 + 0.8 * len(filtered_nodes), 8)
    fmt_power = (format[0], height)
    fmt_comb  = (format_combined[0], height)

    # Construction DataFrames
    df_power = pd.DataFrame({
        "Installed Capacity": [get_val(data[tech], inst_keys)*multiply for tech in filtered_nodes],
        "Max Capacity":       [get_val(data[tech], max_keys)*multiply for tech in filtered_nodes],
        "Mean Capacity":      [get_val(data[tech], mean_keys)*multiply for tech in filtered_nodes],
    }, index=filtered_nodes)

    df_ener = pd.DataFrame({
        "Energy or Quantity": [get_val(data[tech], ener_keys)*multiply for tech in filtered_nodes]
    }, index=filtered_nodes)

    os.makedirs(plot_folder, exist_ok=True)

    # Préparer dégradé de couleurs pour power
    n_bars = len(df_power.columns)
    gradient_colors = generate_gradient(color_palette, n_bars)

    # Plot capacité
    if is_power.lower() == 'yes':
        fig, ax = plt.subplots(figsize=fmt_power)
        for i, col in enumerate(df_power.columns):
            bars = ax.barh(df_power.index, df_power[col],
                           label=col, color=gradient_colors[i], height=bar_width)
            if to_annotate.lower() == 'yes':
                for bar in bars:
                    w = bar.get_width()
                    if w > 0:
                        ax.text(w * percentage, bar.get_y() + bar.get_height()/2,
                                f'{w:.2f}', ha='left', va='center',
                                fontsize=7, color=text_color, weight=weight, rotation=rotation)
        ax.set_ylabel(cap_unit)
        ax.set_title(f"{commodity} - Capacity", fontsize=14)
        ax.tick_params(axis='y', labelsize=8)
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3),
          ncol=len(df_power.columns), fontsize=8, frameon=False)
        ax.grid(axis='x')
        plt.tight_layout()
        plt.savefig(os.path.join(plot_folder, f"{commodity}_power_bar_plot.pdf"))
        plt.show()

    # Plot énergie
    if is_energy.lower() == 'yes':
        fig, ax = plt.subplots(figsize=fmt_power)
        bars = ax.barh(df_ener.index, df_ener["Energy or Quantity"],
                       label="Energy", color=color_palette, height=bar_width)
        if to_annotate.lower() == 'yes':
            for bar in bars:
                w = bar.get_width()
                if w > 0:
                    ax.text(w * percentage, bar.get_y() + bar.get_height()/2,
                            f'{w:.2f}', ha='left', va='center',
                            fontsize=7, color=text_color, weight=weight)
        ax.set_ylabel(ener_unit)
        ax.set_title(f"{commodity} - Energy", fontsize=14)
        ax.tick_params(axis='y', labelsize=8)
        ax.grid(axis='x')
        plt.tight_layout()
        plt.savefig(os.path.join(plot_folder, f"{commodity}_energy_bar_plot.pdf"))
        plt.show()

    # Plot combiné
    if is_combined.lower() == 'yes':
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fmt_comb, sharey=True)
        # Capacity subplot
        for i, col in enumerate(df_power.columns):
            bars = ax1.barh(df_power.index, df_power[col],
                            label=col, color=gradient_colors[i], height=bar_width)
            if to_annotate.lower() == 'yes':
                for bar in bars:
                    w = bar.get_width()
                    if w > 0:
                        ax1.text(w * percentage, bar.get_y() + bar.get_height()/2,
                                 f'{w:.2f}', ha='center', va='center',
                                 fontsize=7, color=text_color, weight=weight, rotation=rotation)
        ax1.set_xlabel(cap_unit)
        ax1.set_ylabel(commodity, fontsize=14)
        ax1.tick_params(axis='y', labelsize=8)
        ax1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3),
          ncol=len(df_power.columns), fontsize=8, frameon=False) 
        ax1.grid(axis='x')
        # Energy subplot
        bars = ax2.barh(df_ener.index, df_ener["Energy or Quantity"],
                        color=color_palette, height=bar_width)
        if to_annotate.lower() == 'yes':
            for bar in bars:
                w = bar.get_width()
                if w > 0:
                    ax2.text(w * percentage, bar.get_y() + bar.get_height()/2,
                             f'{w:.2f}', ha='center', va='center',
                             fontsize=7, color=text_color, weight=weight)
        ax2.set_xlabel(ener_unit)
        # ax2.set_title(f"{commodity} - Energy", fontsize=14)
        ax2.tick_params(axis='y', labelsize=8)
        ax2.grid(axis='x')
        plt.tight_layout()
        plt.savefig(os.path.join(plot_folder, f"{commodity}_power_energy_combined_bar_plot.pdf"))
        plt.show()


        
 
#%% N°48 : functions to plot a bar plot
        
def bar_ploter(data_prod, data_cons, data_charged, data_discharged):
            
    # Création d'un DataFrame
    data = []
    for node in nodes:
        data.append([node, 'Mean Capacity', mean_capacity[node]])
        data.append([node, 'Max Capacity', max_capacity[node]])
        data.append([node, 'Installed Capacity', installed_capacity[node]])

    df = pd.DataFrame(data, columns=['Node', 'Capacity Type', 'Value'])

    # Création du barplot avec Seaborn
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='Node', y='Value', hue='Capacity Type')

    # Ajout des labels et titre
    plt.xlabel('Subnodes')
    plt.ylabel('Capacity (GWh)')
    plt.title(f'Installed Capacity vs Total Capacity in {cluster} for {variable}')
    plt.grid(axis='y')
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    
#%% N°49 : functions to create a dictionary with the capacities and energy of the cluster

def pow_energy_dict(variable, cluster, unit_power, unit_energy, dict, time_horizon = 8760,
                    name_capacity = "new_capacity", name_capacity_0 = "pre_installed_capacity", 
                    name_capacity_max = "max_capacity", all_print = 'yes'):
    
    capacity_quantity = {}
    energy_quantity = {}
    total_energy = {}
    min_capacity = {}
    max_capacity = {}
    mean_capacity = {}
    installed_capacity = {}
    load_factor = {}
    table = {}
    
    nodes = get_cluster_subnodes_names_from_variable(variable, cluster, dict)

    # Capacités initiales via méthode principale
    try:
        capacities = get_cluster_subnodes_capacities_from_nodes(nodes, cluster, dict, name_capacity, name_capacity_0, name_capacity_max)
        first_node = next(iter(capacities))
        if capacities[first_node].get("Max capacity") == "Not given":
            raise ValueError("Max capacity is 'Not given', switching to fallback.")
    except:
        capacities = get_cluster_subnodes_capacities_from_storage(nodes, cluster, dict)

    for node in nodes: 
        value = get_cluster_element_variable(cluster, node, variable, dict)
        energy_quantity[node] = value['values']
        total_energy[node] = sum(value['values'])
        
        max_capacity[node] = max(energy_quantity[node])   
        mean_capacity[node] = mean(energy_quantity[node]) 
        capacity_quantity[node] = capacities    
        installed_capacity[node] = capacities[node]['Total capacity']

        if installed_capacity[node] == 0:
            load_factor[node] = 0
        else:
            load_factor[node] = total_energy[node]/(installed_capacity[node] * time_horizon)
        
        min_capacity[node] = max(energy_quantity[node]) 
        
        table[node] = {
            f"Total energy {unit_energy}": round(total_energy[node]/1000, 2),
            f"Max capacity {unit_power}": round(max_capacity[node], 2),
            f"Min capacity {unit_power}": round(min_capacity[node], 2),
            f"Mean capacity {unit_power}": round(mean_capacity[node], 2),
            f"Installed capacity {unit_power}": round(installed_capacity[node], 2),
            "Load factor": round(load_factor[node], 2)
        }

        if all_print == 'no':
            table[node] = {
                f"Mean capacity {unit_power}": round(mean_capacity[node], 1),
                f"Max capacity {unit_power}": round(max_capacity[node], 1),
                f"Installed capacity {unit_power}": round(installed_capacity[node], 1),
                f"Total energy {unit_energy}": round(total_energy[node]/1000, 2)
            }

    return nodes, energy_quantity, total_energy, capacity_quantity, max_capacity, mean_capacity, installed_capacity, load_factor, table


def cap_pow_energy_dict(energy_dict, capacity_dict, unit_power, unit_energy,
                        time_horizon=8760, name_capacity="new_capacity",
                        name_capacity_0="pre_installed_capacity",
                        name_capacity_max="max_capacity", all_print='yes',
                        total_return='no', decimal = [5,5]):
    
    capacity_quantity = {}
    energy_quantity = {}
    total_energy = {}
    min_capacity = {}
    max_capacity = {}
    mean_capacity = {}
    installed_capacity = {}
    load_factor = {}
    table = {}

    nodes = capacity_dict.keys()

    for node in nodes:
        # Gestion du cas où energy_dict est un dictionnaire de dictionnaires avec node comme clé
        if isinstance(energy_dict, dict) and node in energy_dict:
            node_energy = energy_dict[node]
        else:
            node_energy = energy_dict  # fallback

        try:
            # S'assurer qu'on utilise bien les valeurs numériques (et pas un dict)
            energy_values = list(node_energy.values()) if isinstance(node_energy, dict) else node_energy
            energy_quantity[node] = energy_values
            total_energy[node] = np.sum(energy_values)
            mean_capacity[node] = np.mean(energy_values)
            max_capacity[node] = np.max(energy_values)
            min_capacity[node] = np.min(energy_values)
        except Exception as e:
            print(f"Erreur dans les valeurs d'énergie pour le noeud {node} : {e}")
            energy_quantity[node] = []
            total_energy[node] = 0
            mean_capacity[node] = 0
            max_capacity[node] = 0
            min_capacity[node] = 0

        # Capacité installée
        try:
            capacities = capacity_dict[node]
            installed_capacity[node] = capacities['Total capacity']
            capacity_quantity[node] = capacities
        except Exception as e:
            print(f"Erreur dans la capacité pour le noeud {node} : {e}")
            installed_capacity[node] = 0
            capacity_quantity[node] = {}

        # Facteur de charge
        if installed_capacity[node] == 0:
            load_factor[node] = 0
        else:
            load_factor[node] = total_energy[node] / (installed_capacity[node] * time_horizon)

        # Table des résultats
        table[node] = {
            "Total energy": round(total_energy[node] / 1000, decimal[1]),
            "Max capacity": round(max_capacity[node], decimal[0]),
            "Min capacity": round(min_capacity[node], decimal[0]),
            "Mean capacity": round(mean_capacity[node], decimal[0]),
            "Installed capacity": round(installed_capacity[node], decimal[0]),
            "Load factor": round(load_factor[node], 2)
        }

        if all_print == 'no':
            table[node] = {
            "Mean capacity": round(mean_capacity[node], decimal[0]),
            "Max capacity": round(max_capacity[node], decimal[0]),
            "Installed capacity": round(installed_capacity[node], decimal[0]),
            "Total energy": round(total_energy[node] / 1000, decimal[1])
            }

    if total_return == 'yes':
        return nodes, energy_quantity, total_energy, capacity_quantity, max_capacity, mean_capacity, installed_capacity, load_factor, table
    else:
        return table
    
    
#%% N°50 : functions to plot a box plot and having the statistics of the box plot in a table

def box_plot(data, title, y_label, x_label=None, x_ticks=None, hue=None,
            box_color='grey', mean_color='red', median_color='orange',
            widths=0.4, to_plot='yes', to_annotate='no', figsave = None,
            what_to_annotate=None, to_print='no', figsize=(12, 6)):

    all_data = []
    valid_nodes = []
    show_xticks = True

    # Si data est une simple liste de valeurs, on la transforme en liste de liste
    if isinstance(data, list) and all(isinstance(val, (int, float)) for val in data):
        data = [data]
        show_xticks = False

    # Cas 1 : data est une liste de listes
    if isinstance(data, list):
        for i, values in enumerate(data):  
            if isinstance(x_ticks, list) and i < len(x_ticks):
                label = x_ticks[i]
            else:
                label = ""

            df = pd.DataFrame({
                y_label: values,
                "Node": label
            })

            all_data.append(df)
            valid_nodes.append(label)

    # Cas 2 : data est un dictionnaire
    elif isinstance(data, dict):
        for node, values in data.items():
            try:
                if all(v == 0 for v in values['values']):
                    continue
                df = pd.DataFrame({y_label: values['values'], "Node": node})
            except:
                if all(v == 0 for v in values):
                    continue
                df = pd.DataFrame({y_label: values, "Node": node})

            all_data.append(df)
            valid_nodes.append(node)

    if not all_data:
        print("No valid nodes to display (all contain only zeros or non-iterable data).")
        return

    final_df = pd.concat(all_data, ignore_index=True)

    box_data = [
        final_df[final_df["Node"] == node][y_label].values
        for node in valid_nodes
    ]

    stats_table = []

    if to_annotate == 'yes':
        for i, node in enumerate(valid_nodes):
            node_values = np.array(box_data[i])
            mean_value = np.mean(node_values)
            median_value = np.median(node_values)
            q1 = np.percentile(node_values, 25)
            q3 = np.percentile(node_values, 75)
            iqr = q3 - q1

            min_val = node_values[node_values >= (q1 - 1.5 * iqr)].min()
            max_val = node_values[node_values <= (q3 + 1.5 * iqr)].max()
            min_outlier = node_values.min()
            max_outlier = node_values.max()

            stats = {
                "Node": node,
                "Mean": round(mean_value, 2),
                "Median": round(median_value, 2),
                "Min": round(min_val, 2),
                "Max": round(max_val, 2),
                "Q1": round(q1, 2),
                "Q3": round(q3, 2),
                "Min Outlier": round(min_outlier, 2),
                "Max Outlier": round(max_outlier, 2)
            }

            stats_table.append(stats)

    if to_plot == 'yes':
        fig, ax = plt.subplots(figsize=figsize)
        bp = ax.boxplot(box_data, patch_artist=True, widths=widths)

        for patch in bp['boxes']:
            patch.set_facecolor(box_color)

        for i, node in enumerate(valid_nodes):
            mean_value = np.mean(box_data[i])
            ax.plot([i + 1 - widths / 2, i + 1 + widths / 2], [mean_value, mean_value],
                    color=mean_color, linewidth=1, label='Mean' if i == 0 else "")

        vertical_offset = 0.1

        if to_annotate == 'yes' and what_to_annotate:
            for i, node in enumerate(valid_nodes):
                value_dict = {
                    'mean': stats_table[i]['Mean'],
                    'median': stats_table[i]['Median'],
                    'min': stats_table[i]['Min'],
                    'max': stats_table[i]['Max'],
                    'q1': stats_table[i]['Q1'],
                    'q3': stats_table[i]['Q3'],
                    'min_outlier': stats_table[i]['Min Outlier'],
                    'max_outlier': stats_table[i]['Max Outlier']
                }

                for stat in what_to_annotate:
                    if stat in value_dict:
                        value = value_dict[stat]
                        ax.annotate(f'{value:.2f}', xy=(i + 1, value),
                                    xytext=(i + 1 + 0.22, value + vertical_offset),
                                    fontsize=8, color='black', va='center')

        ax.set_xticks(np.arange(1, len(valid_nodes) + 1))
        
        if show_xticks:
            ax.set_xticklabels(valid_nodes, ha='right')
            if x_label is not None and isinstance(x_label, str):
                ax.set_xlabel(x_label)
        else:
            ax.set_xticklabels([])
            ax.set_xticks([])

        plt.title(title)
        plt.ylabel(y_label)

        mean_patch = plt.Line2D([0], [0], color=mean_color, label='Mean', linewidth=2)
        median_patch = plt.Line2D([0], [0], color=median_color, label='Median', linewidth=2)

        plt.legend(handles=[mean_patch, median_patch],
                    loc='upper center', bbox_to_anchor=(0.5, -0.05),
                    ncol=2, fontsize=10, frameon=False)

        plt.tight_layout()
        
        if figsave is not None:
            plt.savefig(figsave, format="pdf", bbox_inches="tight")
        plt.show()

    return transform_dict_into_table_several_column(stats_table)


#%% N°51 : functions to sort the values of a list in descending order

def duration_sort(data, sort_by=None, ascending=False):
    if isinstance(data, dict):
        if sort_by is None:
            raise ValueError("For dictionaries, 'sort_by' must be specified.")
        sorted_data = sorted(data.items(), key=lambda x: x[1][sort_by], reverse=not ascending)
        
    elif isinstance(data, list):
        if all(isinstance(i, (int, float)) for i in data):
            sorted_data = sorted(data, reverse=not ascending)
        else:
            raise TypeError("The list must contain numbers (int or float).")
        
    else:
        raise TypeError("The data must be a dictionary or a list of dictionaries.")

    return sorted_data

    
#%% N°52 : functions to plot load duration curves either in a single plot or stacked
    
from matplotlib.lines import Line2D
import os
import os

def load_duration_curves(data , xlabel, ylabel, title, figsize = (14, 6),
                        unit_cap='GW', unit_energy='TWh', is_together='no', ener_quan='Energy', 
                        figsave = None): 

    node_productions = []
    
    if isinstance(data, list):
        for i, value in enumerate(data):
            if all(v == 0 for v in value):
                continue
            value_sorted = duration_sort(value, ascending=False)
            peak_value = max(value_sorted)
            total_production = sum(value_sorted)
            node_productions.append((f"Node {i+1}", value_sorted, total_production))
    elif isinstance(data, dict):
        for node, value in data.items():
            if all(v == 0 for v in value):
                continue
            value_sorted = duration_sort(value, ascending=False)
            peak_value = max(value_sorted)
            total_production = sum(value_sorted)
            node_productions.append((node, value_sorted, total_production))
    
    node_productions.sort(key=lambda x: x[2], reverse=True)

    if is_together == 'no':
        plt.figure(figsize=figsize)

        legend_labels = []  # Liste pour stocker les labels de légende
        handles = []  # Liste pour stocker les handles de légende

        for node, value_sorted, total_production in node_productions:
            peak_value = max(value_sorted) 
            legend_label = f'{node}: P$_{{rated}}$ = {peak_value:.2f} {unit_cap}, {ener_quan} = {total_production / 1000:.3f} {unit_energy}'
            legend_labels.append(legend_label)
            handle, = plt.plot(value_sorted, label=legend_label)  # Garder le handle pour chaque courbe
            handles.append(handle)  # Ajouter le handle à la liste

        plt.title(title)
        plt.xlabel(xlabel)
        plt.xticks(ticks=np.append(np.arange(0, 8761, 1000), 8760))
        plt.ylabel(ylabel)
        plt.xlim((0, 8761))
        plt.legend(handles=handles, fontsize=8.5)
        plt.grid()
        
        if figsave is not None:
            plt.savefig(figsave, format="pdf", bbox_inches="tight")
        plt.show()
        
    else:
        time_steps = len(node_productions[0][1])   
        stacked_values = np.zeros(time_steps) 

        plt.figure(figsize=figsize)

        colors = plt.cm.tab10.colors 
        legend_labels = []  # Liste pour stocker les labels de légende
        handles = []  # Liste pour stocker les handles de légende

        for i, (node, value_sorted, total_production) in enumerate(node_productions):
            peak_value = max(value_sorted)   
            legend_labels.append(f'{node}: P$_{{rated}}$ = {peak_value:.2f} {unit_cap}, {ener_quan} = {total_production / 1000:.3f} {unit_energy}')
            handle = plt.fill_between(range(time_steps), stacked_values, stacked_values + value_sorted, 
                                        color=colors[i % len(colors)],
                                        label=f'{node}: P$_{{rated}}$ = {peak_value:.2f} {unit_cap}, {ener_quan} = {total_production / 1000:.3f} {unit_energy}')
            handles.append(handle)  # Ajouter le handle à la liste
            
            stacked_values += value_sorted

        # ✅ Correction du calcul de l'énergie totale agrégée en TWh
        E_tot = sum(tp for _, _, tp in node_productions) / 1000 

        if is_together == 'yes':

            # Ajouter l'étiquette d'énergie totale dans la légende, en utilisant ener_quan
            legend_label_total = r'Total {ener_quan} = $\int_{{t=0}}^{{8760}} P(t) \, dt = {0:.3f}$ {1}'.format(E_tot, unit_energy, ener_quan=ener_quan)

            # Ajouter un élément invisible pour Total Energy dans la légende
            custom_legend = Line2D([0], [0], color='none', label=legend_label_total)
            handles.append(custom_legend)  # Ajouter l'élément invisible à la légende

        plt.title(title)
        plt.xlabel(xlabel)
        plt.xticks(ticks=np.append(np.arange(0, 8761, 1000), 8760))
        plt.ylabel(ylabel)
        plt.xlim((0, 8761))

        # Mise à jour de la légende avec l'élément invisible et les autres labels
        plt.legend(handles=handles, fontsize=8.5)  # Passer la liste complète des handles
        plt.grid() 
        
        if figsave is not None:
            plt.savefig(figsave, format="pdf", bbox_inches="tight")
        plt.show()
        
    return value_sorted



def cost_duration_curves(data , xlabel, ylabel, title, figsize = (14, 6), figsave = None, unit='€/MWh'): 

    node_productions = []
    
    if isinstance(data, list):
        for i, value in enumerate(data):
            if all(v == 0 for v in value):
                continue
            value_sorted = duration_sort(value, ascending=False)
            peak_value = max(value_sorted)
            total_production = sum(value_sorted)
            node_productions.append((f"Node {i+1}", value_sorted, total_production))
    elif isinstance(data, dict):
        for node, value in data.items():
            if all(v == 0 for v in value):
                continue
            value_sorted = duration_sort(value, ascending=False)
            peak_value = max(value_sorted)
            total_production = sum(value_sorted)
            node_productions.append((node, value_sorted, total_production))
    
    node_productions.sort(key=lambda x: x[2], reverse=True)


    plt.figure(figsize=figsize)

    legend_labels = []  # Liste pour stocker les labels de légende
    handles = []  # Liste pour stocker les handles de légende

    for node, value_sorted, total_production in node_productions:
        peak_value = max(value_sorted) 
        mean_value = mean(value_sorted)
        min_value = min(value_sorted)
        legend_label = f'{node}: Max = {peak_value:.2f} {unit}, Mean = {mean_value:.2f} {unit}, Min = {min_value:.2f} {unit}'
        legend_labels.append(legend_label)
        handle, = plt.plot(value_sorted, label=legend_label)  # Garder le handle pour chaque courbe
        handles.append(handle)  # Ajouter le handle à la liste

    plt.title(title)
    plt.xlabel(xlabel)
    plt.xticks(ticks=np.append(np.arange(0, 8761, 1000), 8760))
    plt.ylabel(ylabel)
    plt.xlim((0, 8761))
    plt.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=5, fontsize=8.5)
    plt.grid()
    
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()

    return value_sorted

        
        
#%% TO HAVE ALL

def get_all_from_variable_and_parameter(dictionary, variable=None, parameter=None, to_print='no', cluster=None, global_parameter=None): 
    if cluster is None:
        cluster = get_all_cluster_names(dictionary)

    var = {} 
    cap = {} 
    par = {}
    glob_par = {}
    objective = {} 
    cost = {}
    prod = {}

    if variable is not None:
        for v in variable: 
            for clust in cluster: 
                if clust not in var:
                    var[clust] = {}
                    cap[clust] = {}
                    cost[clust] = {}
                    prod[clust] = {}

                var[clust][v] = {}
                cap[clust][v] = {}
                prod[clust][v] = {}

                try:
                    nodes = get_cluster_subnodes_names_from_variable(variable=v, cluster=clust, dictionary=dictionary)
                except:
                    try:
                        cluster_data = get_cluster_variable(node=clust, variable=v, dictionary=dictionary)
                        try:
                            var[clust][v] = cluster_data['values']
                        except:
                            var[clust][v] = cluster_data
                    except:
                        continue

                if not nodes:
                    continue

                for node in nodes:
                    try:
                        if "sub_elements" not in dictionary["solution"]["elements"].get(clust, {}): 
                            continue  

                        # Capacités
                        cluster_cap_data = {}
                        not_given = False

                        try:
                            cap_result = get_cluster_subnodes_capacities_from_nodes(nodes=[node], cluster=clust, dictionary=dictionary)
                            cluster_cap_data = cap_result
                            values = list(cap_result.values())
                            if values and isinstance(values[0], dict) and values[0].get("Max capacity", '') == 'Not given':
                                not_given = True
                        except:
                            not_given = True

                        if not_given:
                            try:
                                cluster_cap_data = get_cluster_subnodes_capacities_from_storage(nodes=[node], cluster=clust, dictionary=dictionary)
                            except:
                                cluster_cap_data = {}

                        cap[clust][v].update(cluster_cap_data)

                        # Objectif
                        if clust not in objective:
                            objective[clust] = {}

                        try:
                            obj_data = dictionary["solution"]["elements"][clust]["sub_elements"][node]["objectives"]
                            obj_values = obj_data.get("named", obj_data).values()
                            objective_sum = sum(val for val in obj_values if isinstance(val, (int, float)))
                            objective[clust][node] = objective_sum
                        except:
                            objective_sum = 0

                        # Production
                        prod_val = 0
                        try:
                            var_entry = dictionary["solution"]["elements"][clust]["sub_elements"][node]["variables"].get(v, None)
                            if var_entry is not None:
                                if isinstance(var_entry, dict):
                                    var_data = var_entry.get('values', [])
                                else:
                                    var_data = var_entry
                                prod_val = sum(var_data) if isinstance(var_data, list) else var_data
                                prod[clust][v][node] = prod_val / 1000
                        except Exception as e:
                            prod[clust][v][node] = 0
                            print(f"Error computing prod for {clust}-{node}: {e}")
                            continue

                        # Coût
                        try:
                            cost[clust][node] = (objective_sum * 1000 / prod_val) if prod_val > 0 else 0
                        except Exception as e:
                            cost[clust][node] = 0
                            print(f"Error computing cost for {clust}-{node}: {e}")

                    except KeyError as e:
                        print(f"KeyError in cluster {clust} for node {node}: {e}")
                        continue  

                # Variable globale (hors sous-nœuds)
                try:
                    cluster_data = get_timeseries_dict(dictionary, variable=v, cluster=clust)
                    if cluster_data:
                        if 'PRODUCTION' in cluster_data:
                            try:
                                special_data = get_cluster_variable(node=clust, variable=v, dictionary=dictionary)
                                var[clust][v] = special_data['values']
                            except:
                                pass
                        else:
                            var[clust][v] = cluster_data
                except:
                    try:
                        special_data = get_cluster_variable(node=clust, variable=v, dictionary=dictionary)
                        if 'values' in special_data:
                            var[clust][v] = special_data['values']
                    except:
                        continue

    if parameter is not None:
        for p in parameter:
            for clust in cluster:
                if clust not in par:
                    par[clust] = {}

                try:
                    cluster_data = get_timeseries_dict(dictionary, parameter=p, cluster=clust)
                    if cluster_data:
                        par[clust][p] = cluster_data
                except:
                    continue

    if global_parameter is not None:
        for gp in global_parameter:
            try:
                data = get_timeseries_of_global_parameters(dictionary, gp)
                glob_par[gp] = data
            except:
                continue 

    return {
        'variables': var,
        'objectives': objective,
        'prod': prod,
        'cost': cost,
        'capacities': cap,
        'parameters': par,
        'global_parameters': glob_par,
    }



#%% FUNCTION TO BAR PLOT 

def map_energy_data(dict):

    argument_names = [
        'data_prod',
        'data_cons',
        'data_demand',
        'data_charged',
        'data_discharged',
        'data_imported',
        'data_exported'
    ]
    
    mapped_args = {}
    
    for i, (key, value) in enumerate(dict.items()):
        if i < len(argument_names):
            mapped_args[argument_names[i]] = value
        else:
            print(f"Keys ignored : {key}")
    
    return mapped_args


def bar_ploter_stack_time(data_prod, data_cons, data_demand=None, data_charged=None, data_discharged=None,  
                            data_imported=None, data_exported=None, time_horizon=8760, zoom='month'):
    
    # Vérifie si les entrées sont valides (dict contenant des list ou pd.Series)
    def check_and_convert_data(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if not isinstance(value, (pd.Series, list)):
                    raise TypeError(f"Expected pd.Series or list, but got {type(value)} for key: {key}")
        else:
            raise TypeError(f"Expected a dictionary, but got {type(data)}")

    # Fonction d'application du zoom aux données
    def zoom_dict_values(data, zoom):
        if data is None:
            return None
        zoomed = {}
        for key, value in data.items():
            if isinstance(value, pd.Series):
                value = value.tolist()
            zoomed[key] = zoom_with_timestep(value, zoom=zoom)
        return zoomed

    # Vérification et zoom sur chaque type de données
    check_and_convert_data(data_prod)
    check_and_convert_data(data_cons)
    
    if data_demand:
        check_and_convert_data(data_demand)
    if data_charged:
        check_and_convert_data(data_charged)
    if data_discharged:
        check_and_convert_data(data_discharged)
    if data_imported:
        check_and_convert_data(data_imported)
    if data_exported:
        check_and_convert_data(data_exported)

    data_prod = zoom_dict_values(data_prod, zoom)
    data_cons = zoom_dict_values(data_cons, zoom)
    data_demand = zoom_dict_values(data_demand, zoom)
    data_charged = zoom_dict_values(data_charged, zoom)
    data_discharged = zoom_dict_values(data_discharged, zoom)
    data_imported = zoom_dict_values(data_imported, zoom)
    data_exported = zoom_dict_values(data_exported, zoom)

    # Détermination de l'index et du nombre d'étapes après zoom
    index = range(len(list(data_prod.values())[0]))
    n_steps = len(index)

    # Initialisation des arrays de stacking
    prod_stack = np.zeros(n_steps)
    cons_stack = np.zeros(n_steps)
    demand = np.zeros(n_steps) if data_demand else None
    charged = np.zeros(n_steps) if data_charged else None
    discharged = np.zeros(n_steps) if data_discharged else None
    imported = np.zeros(n_steps) if data_imported else None
    exported = np.zeros(n_steps) if data_exported else None

    # Ajout des valeurs empilées pour chaque catégorie de données
    def sum_node_values(data):
        # On somme les valeurs de chaque noeud (chaque liste dans le dictionnaire)
        total = 0
        for values in data.values():
            total += np.sum(np.array(values))/1000
        return total

    prod_stack += sum_node_values(data_prod)
    cons_stack += sum_node_values(data_cons)
    if data_demand: 
        cons_stack += sum_node_values(data_demand)
    if data_charged:
        charged += sum_node_values(data_charged)
    if data_discharged:
        discharged += sum_node_values(data_discharged)
    if data_imported:
        imported += sum_node_values(data_imported)
    if data_exported:
        exported += sum_node_values(data_exported)

    # Position des barres
    x = np.arange(n_steps)
    bar_width = 0.4

    # Création du graphique
    fig, ax = plt.subplots(figsize=(14, 6))

    # Barres de gauche : production + discharge
    ax.bar(x - bar_width/2, prod_stack, width=bar_width, label='Production', color='tab:blue')
    if discharged is not None:
        ax.bar(x - bar_width/2, discharged, width=bar_width, bottom=prod_stack, label='Discharged', color='tab:cyan')

    # Barres de droite : consumption + charge
    ax.bar(x + bar_width/2, cons_stack, width=bar_width, label='Consumption', color='tab:orange')
    if charged is not None:
        ax.bar(x + bar_width/2, charged, width=bar_width, bottom=cons_stack, label='Charged', color='tab:green')

    # Import/Export
    if imported is not None:
        ax.bar(x - bar_width, imported, width=bar_width, label='Imported', color='tab:red')
    if exported is not None:
        ax.bar(x + bar_width, exported, width=bar_width, label='Exported', color='tab:purple')

    # Légendes et mise en forme
    ax.set_xticks(x)
    ax.set_xticklabels(x, rotation=45)
    ax.set_ylabel('Energy (GWh)')
    ax.set_title(f'Production/Discharge vs Consumption/Charge per {zoom.capitalize()}')
    ax.legend()
    ax.grid(axis='y')
    plt.tight_layout()
    plt.show()


def get_timeseries_of_global_parameters(dictionary, parameters):
    global_parameter = {}
    dic_nodes = dictionary["model"]["global_parameters"]
    
    if isinstance(parameters, list):
        for parameter in parameters:
            if parameter in dic_nodes:
                global_parameter[parameter] = dic_nodes[parameter]
    else:
        if parameters in dic_nodes:
            global_parameter = {parameters: dic_nodes[parameters]}   

    return global_parameter




def convert_mmr_to_dict(obj):
    return gf.transform_makemereadable_into_dict(obj)





def process_commodity(model_dict, 
                    variable_key, capacity_key, 
                    clusters, node_to_remove, 
                    unit_power, unit_energy):
    """
    Automatically generates data for a commodity,
    skipping clusters where the variable/capacity is absent.
    """ 

    # 1️⃣ Fusion des séries temporelles – on ne garde que les clusters valides
    prod_dicts, valid_prod_clusters = [], []
    for c in clusters:
        if c in model_dict['variables'] and variable_key in model_dict['variables'][c]:
            prod_dicts.append(model_dict['variables'][c][variable_key])
            valid_prod_clusters.append(c)
        else:
            print(f"⚠ Variable '{variable_key}' absente pour cluster '{c}', skipping.")
    if not prod_dicts:
        return {}
    merged_energy = merge_dictionaries(*prod_dicts, name=valid_prod_clusters)

    # 2️⃣ Fusion des capacités
    cap_dicts, valid_cap_clusters = [], []
    for c in clusters:
        if c in model_dict['capacities'] and capacity_key in model_dict['capacities'][c]:
            cap_dicts.append(model_dict['capacities'][c][capacity_key])
            valid_cap_clusters.append(c)
        else:
            print("")
    if not cap_dicts:
        return {'merged_energy': merged_energy}
    merged_cap = merge_dictionaries(*cap_dicts, name=valid_cap_clusters)

    # 3️⃣ Table des capacités
    cap_filtered = remove_keys(merged_cap, node_to_remove)
    cap_table = transform_dict_into_table_several_column(cap_filtered, zero_print='no', show='no')

    # 4️⃣ Statistiques capacité vs production
    stats = cap_pow_energy_dict(
        energy_dict=merged_energy,
        capacity_dict=merged_cap,
        unit_power=unit_power,
        unit_energy=unit_energy,
        total_return='no'
    )
    stats_filtered = remove_keys(stats, node_to_remove)
    stats_table = transform_dict_into_table_several_column(stats_filtered, zero_print='no', show='no')

    return {
        'merged_energy': merged_energy,
        'merged_cap': merged_cap,
        'cap_table': cap_table,
        'stats': stats,
        'stats_table': stats_table
    }


def process_commodity_all(dict, node_to_remove, cluster, variable, commodity, plot_folder, color = 'black', unit = 'Gwh', multiply=1, to_plot = 'yes'):


    for index, var in enumerate(variable): 

        print(colored(f'{commodity[index]}:', 'black', attrs=['bold']))

        results = process_commodity(
            dict,
            variable_key=var, capacity_key=var,
            clusters=cluster,
            node_to_remove=node_to_remove,
            unit_power=unit[0], unit_energy=unit[1])
        
        if to_plot == 'yes':
            try:
                bar_ploter_stack_dict(
                    data=results['stats'],
                    color_palette=color,
                    cap_unit=unit[0], ener_unit=unit[1],
                    is_energy='no', is_power='no',
                    commodity=commodity[index],
                    plot_folder=plot_folder, 
                    multiply=multiply)
            except:
                print(f'No data for {commodity[index]}')

            print('')
        
        return results
        
        
######################        
        
# def get_cluster_subnodes_capacities_from_nodes(nodes,cluster,dictionary,name_capacity="new_capacity",
#                                                name_capacity_0="pre_installed_capacity",name_capacity_max="max_capacity"):
#     # Create a dictionary with the capacity, the limit on the capacity and the preinstalled capacity for each node in the list
#     # "nodes". "new_capacity" is the name of the variable corresponding to the capacity, "name_capacity_0" is the name used for
#     # parameter corresponding to the preinstalled capacity and "name_capacity_max" is the parameter corresponding to the maximum 
#     # capacity that can be installed
#     # if no preinstalled capacity or max capacity used in the code, just insert a empty char for those inputs like that: ''
#     capacities = {}
#     dic_nodes_var = dictionary["solution"]["elements"][cluster]["sub_elements"]
#     dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]
#     for node in nodes:  
#         if name_capacity in dic_nodes_var[node]["variables"]:
#             capacity = get_cluster_element_variable(cluster,node,name_capacity,dictionary)
#             capacity = capacity['values'][0]
#         else:
#             capacity = 0
#         if name_capacity_0 in dic_nodes_par[node]["parameters"]:
#             capacity_0 = get_cluster_element_parameter(cluster,node,name_capacity_0,dictionary)
#             capacity_0 = capacity_0[0]
#         else:
#             capacity_0 = 0
#         if name_capacity_max in dic_nodes_par[node]["parameters"]:
#             capacity_max = get_cluster_element_parameter(cluster,node,name_capacity_max,dictionary)
#             capacity_max = capacity_max[0]
#         else:
#             capacity_max = 'Not given'
#         total_capacity = capacity_0 + capacity
#         key = node
#         capacities[key] = {"Preinstalled capacity":capacity_0,"Added capacity":capacity, "Total capacity":total_capacity, "Max capacity": capacity_max}
#     return capacities


def get_capex_from_cluster_subnodes_capacity(cluster,capex_name,capacities,dictionary):
    # create a dictionary calculating the total capex cost of each node where a capacity is calculated 
    # from the name used for the capex in node and the dictionary of capacity
    capex_all = {}
    dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]
    for node in capacities:
        if isinstance(capex_name, str):
            if capex_name in dic_nodes_par[node]["parameters"]:
                capex = dic_nodes_par[node]["parameters"][capex_name][0]
            else:
                capex = 0
        elif isinstance(capex_name, list):
            for capex_buffer in capex_name:
                if capex_buffer in dic_nodes_par[node]["parameters"]:
                    capex += dic_nodes_par[node]["parameters"][capex_buffer][0]
                    break
                else:
                    capex = 0
        add_cap = capacities[node]["Added capacity"] 
        
        capex_all[node] = {
            "Capex": round(capex, 3),
            "Added capacity": round(add_cap, 3), 
        }
        
    return capex_all


def get_capex_from_cluster_storage_capacities(cluster, capex_name, capacities, dictionary):
    """
    Calcule le CAPEX total pour chaque noeud de stockage (power/energy) à partir de leurs capacités ajoutées.
    """
    capex_all = {}
    dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]

    for node in capacities:
        # nettoyage du nom pour obtenir le vrai nom du noeud (ex : "BATTERIES power" → "BATTERIES")
        if " power" in node:
            base_node = node.replace(" power", "")
        elif " energy" in node:
            base_node = node.replace(" energy", "")
        else:
            base_node = node

        if base_node not in dic_nodes_par:
            print(f"[Warning] Node '{base_node}' not found in cluster '{cluster}' → skipped.")
            continue

        capex = 0
        if isinstance(capex_name, str):
            if capex_name in dic_nodes_par[base_node]["parameters"]:
                capex = dic_nodes_par[base_node]["parameters"][capex_name][0]
        elif isinstance(capex_name, list):
            for capex_buffer in capex_name:
                if capex_buffer in dic_nodes_par[base_node]["parameters"]:
                    capex = dic_nodes_par[base_node]["parameters"][capex_buffer][0]
                    break

        try:
            add_cap = capacities[node]["Added capacity"]
        except KeyError:
            print(f"[Warning] 'Added capacity' not found for node '{node}' → set to 0.")
            add_cap = 0

        capex_all[node] = {
            "Capex": round(capex, 3),
            "Added capacity": round(add_cap, 3)
        }

    return capex_all


def get_fom_from_cluster_subnodes_capacity(cluster,fom_name,capacities,dictionary):
    # create a dictionary calculating the total fixed operation and maintenance cost of each node where 
    # a capacity is calculated from the name used for the fom in node and the dictionary of capacity
    fom_all = {}
    dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]
    for node in capacities: 
        if isinstance(fom_name, str):
            if fom_name in dic_nodes_par[node]["parameters"]:
                fom = dic_nodes_par[node]["parameters"][fom_name][0]
            else:
                fom = 0
        elif isinstance(fom_name, list):
            for fom_buffer in fom_name:
                if fom_buffer in dic_nodes_par[node]["parameters"]:
                    fom += dic_nodes_par[node]["parameters"][fom_buffer][0]
                    break
                else:
                    fom = 0
        add_cap = capacities[node]["Total capacity"] 
        
        fom_all[node] = {
            "Fom": round(fom, 3),
            "Added capacity": round(add_cap, 3), 
        }
        
    return fom_all    


def get_fom_from_cluster_storage_capacities(cluster, fom_name, capacities, dictionary):
    """
    Calcule le FOM total pour chaque noeud de stockage (power/energy) à partir de leurs capacités totales.
    """
    fom_all = {}
    dic_nodes_par = dictionary["model"]["nodes"][cluster]["sub_nodes"]

    for node in capacities:
        # Extraire le nom du noeud (ex : "BATTERIES power" → "BATTERIES")
        if " power" in node:
            base_node = node.replace(" power", "")
        elif " energy" in node:
            base_node = node.replace(" energy", "")
        else:
            base_node = node

        if base_node not in dic_nodes_par:
            print(f"[Warning] Node '{base_node}' not found in cluster '{cluster}' → skipped.")
            continue

        fom = 0
        if isinstance(fom_name, str):
            if fom_name in dic_nodes_par[base_node]["parameters"]:
                fom = dic_nodes_par[base_node]["parameters"][fom_name][0]
        elif isinstance(fom_name, list):
            for fom_buffer in fom_name:
                if fom_buffer in dic_nodes_par[base_node]["parameters"]:
                    fom = dic_nodes_par[base_node]["parameters"][fom_buffer][0]
                    break

        try:
            total_cap = capacities[node]["Total capacity"]
        except KeyError:
            print(f"[Warning] 'Total capacity' not found for node '{node}' → set to 0.")
            total_cap = 0

        fom_all[node] = {
            "Fom": round(fom, 3),
            "Added capacity": round(total_cap, 3),
            "Total capacity": round(total_cap, 3)
        }

    return fom_all


def get_objective_from_cluster_subnodes_variable(cluster, nodes, dictionary, max_constraint = 'yes'):
    
    dic_nodes_var = dictionary["solution"]["elements"][cluster]["sub_elements"]
    
    obj_cluster = 0 
    obj_dict = {} 
    
    for node in nodes:
        node_sum = 0  # Initialize node_sum for each node
        if node in dic_nodes_var and "objectives" in dic_nodes_var[node] and "named" in dic_nodes_var[node]["objectives"]:
            obj_name = dic_nodes_var[node]["objectives"]["named"]  
            for key in obj_name.keys():
                
                if max_constraint == 'yes':
                    
                    if key == 'co2_capt_cost'  and 'PCCC' not in node:
                        node_sum -= obj_name[key]
                    elif key == 'export_cost'and node != 'CO2_EXPORT':    
                        node_sum -= obj_name[key]
                    else:
                        node_sum += obj_name[key] 
                        
                else:
                    node_sum += obj_name[key] 
                    
            # obj_dict[node] = node_sum 
            obj_cluster += node_sum
            
        obj_dict[node] = {
            "Cost [M€]": round(node_sum, 3) 
        }
    
    return obj_dict, obj_cluster


def get_objective_from_cluster_storage(cluster, nodes, dictionary):
    
    dic_nodes_var = dictionary["solution"]["elements"][cluster]["sub_elements"]

    obj_dict = {} 
    
    for node in nodes:
        node_sum = 0  # Initialize node_sum for each node
        pow_sum = 0
        energy_sum = 0
        
        if node in dic_nodes_var and "objectives" in dic_nodes_var[node] and "named" in dic_nodes_var[node]["objectives"]:
            obj_name = dic_nodes_var[node]["objectives"]["named"]  
            for key in obj_name.keys():

                if 'power' in key:
                    pow_sum += obj_name[key]
                if 'energy' in key:
                    energy_sum += obj_name[key]
                node_sum += obj_name[key]
                        
        obj_dict[node] = {
            "Cost power [M€]": round(pow_sum, 3), 
            'Cost energy [M€]': round(energy_sum, 3),
            'Total cost [M€]': round(node_sum, 3)
        }
    
    return obj_dict



def get_total_cluster_subnodes_cost(capex_dict,fom_dict,vom_dict,obj_dict, all_var = 'yes', type_node = None, just_prod = 'no', time= 8760):
    
    total_cost = {}
    for node in capex_dict:
        capacity = fom_dict[node]["Added capacity"] 
        capex = capex_dict[node]["Capex"]
        if node in fom_dict: 
            fom = fom_dict[node]["Fom"]
        else: 
            fom = 0
        if node in vom_dict: 
            vom = vom_dict[node]["Vom"]
            total_prod = vom_dict[node]["Total production"]
        else: 
            vom = 0
            total_prod = 0 
        if node in obj_dict:
            tot_cost = obj_dict[node]["Cost [M€]"]
        else:
            tot_cost = 0 
        

        load_factor = 100*total_prod/ (capacity * time) if capacity > 0 else 0
        
        if all_var == 'yes':
            if type_node is None:
                metrics = {
                    "CAPEX [M€/GW]":      round(capex, 3),
                    "FOM [M€/GW]":        round(fom, 3),
                    "VOM [M€/(GW.y)]":    round(vom, 3), 
                    "Total production [TWh/y]": round(total_prod/1000, 3),
                    "Total capacity [GW]":      round(capacity, 3),
                    "Total cost [M€]":         round(tot_cost, 3),
                    "Load factor [%]":         round(load_factor, 1)
                }
            else:
                metrics = {
                    "CAPEX [M€/(kton/h)]":    round(capex, 3),
                    "FOM [M€/(kton/h)]":      round(fom, 3),
                    "VOM [M€/(kton/h).y]":    round(vom, 3), 
                    "Total production [Mt/y]":  round(total_prod/1000, 3),
                    "Total capacity [kt/h]":    round(capacity, 3),
                    "Total cost [M€]":         round(tot_cost, 3),
                    "Load factor [%]":         round(load_factor, 1)
                }
        
        
        else:
            
            if type_node is None:
                metrics = { 
                    "Total production [TWh/y]": round(total_prod/1000, 3),
                    "Total capacity [GW]":      round(capacity, 3),
                    "Total cost [M€]":         round(tot_cost, 3),
                    "Load factor [%]":         round(load_factor, 1)
                }
            else:
                metrics = {
                    "Total production [Mt/y]":  round(total_prod/1000, 3),
                    "Total capacity [kt/h]":    round(capacity, 3),
                    "Total cost [M€]":         round(tot_cost, 3),
                    "Load factor [%]":         round(load_factor, 1)
                }
                
        if just_prod == 'yes':
            
            if type_node is None:
                metrics = { 
                    "Total production [TWh/y]": round(total_prod/1000, 3) 
                }
            else:
                metrics = { 
                    "Total production [Mt/y]":  round(total_prod/1000, 3) 
                }
                

        # Ajout conditionnel de la dernière clé pour éviter division par zéro
        if total_prod != 0 and just_prod == 'no':
            if type_node is None:
                metrics["Total cost [€/MWh]"] = round(tot_cost / (total_prod / 1000), 3)
            else:
                metrics["Total cost [€/ton]"]  = round(tot_cost / (total_prod / 1000), 3)

        # Affectation finale
        total_cost[node] = metrics
                        
    return total_cost


def all_cost_prod_dict_per_cluster(dict, cluster, variable, folder=None, file_name=None, all_var='yes', zero_node='yes', show ='yes',just_prod = 'no', type_node = None):
    """
    Fonction pour calculer les coûts de production, CAPEX, FOM, VOM et coûts totaux des sous-noeuds d’un cluster.
    Elle gère aussi bien les variables simples que multiples (ex: stockage avec puissance et énergie).
    """
    total_cost_tables_merged = {}
    cost_dicts = []

    for clus in cluster:
        # Récupération des noms des sous-noeuds en fonction de la variable (ou première si liste)
        if isinstance(variable, list):
            nodes = get_cluster_subnodes_names_from_variable(variable[0], clus, dict)
        else:
            nodes = get_cluster_subnodes_names_from_variable(variable, clus, dict)

        # Récupération des capacités
        capacities = get_cluster_subnodes_capacities_from_nodes(nodes, clus, dict)
        
        # Si les capacités max ne sont pas données, on bascule sur les versions "storage"
        # Exclude 'LOAD_SHIFTING' node from special storage handling
        if nodes and capacities.get(nodes[0], {}).get('Max capacity') == 'Not given' and nodes[0] != 'LOAD_SHIFTING' and nodes[0] != "DESALINATION" and just_prod == 'no':
            capacities = get_cluster_subnodes_capacities_from_storage(nodes, clus, dict)
            cost = get_objective_from_cluster_storage(clus, nodes, dict)
            capex = get_capex_from_cluster_storage_capacities(clus, ['capex_power', 'capex_energy'], capacities, dict)
            fom   = get_fom_from_cluster_storage_capacities(clus, ['fom_power', 'fom_energy'], capacities, dict)
            vom   = get_vom_from_cluster_storage_variable(clus, ['vom_power', 'vom_energy'], variable, capacities, dict) 
            cost_dict = get_total_cluster_storage_cost(capex, fom, vom, cost, all_var=all_var, type_node=type_node)
        
        else:
            cost, _ = get_objective_from_cluster_subnodes_variable(clus, nodes, dict)
            capex = get_capex_from_cluster_subnodes_capacity(clus, 'capex', capacities, dict)
            fom   = get_fom_from_cluster_subnodes_capacity(clus, 'fom', capacities, dict)
            vom   = get_vom_from_cluster_subnodes_variable(clus, 'vom', variable, capacities, dict) 
            cost_dict = get_total_cluster_subnodes_cost(capex, fom, vom, cost, all_var=all_var,just_prod = just_prod, type_node=type_node)

        # Supprime les noeuds à capacité nulle si demandé
        if zero_node == 'no':
            cost_dict = {k: v for k, v in cost_dict.items() if v.get("Total capacity [GW]", 0)}

        cost_dicts.append(cost_dict)

    merged_dict = merge_dictionaries(*cost_dicts, name=cluster) 
    merged_table = transform_dict_into_table_several_column(merged_dict,show=show)

    # Correction ici pour utiliser une clé string même si variable est une liste
    var_key = '_'.join(variable) if isinstance(variable, list) else variable
    total_cost_tables_merged[var_key] = merged_table

    if folder is not None:
        export_name = file_name if file_name is not None else f'cost_and_prod_for_{var_key}'
        save_table_into_csv(merged_table, export_name, folder=folder)

    return merged_table, merged_dict
    


def node_objective(cluster, model,max_constraint):
    
    nodes = get_all_cluster_subnodes_names(cluster, model)  
    obj_dict, obj_cluster = get_objective_from_cluster_subnodes_variable(cluster, nodes, model, max_constraint)
    return obj_dict, obj_cluster


def cluster_objective(cluster, model):
    
    cost = 0
    objective = model['solution']["elements"][cluster]["objectives"]["named"]
    for clust in objective.keys():
        cost += objective[clust]
    return cost 


def system_cost(model, approx=None, max_constraint = 'yes'):
    
    cluster_name = model['solution']["elements"]  
    cluster_dict = {}
    node_dict = {}
    
    for cluster in cluster_name.keys():
        
        try:
            try:
                cluster_obj = cluster_objective(cluster, model) 
            except: 
                cluster_obj = 0
            
            
            try:
                nodes_cost, cluster_node_cost = node_objective(cluster, model,max_constraint)
                node_dict[cluster] = nodes_cost
            except:
                cluster_node_cost = 0
                
            if approx is not None:
                cluster_dict[cluster] = {
                    "Cluster cost [M€]": round(cluster_obj, approx),
                    "Total node cost [M€]": round(cluster_node_cost, approx),
                    "Total cluster cost [M€]": round(cluster_obj + cluster_node_cost, approx)
                }
            
            else:
                cluster_dict[cluster] = {
                    "Cluster cost [M€]": cluster_obj,
                    "Total node cost [M€]": cluster_node_cost,
                    "Total cluster cost [M€]": cluster_obj + cluster_node_cost
                }
        
        except:
            pass
        
    return cluster_dict, node_dict


def divide_any_mapping(data, divisor):
    """Divise toutes les valeurs par divisor tout en conservant la structure attendue par pf.zoom_with_timestep."""
    import pandas as pd

    # Cas dict avec clé "values"
    if isinstance(data, dict) and "values" in data:
        return {"values": [v / divisor for v in data["values"]]}

    # Cas dict simple {clé: liste}
    if isinstance(data, dict) and all(isinstance(v, list) for v in data.values()):
        return {k: [x / divisor for x in v] for k, v in data.items()}

    # Cas dict simple {clé: valeur unique} → on transforme en liste 1 élément
    if isinstance(data, dict):
        return {k: [v / divisor] for k, v in data.items()}

    # Cas liste brute
    if isinstance(data, list):
        return [v / divisor for v in data]

    # Cas pandas.Series
    if isinstance(data, pd.Series):
        return list((data / divisor).values)

    raise TypeError(f"Type non supporté : {type(data)}")



def negate_values(data):
    """Inverse le signe des valeurs tout en conservant la structure."""
    import pandas as pd

    # Cas dict {clé: valeur unique}
    if isinstance(data, dict) and all(isinstance(v, (int, float)) for v in data.values()):
        return {k: -v for k, v in data.items()}

    # Cas dict {clé: liste}
    if isinstance(data, dict) and all(isinstance(v, list) for v in data.values()):
        return {k: [-x for x in v] for k, v in data.items()}

    # Cas liste simple
    if isinstance(data, list):
        return [-x for x in data]

    # Cas pandas.Series
    if isinstance(data, pd.Series):
        return (-data).to_dict()

    raise TypeError(f"Format non supporté : {type(data)}")




def capacity_check(model_dict, cluster, variables, nodes, storage = ' power', multiply = 1):
    
    try: 
        capacity = model_dict['capacities'][cluster][variables][nodes]['Total capacity']
    except:
        capacity = model_dict['capacities'][cluster][variables][nodes + storage]['Total capacity']
        
    prod = model_dict['prod'][cluster][variables][nodes]
    max_prod = max(model_dict['variables'][cluster][variables][nodes])
    mean_prod = mean(model_dict['variables'][cluster][variables][nodes])

    
    data = {nodes: {
        'capacity': capacity * multiply,
        'max': max_prod * multiply,
        'mean': mean_prod * multiply,
        'production': prod * multiply}
    }
    
    return data
    
    
def get_tricolor_shades(base_color):
    """
    Retourne un dégradé tricolore (foncé, moyen, clair) pour une couleur de base : blue, red, green, orange, purple
    """
    color_schemes = {
        "blue":   ("#08519c", "#3182bd", "#bdd7e7"),  # foncé, moyen, clair
        "red":    ("#a50f15", "#de2d26", "#fcbba1"),
        "green":  ("#006d2c", "#31a354", "#a1d99b"),
        "orange": ("#994404", "#d95f0e", "#fdd0a2"),
        "purple": ("#54278f", "#756bb1", "#dadaeb"),
        "gray":   ("#252525", "#636363", "#bdbdbd")
    }
    return color_schemes.get(base_color.lower(), color_schemes["blue"])


def plot_capacity_and_production_dual_axis(data, title="Scenario Overview", color="blue", color_write = 'black', x_label_title= 'Capacity [GW]', 
                                            y_label_title = 'Production [TWh/y]', step_cap = 2, step_energy = 2, offset = 0.18, offset_energy = 0.03,
                                            figsave = None, figsize = (10,5)):

    # Dégradé selon la couleur choisie
    color_mean, color_peak, color_installed = get_tricolor_shades(color)

    techs = list(data.keys())
    mean_power = [data[t]['mean'] for t in techs]
    max_power = [data[t]['max'] for t in techs]
    capacity = [data[t]['capacity'] for t in techs]
    production = [data[t]['production'] for t in techs]
    x = np.arange(len(techs))
    width = 0.5

    # Segments
    peak_extra = [max_ - mean for max_, mean in zip(max_power, mean_power)]
    installed_cap = [cap - max_ for cap, max_ in zip(capacity, max_power)]

    fig, ax1 = plt.subplots(figsize=figsize)

    # Stack bars avec dégradé
    bar1 = ax1.bar(x, mean_power, width=width, label="Average Power", color=color_mean)
    bar2 = ax1.bar(x, peak_extra, width=width, bottom=mean_power, label="Peak Power", color=color_peak)
    bar3 = ax1.bar(x, installed_cap, width=width, bottom=[m + p for m, p in zip(mean_power, peak_extra)],
                    label="Installed Capacity", color=color_installed)

    ax1.set_ylabel(x_label_title, color=color)
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.set_xticks(x)
    ax1.set_xticklabels(techs, fontsize=10)
    ax1.set_yticks(np.arange(0, max(capacity) + step_cap, step_cap))
    ax1.set_title(title)

    # Labels sur barres
    for i in range(len(x)):
        # Calculate a small offset to the left, but keep labels inside the plot 
        ax1.text(x[i] - offset, capacity[i], f"{capacity[i]:.2f}", ha='right', va='bottom', fontsize=7, color=color)
        ax1.text(x[i] - offset, max_power[i], f"{max_power[i]:.2f}", ha='right', va='bottom', fontsize=7, color=color)
        ax1.text(x[i] - offset, mean_power[i], f"{mean_power[i]:.2f}", ha='right', va='bottom', fontsize=7, color=color)

    # Axe 2 : production
    ax2 = ax1.twinx()
    ax2.set_ylabel(y_label_title, color=color_write)
    ax2.tick_params(axis='y', labelcolor="black", rotation = 0)
    ax2.scatter(x, production, marker='*', s=130, color=color_write, label='Production', zorder=5)
    ax2.set_yticks(np.arange(0, max(production) + step_energy, step_energy))
    ax2.tick_params(axis='y', labelsize=9)

    for i, val in enumerate(production):
        ax2.text(x[i] + offset + offset_energy, val, f"{val:.2f}", ha='center', va='bottom', fontsize=7, color=color_write)

    # Légende
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    fig.legend(handles1 + handles2, labels1 + labels2,
                bbox_to_anchor=(0.5, -0.02),
                loc='upper center',
                ncol=4,
                fontsize=9)

    ax1.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
    
    
    
def sum_multiple_dict(*datas):
    """
    Sums the values of several dicts/lists/numbers.
    Each element can be:
        - un nombre
        - une liste de nombres
        - un dictionnaire avec valeurs imbriquées
    """
    def sum_dict_value(data):
        if isinstance(data, dict):
            return (sum_dict_value(v) for v in data.values())
        elif isinstance(data, list):
            return (sum_dict_value(v) for v in data)
        else:
            return data

    return (sum_dict_value(d) for d in datas)


from collections import defaultdict

def sum_dicts_or_lists(*args):
    # Si ce sont tous des dictionnaires
    if all(isinstance(a, dict) for a in args):
        result = defaultdict(float)
        for d in args:
            for k, v in d.items():
                result[k] += v
        return dict(result)
    
    # Si ce sont tous des listes
    elif all(isinstance(a, list) for a in args):
        return [sum(vals) for vals in zip(*args)]
    
    else:
        raise TypeError("Tous les arguments doivent être soit des dicts soit des listes")
    
    
    
    
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def format_time_axis(ax, start_date="2025-01-01", periods=8760, freq="H", fmt="month"):
    time_index = pd.date_range(start=start_date, periods=periods, freq=freq)
    ax.set_xlim(time_index[0], time_index[-1])
    
    if fmt == "hour":
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %Hh'))
    elif fmt == "week":
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('W%W - %b'))
    elif fmt == "month":
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    else:
        raise ValueError("fmt doit être 'hour', 'week' ou 'month'.")
    
    ax.figure.autofmt_xdate()
    return time_index




from itertools import accumulate, islice

def month_xticks(data, unit="hour", align="start", strict=False):
    """
    Non-leap-year only (8760/365/52/12).
    - data: list/array/Series
    - unit: "hour" | "day" | "week" | "month"
    - align: "start" (month start) | "center" (mid-month)
    - strict: if True, raise if len(data) != target; if False, trim extra samples from the tail
    Returns: data_aligned, positions, labels, n_target
    """
    unit_to_n = {"hour": 8760, "day": 365, "week": 52, "month": 12}
    if unit not in unit_to_n:
        raise ValueError('unit must be one of {"hour","day","week","month"}')
    n_target = unit_to_n[unit]

    L = len(data)
    if L < n_target:
        raise ValueError(f"Data too short for a full non-leap year ({n_target}). Got {L}.")
    if L > n_target:
        if strict:
            raise ValueError(f"Data longer than {n_target}. Got {L}. Use strict=False to trim.")
        data = data[:n_target]  # keep the first full calendar year starting Jan 1, 00:00

    months = ["January","February","March","April","May","June",
                "July","August","September","October","November","December"]
    dim = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # days in month (non-leap)

    month_start_days = [0] + list(accumulate(dim[:-1]))               # 0,31,59,...
    month_center_days = [s + d/2 for s, d in zip(month_start_days, dim)]
    base_days = month_center_days if align == "center" else month_start_days

    if unit == "hour":
        positions = [int(round(d * 24)) for d in base_days]
    elif unit == "day":
        positions = [int(round(d)) for d in base_days]
    elif unit == "week":
        pos = [min(int(round(d / 7)), 51) for d in base_days]
        fixed, last = [], -1
        for p in pos:
            p = max(p, last + 1)
            p = min(p, 51)
            fixed.append(p)
            last = p
        positions = fixed
    else:  # unit == "month"
        positions = list(range(12))

    labels = months
    return data, positions, labels, n_target
