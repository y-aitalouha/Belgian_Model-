
#%% Librairy for function in GBOML
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


#%% Function to load a JSON file and convert into a usefull dictionnary
class MakeMeReadable:
    def __init__(self, d):
        self.d = d
   
    def __dir__(self):
        return self.d.keys()
   
    def __getattr__(self, v):
        try:
            out = self.d[v]
            if isinstance(out, dict):
                return MakeMeReadable(out)
            return out
        except:
            return getattr(self.d, v)
       
    def __str__(self):
        return str(self.d)
   
    def __repr__(self):
        return repr(self.d)
    
    # Function to print the keys dictionary in a readable way
    def what_in_it(self):
        if isinstance(self.d, dict):
            keys = self.d.keys()
            if keys:
                print(f"Keys: {', '.join(keys)}")
            else:
                print("There are no keys, maybe it is a time series (list of values)")
        elif isinstance(self.d, list):
            print("This is a list of values")
        else:
            print("This object is neither a dictionary nor a list")
            

    # Function to check if an item is in the dictionary (key or value)
    def is_in_it(self, item):
        if isinstance(item, (str, int, float)):
            if item in self.d.keys() or item in self.d.values():
                print(f"Yes, {item} is in the current dictionary")
            else:
                print(f"No, {item} is not in the current dictionnary")
        else:
            print("Invalid input type. Please provide a string, number, or float.")
            
             
             
def transform_makemereadable_into_dict(obj):
    if isinstance(obj, MakeMeReadable):
        result = {}
        for key in obj.d:
            value = obj.d[key]
            result[key] = transform_makemereadable_into_dict(value)
        return result
    elif isinstance(obj, dict):
        return {k: transform_makemereadable_into_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [transform_makemereadable_into_dict(item) for item in obj]
    else:
        return obj            
            



#%% Function to load data and solve the model

def load_data_and_solve(VECTOR, TIME_HORIZON, result_path): # Has a several vectors in list format and time horizon in hours (default is 8760)
    
    vector_path = []
    
    for vector in VECTOR:
        
        gboml_model = GbomlGraph(TIME_HORIZON) # Create a new model
        nodes, edges, global_params = gboml_model.import_all_nodes_and_edges(f"Hubs/{vector}.txt") # Import nodes, edges and global parameters
        
        gboml_model.set_timehorizon(TIME_HORIZON) # Set the time horizon
        gboml_model.add_nodes_in_model(*nodes) # Add nodes in the model
        gboml_model.add_hyperedges_in_model(*edges) # Add hyperedges in the model
        gboml_model.add_global_parameters(global_params) # Add global parameters in the model
        gboml_model.build_model() # Build the model
        
        
        # results_dir = result_path
        # os.makedirs(results_dir, exist_ok=True) # Create the results directory
        vector_dir = os.path.join(result_path, vector) 
        os.makedirs(vector_dir, exist_ok=True) # Create the vector directory
        
        solution = gboml_model.solve_gurobi() # Solve the model using Gurobi 
        # solution = gboml_model.solve_cplex() # Solve the model using cplex 
        
        
        if not solution:
            print(f"⚠️ Resolution problem {vector}: no solution returned.")
            continue

        solution, objective, status, solver_info, constraints_information, variables_information = solution # Get the solution, the objective, the status, the solver information, the constraints information and the variables information
        
        if status in ["OPTIMAL", "optimal", 2]:  # Gurobi retourne 2 pour une solution optimale
            print(f"✅ {vector} hub solved optimally!")
            
            
        
        dico = gboml_model.turn_solution_to_dictionary(solver_info, status, solution, objective, constraints_information, variables_information) # Turn the solution into a dictionary
        
        print("Json done\n")
        
        if TIME_HORIZON >= 8760:
            if TIME_HORIZON % 8760 == 0:
                output_file_path = f"{vector}_{int(TIME_HORIZON/8760)}years.json"
        
            elif TIME_HORIZON % 8760 != 0:
                output_file_path = f"{vector}_{TIME_HORIZON}hours.json"
                
        if TIME_HORIZON < 8760:
            if TIME_HORIZON % 24 == 0:
                output_file_path = f"{vector}_{int(TIME_HORIZON/24)}days.json"
            
            else:
                output_file_path = f"{vector}_{TIME_HORIZON}hours.json"
                
                
        full_path = os.path.join(vector_dir, output_file_path) 
        vector_path.append(full_path)
        
        with open(full_path, "w") as json_file:
            json_obj = json.dumps(dico)
            json_file.write(json_obj)

    return vector_path


#%% Function to change a parameter in a node
def change_param_in_node(ls_nodes, name_node, params):
    # Iterate over every node
    for n in ls_nodes:
        # Get the right node
        if n.name == name_node:
            # Iterate over the parameters to be changed
            for name_param, value_param in params.items():
                # Iterate over every parameter and get the right one
                for param in n.get_parameters():
                    if param.name == name_param:
                        print(f"{name_node} , {name_param}, {value_param}")
                        # Change the value of the parameter
                        expr = Expression('literal', value_param)
                        param.expression = expr
                        param.type = "expression"
                        param.vector = None
                        
    return ls_nodes

#%% Function to scale up a unit 

def scale_up(prod_low, prod_high, cost_low, index):
    return cost_low * (prod_high / prod_low) ** index

#%% Function to get the result file with the name to display the results

def get_the_result_file_with_name(VECTOR, TIME_HORIZON, PATH, HHV):
    
    if TIME_HORIZON >= 8760:
                if TIME_HORIZON % 8760 == 0:
                    
                    if int(TIME_HORIZON/8760) == 1:
                        print(colored(f"[INFO] In a period of {int(TIME_HORIZON/8760)} year:\n", 'green'))  
                        
                    else:
                        print(colored(f"[INFO] In a period of {int(TIME_HORIZON/8760)} years:\n", 'green')) 
            
                elif TIME_HORIZON % 8760 != 0: 
                    print(colored(f"[INFO] In a period of {TIME_HORIZON} hours:\n", 'green'))
                
    if TIME_HORIZON < 8760:
                if TIME_HORIZON % 24 == 0:
                    print(colored(f"[INFO] In a period of {int(TIME_HORIZON/24)} days:\n", 'green'))
                
                else: 
                    print(colored(f"[INFO] In a period of {TIME_HORIZON} hours:\n", 'green'))
                                       
    for index, path in enumerate(PATH):

        with open(path, 'r') as file:
            RREH_json = json.load(file)
            RREH_dico = MakeMeReadable(RREH_json)
            total_cost = RREH_dico.solution.objective
            
            if VECTOR[index] == "Hydrogen" :
                total_production = sum(RREH_dico.solution.elements.LIQUEFIED_HYDROGEN_REGASIFICATION.variables.hydrogen.values)
                
            if VECTOR[index] == "Methanol" :
                total_production = sum(RREH_dico.solution.elements.LIQUEFIED_METHANOL_CARRIERS.variables.liquefied_methanol_out.values)
                
            if VECTOR[index] == "Methane" :
                total_production = sum(RREH_dico.solution.elements.LIQUEFIED_METHANE_REGASIFICATION.variables.methane.values)
                
            if VECTOR[index] == "Ammonia" :
                total_production = sum(RREH_dico.solution.elements.LIQUEFIED_NH3_REGASIFICATION.variables.ammonia.values)
                
            if VECTOR[index] == "DME from MEOH" or VECTOR[index] == "DME_new" or VECTOR[index] == "DME":
                total_production = sum(RREH_dico.solution.elements.LIQUEFIED_DME_CARRIERS.variables.liquefied_dme_out.values)
                
            if VECTOR[index] == "DME D1" or VECTOR[index] == "DME I1" or VECTOR[index] == "DME D1 scaled" or VECTOR[index] == "DME I1 scaled":
                total_production = sum(RREH_dico.solution.elements.LIQUEFIED_DME_CARRIERS.variables.liquefied_dme_out.values)    
                
            if VECTOR[index] == "Ethanol_corn" or VECTOR[index] == "Ethanol_cellulosique" or VECTOR[index] == "Ethanol_wheat":
                total_production = sum(RREH_dico.solution.elements.ETHANOL_PLANTS.variables.ethanol.values)
                
            cost_per_MWH = (total_cost)/(total_production*HHV[index]) # HHV
            print(f"{VECTOR[index]} model: {(round(cost_per_MWH, 2))} €/MWh (HHV)")
            
       