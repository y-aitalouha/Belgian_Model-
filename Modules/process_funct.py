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

def get_cluster_subnodes_capacities_from_storage(nodes,cluster,dictionary,name_capacity_power= "name_capacity_power",
                                                 name_capacity_0_power= "pre_installed_capacity_power",
                                                 name_capacity_max_power= "max_capacity_power",
                                                 name_capacity_energy= "name_capacity_energy",
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
        key = node+' power'
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
        key = node+' energy'
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
        tot_cap = capacities[node]["Added capacity"]
        inst_cost = capex * tot_cap 
        capex_all[node] = {"Capex":capex,"Added capacity":tot_cap,"Installation cost":inst_cost}
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
        fom_all[node] = {"Fom":fom,"Total capacity":tot_cap,"tot fom cost":fom_cost}
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
        vom_all[node] = {"Vom":vom,"Total production":total_prod,"tot vom cost":vom_cost}    
    return vom_all

#%% N°27 : def get_total_cluster_subnodes_cost(capex_dict,fom_dict,vom_dict):

def get_total_cluster_subnodes_cost(capex_dict,fom_dict,vom_dict):
    total_cost = {}
    for node in capex_dict:
        capacity = fom_dict[node]["Total capacity"]
        inst_cost = capex_dict[node]["Installation cost"]
        if node in fom_dict:
            fom_tot = fom_dict[node]["tot fom cost"]
        else:
            fom_tot = 0
        if node in vom_dict:
            vom_tot = vom_dict[node]["tot vom cost"]
        else:
            vom_tot = 0
        tot_cost = inst_cost + fom_tot + vom_tot
        total_cost[node] = {"Total capacity":capacity,"Installation cost":inst_cost,"Fixed OM cost":fom_tot,"Variable OM cost":vom_tot,"Total Cost":tot_cost}
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
    """
    Merge multiple dictionaries. If `name` is provided (a list of suffixes),
    append the suffix to each key of the corresponding dictionary.

    :param dictionaries: dicts to be merged
    :param name: list of suffixes, one per dictionary
    :return: merged dictionary with optionally renamed keys
    """
    dict_merged = {}

    for idx, dictionary in enumerate(dictionaries):
        suffix = f" ({name[idx]})" if name and idx < len(name) else ""
        renamed_dict = {f"{k}{suffix}": v for k, v in dictionary.items()}
        dict_merged.update(renamed_dict)

    return dict_merged

#%% N°34 : def merge_lists(*lists):

def merge_lists(*lists):
    # merge dictionaries together
    list_merged = []
    for list in lists:
        list_merged += list
    return list_merged

#%% N°35 : def transform_dict_into_table(data):

def transform_dict_into_table(data):
    # Convert dictionary into dataframe table
    table = pd.DataFrame.from_dict(data, orient='index')
    return table

#%% N°35bis : def transform_dict_into_table(data):

def transform_dict_into_table_several_column(data, zero_print = 'yes', show = 'yes'): 
    # Convertir la liste de dictionnaires en DataFrame sans fournir les colonnes
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
#%% N°36 : def save_table_into_csv(table,table_name):

def save_table_into_csv(table,table_name):
    # save dataframe table as a csv file
    table.to_csv(r'' + table_name+'.csv')

#%% N°37 : def save_table_into_excel(table,table_name):

def save_table_into_excel(table,table_name):
    # save dataframe table as a csv file
    table.to_excel(r'' + table_name+'.xlsx')

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

def zoom_with_timestep(data, zoom = 'hour', mean_or_sum='sum', zero_nodes='no'): 
   
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

def bar_ploter_stack_dict(data, color_palette, cap_unit, ener_unit, commodity, plot_folder,
                          to_annotate='yes', text_color='white',  weight='bold',
                          bar_width=0.3, rotation=90, percentage=0.95,
                          is_power='yes', is_energy='yes', is_combined='yes',
                          format=(10, 6), format_combined=(14, 6), multiply=1):


    filtered_nodes = [
        tech for tech, series in data.items()
        if series['Installed capacity [GW]'] * multiply > 0 or
           series['Max capacity [GW]'] * multiply > 0 or
           series['Mean capacity [GW]'] * multiply > 0
    ]

    if not filtered_nodes:
        print("❌ No data to display (all capacities are zero after scaling).")
        return

    base_height = 1.5
    max_height = 8
    calculated_height = min(base_height + 0.8 * len(filtered_nodes), max_height)
    adjusted_format = (format[0], calculated_height)
    adjusted_format_combined = (format_combined[0], calculated_height)

    data_power = {
        "Installed Capacity": [data[tech]['Installed capacity [GW]'] * multiply for tech in filtered_nodes],
        "Max Capacity": [data[tech]['Max capacity [GW]'] * multiply for tech in filtered_nodes],
        "Mean Capacity": [data[tech]['Mean capacity [GW]'] * multiply for tech in filtered_nodes]
    }
    df_power = pd.DataFrame(data_power, index=filtered_nodes)

    data_ener = {
        "Energy or Quantity": [data[tech]['Total energy [TWh]'] * multiply for tech in filtered_nodes]
    }
    df_ener = pd.DataFrame(data_ener, index=filtered_nodes)

    os.makedirs(plot_folder, exist_ok=True)

    if is_power == 'yes':
        fig, ax = plt.subplots(figsize=adjusted_format)
        gradient_colors = generate_gradient(color_palette, 3)

        for i, (col, color) in enumerate(zip(df_power.columns, gradient_colors)):
            bars = ax.barh(df_power.index, df_power[col], label=col, color=color, height=bar_width)
            for bar in bars:
                width = bar.get_width()
                if width > 0 and to_annotate == 'yes':
                    ax.text(width * percentage, bar.get_y() + bar.get_height() / 2,
                            f'{width:.2f}', ha='left', va='center',
                            fontsize=7, color=text_color, weight=weight, rotation=rotation)

        ax.set_ylabel(cap_unit)
        ax.set_title(f"{commodity} - Capacity", fontsize=14)
        ax.tick_params(axis='y', labelsize=8)
        ax.legend()
        ax.grid(axis='x')
        plt.tight_layout()
        plt.savefig(os.path.join(plot_folder, f"{commodity}_power_bar_plot.pdf"))
        plt.show()

    if is_energy == 'yes':
        fig, ax = plt.subplots(figsize=adjusted_format)
        bars = ax.barh(df_ener.index, df_ener["Energy or Quantity"], label="Energy",
                       color=color_palette, height=bar_width)
        for bar in bars:
            width = bar.get_width()
            if width > 0 and to_annotate == 'yes':
                ax.text(width * percentage, bar.get_y() + bar.get_height() / 2,
                        f'{width:.2f}', ha='left', va='center',
                        fontsize=7, color=text_color, weight=weight)

        ax.set_ylabel(ener_unit)
        ax.set_title(f"{commodity} - Energy", fontsize=14)
        ax.tick_params(axis='y', labelsize=8)
        ax.grid(axis='x')
        plt.tight_layout()
        plt.savefig(os.path.join(plot_folder, f"{commodity}_energy_bar_plot.pdf"))
        plt.show()

    if is_combined == 'yes':
        fig, axs = plt.subplots(1, 2, figsize=adjusted_format_combined, sharey=True)

        for i, (col, color) in enumerate(zip(df_power.columns, generate_gradient(color_palette, 3))):
            bars = axs[0].barh(df_power.index, df_power[col], label=col, color=color, height=bar_width)
            for bar in bars:
                width = bar.get_width()
                if width > 0 and to_annotate == 'yes':
                    axs[0].text(width * percentage, bar.get_y() + bar.get_height() / 2,
                                f'{width:.2f}', ha='center', va='center',
                                fontsize=7, color=text_color, weight=weight, rotation=rotation)

        axs[0].set_xlabel(cap_unit)
        axs[0].set_ylabel(commodity, fontsize=14)
        axs[0].tick_params(axis='y', labelsize=8)
        axs[0].legend()
        axs[0].grid(axis='x')

        bars = axs[1].barh(df_ener.index, df_ener["Energy or Quantity"],
                           color=color_palette, height=bar_width)
        for bar in bars:
            width = bar.get_width()
            if width > 0 and to_annotate == 'yes':
                axs[1].text(width * percentage, bar.get_y() + bar.get_height() / 2,
                            f'{width:.3f}', ha='center', va='center',
                            fontsize=7, color=text_color, weight=weight)

        axs[1].set_xlabel(ener_unit)
        axs[1].tick_params(axis='y', labelsize=8)
        axs[1].grid(axis='x')

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

def pow_energy_dict(variable, cluster, unit_power, unit_energy, dict, time_horizon = 8760, name_capacity = "new_capacity", name_capacity_0 = "pre_installed_capacity", 
                    name_capacity_max = "max_capacity",  all_print = 'yes'):
    
    capacity_quantity = {}
    energy_quantity = {}
    total_energy = {}
    min_capacity = {}
    max_capacity = {}
    mean_capacity = {}
    installed_capacity = {}
    load_factor = {}
    table = {}
    
    nodes = get_cluster_subnodes_names_from_variable(variable,cluster,dict)
    # print(f'The list of all subnodes of {cluster} cluser is {nodes}')
    capacities = get_cluster_subnodes_capacities_from_nodes(nodes, cluster, name_capacity, name_capacity_0, name_capacity_max, dict)
    
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
        
        
        table[node] = {f"Total energy {unit_energy}": round(total_energy[node]/1000, 2), f"Max capacity {unit_power}": round(max_capacity[node], 2), 
                   f"Min capacity {unit_power}": round(min_capacity[node], 2), f"Mean capacity {unit_power}": round(mean_capacity[node], 2), 
                   f"Installed capacity {unit_power}": round(installed_capacity[node], 2), f"Load factor": round(load_factor[node], 2)}

        if all_print == 'no':
            table[node] = {f"Mean capacity {unit_power}": round(mean_capacity[node], 1), f"Max capacity {unit_power}": round(max_capacity[node], 1),
                   f"Installed capacity {unit_power}": round(installed_capacity[node], 1),f"Total energy {unit_energy}": round(total_energy[node]/1000, 2)}

    
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
            f"Total energy {unit_energy}": round(total_energy[node] / 1000, decimal[1]),
            f"Max capacity {unit_power}": round(max_capacity[node], decimal[0]),
            f"Min capacity {unit_power}": round(min_capacity[node], decimal[0]),
            f"Mean capacity {unit_power}": round(mean_capacity[node], decimal[0]),
            f"Installed capacity {unit_power}": round(installed_capacity[node], decimal[0]),
            "Load factor": round(load_factor[node], 2)
        }

        if all_print == 'no':
            table[node] = {
                f"Mean capacity {unit_power}": round(mean_capacity[node], decimal[0]),
                f"Max capacity {unit_power}": round(max_capacity[node], decimal[0]),
                f"Installed capacity {unit_power}": round(installed_capacity[node], decimal[0]),
                f"Total energy {unit_energy}": round(total_energy[node] / 1000, decimal[1])
            }

    if total_return == 'yes':
        return nodes, energy_quantity, total_energy, capacity_quantity, max_capacity, mean_capacity, installed_capacity, load_factor, table
    else:
        return table
    
    
#%% N°50 : functions to plot a box plot and having the statistics of the box plot in a table

def box_plot(data, title, y_label, x_label=None, x_ticks=None, hue=None,
             box_color='grey', mean_color='red', median_color='orange',
             widths=0.4, to_plot='yes', to_annotate='no',
             what_to_annotate=None, to_print='no'):

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
        fig, ax = plt.subplots(figsize=(12, 6))
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

def load_duration_curves(data , xlabel, ylabel, title, 
                         unit_cap='GW', unit_energy='TWh', is_together='no', ener_quan='Energy'): 

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
        plt.figure(figsize=(10, 6))

        legend_labels = []  # Liste pour stocker les labels de légende
        handles = []  # Liste pour stocker les handles de légende

        for node, value_sorted, total_production in node_productions:
            peak_value = max(value_sorted) 
            legend_label = f'{node}: P$_{{rated}}$ = {peak_value:.1f} {unit_cap}, {ener_quan} = {total_production / 1000:.3f} {unit_energy}'
            legend_labels.append(legend_label)
            handle, = plt.plot(value_sorted, label=legend_label)  # Garder le handle pour chaque courbe
            handles.append(handle)  # Ajouter le handle à la liste

        plt.title(title)
        plt.xlabel('Time')
        plt.xticks(ticks=np.append(np.arange(0, 8761, 1000), 8760))
        plt.ylabel('Value')
        plt.xlim((0, 8761))
        plt.legend(handles=handles, fontsize=8.5)
        plt.grid()
        plt.show()
        
        
    else:
        time_steps = len(node_productions[0][1])   
        stacked_values = np.zeros(time_steps) 

        plt.figure(figsize=(10, 6))

        colors = plt.cm.tab10.colors 
        legend_labels = []  # Liste pour stocker les labels de légende
        handles = []  # Liste pour stocker les handles de légende

        for i, (node, value_sorted, total_production) in enumerate(node_productions):
            peak_value = max(value_sorted)   
            legend_labels.append(f'{node}: P$_{{rated}}$ = {peak_value:.1f} {unit_cap}, {ener_quan} = {total_production / 1000:.3f} {unit_energy}')
            handle = plt.fill_between(range(time_steps), stacked_values, stacked_values + value_sorted, 
                                      color=colors[i % len(colors)],
                                      label=f'{node}: P$_{{rated}}$ = {peak_value:.1f} {unit_cap}, {ener_quan} = {total_production / 1000:.3f} {unit_energy}')
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
        plt.show()
        
        
#%% TO HAVE ALL

def get_all_from_variable_and_parameter(dictionary, variable=None, parameter=None, to_print='no', cluster=None, global_parameter=None): 
    
    if cluster is None:
        cluster = get_all_cluster_names(dictionary) 

    var = {}
    cap = {} 
    par = {}
    glob_par = {}

    if variable is not None:
        for v in variable: 
            for clust in cluster: 
                if clust not in var:
                    var[clust] = {}
                    cap[clust] = {}
                    
                

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

                cap[clust][v] = {}

                for node in nodes: 
                    try:
                        
                        if "sub_elements" not in dictionary["solution"]["elements"].get(clust, {}): 
                            continue  
                        
                        cluster_cap_data = get_cluster_subnodes_capacities_from_nodes(nodes=[node], cluster=clust, dictionary=dictionary)
                        cap[clust][v].update(cluster_cap_data)
                        
                    except KeyError as e:
                        print(f"KeyError in cluster {clust} for node {node}: {e}")
                        continue  

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

    return {'variables': var, 'capacities': cap, 'parameters': par, 'global_parameters': glob_par}



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