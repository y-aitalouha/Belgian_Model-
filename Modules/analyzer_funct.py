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
import seaborn  
import matplotlib.colors as mcolors
import matplotlib
from IPython.display import display
from builtins import sum as sum
import os
import sys
import GBOML_function as gf
import process_funct as pf

from process_funct import merge_dictionaries as merge
from process_funct import convert_mmr_to_dict as convert
from process_funct import transform_dict_into_table_several_column as table
from process_funct import all_cost_prod_dict_per_cluster as node_stat

#%% COST CHECK FUNCTION:

def system_cost_check(model, result_folder, to_display= 'yes', approx=None, max_constraint= 'yes'):
    
    system_cost_dict, system_node_dict = pf.system_cost(model, approx=approx, max_constraint = max_constraint) 
    
    inland_node_cost = pf.transform_dict_into_table_several_column(system_node_dict['INLAND'], show='no', zero_print='no')
    offshore_node_cost = pf.transform_dict_into_table_several_column(system_node_dict['OFFSHORE'], show='no', zero_print='no')
    zeebrugge_node_cost = pf.transform_dict_into_table_several_column(system_node_dict['ZEEBRUGGE'], show='no', zero_print='no')
    system_cost_table = pf.transform_dict_into_table_several_column(system_cost_dict, show='no', zero_print='no')
    
    if to_display == 'yes':
        print(colored('Inland node cost:', 'blue', attrs=['bold']))
        display(inland_node_cost)
        
        print(colored('Offshore node cost:', 'blue', attrs=['bold']))
        display(offshore_node_cost)
        
        print(colored('Zeebrugge node cost:', 'blue', attrs=['bold']))
        display(zeebrugge_node_cost) 
        
        print(colored('System cost table:', 'blue', attrs=['bold']))
        display(system_cost_table)
    
    inland_cost_excel = pf.save_table_into_excel(inland_node_cost, table_name=f'inland_cost.xlsx', folder=result_folder)
    offshore_cost_excel = pf.save_table_into_excel(offshore_node_cost, table_name=f'offshore_cost.xlsx', folder=result_folder)
    zeebrugge_cost_excel = pf.save_table_into_excel(zeebrugge_node_cost, table_name=f'zeebrugge_cost.xlsx', folder=result_folder)
    system_cost_excel = pf.save_table_into_excel(system_cost_table, table_name=f'system_cost.xlsx', folder=result_folder)

    if to_display == 'yes':
        total_cost = model['solution']["objective"]
        print(f'The total system objective cost is: {round(total_cost,1)} M€')
        print('')

        cost = 0
        imp_countries = ['FRANCE', 'NETHERLANDS', 'DEUTSCHLAND', 'LUXEMBOURG','UNITED_KINGDOM','DENMARK'] 
        imp = 0 
        
        for key in system_cost_dict.keys():
            print(f'{key} cost is: {round(system_cost_dict[key]["Total cluster cost [M€]"],1)} M€')
            cost += system_cost_dict[key]['Total cluster cost [M€]'] 
            if key in imp_countries:
                imp += system_cost_dict[key]['Total cluster cost [M€]']
        
        print(f'\nThe total cost is: {round(cost,1)} M€')
        print(f'The total import cost is: {round(imp,1)} M€')
    
    return inland_node_cost, offshore_node_cost, zeebrugge_node_cost, system_cost_table


#%% STATE OF CHARGE FUNCTION:

def storage_analysis(soc, soc_cap, dischar, dischar_cap, char, char_cap):

    # SOC
    print(colored('State of charge of batteries in INLAND:', 'blue'))
    soc_sum = sum(soc)
    print('Total energy stored in batteries:', round(soc_sum,3), 'GWh')
    print('Battery energy capacity:', round(soc_cap,3), 'GWh')
    print('')

    # Discharge 
    print(colored('Discharge of batteries in INLAND:', 'blue'))
    dischar_sum = sum(dischar)
    print('Total energy discharged from batteries:', round(dischar_sum,3), 'GWh')
    print('Battery discharge power capacity:', round(dischar_cap,3), 'GW')
    print('')

    # Charge
    print(colored('Charge of batteries in INLAND:', 'blue'))
    char_sum = sum(char)
    print('Total energy charged to batteries:', round(char_sum,3), 'GWh')
    print('Battery charge power capacity:', round(char_cap,3), 'GW')
    print('')

    # Energy yield
    energy_yield = (dischar_sum / char_sum) * 100
    print(colored('Energy yield of batteries in INLAND:', 'blue'))
    print('Energy yield:', round(energy_yield, 2), '%')
    print('')

    # Charge factor
    print(colored('Charge factor of batteries in INLAND:', 'blue'))
    char_mean = mean(char)
    print('Mean charge:', round(char_mean, 3), 'GWh')
    char_max = max(char)
    print('Max charge:', round(char_max, 3), 'GWh')
    char_factor = (char_mean / char_max) * 100
    print('Charge factor:', round(char_factor, 2), '%')
    print('')

    # Discharge factor
    print(colored('Discharge factor of batteries in INLAND:', 'blue'))
    dischar_mean = mean(dischar)
    print('Mean discharge:', round(dischar_mean, 3), 'GWh')
    dischar_max = max(dischar)
    print('Max discharge:', round(dischar_max, 3), 'GWh')
    dischar_factor = (dischar_mean / dischar_max) * 100
    print('Discharge factor:', round(dischar_factor, 2), '%')
    print('')

    # Use factor of the batteries
    print(colored('Use factor of batteries in INLAND:', 'blue'))
    soc_use = mean(soc)/ soc_cap * 100
    print('Mean state of charge:', round(soc_use, 3), '%')
    print('')

    # Number of hours where batteries are active
    print(colored('Number of hours where batteries are active in INLAND:', 'blue'))
    batt_charge_hours = sum(1 for value in char if value > 0)
    print('Number of hours where batteries charged:', batt_charge_hours)
    batt_discharge_hours = sum(1 for value in dischar if value > 0)
    print('Number of hours where batteries discharged:', batt_discharge_hours)
    print('Total number of hours where batteries are active:', batt_charge_hours + batt_discharge_hours)
    print('')

    # Number of cycles of the batteries
    print(colored('Number of cycles of the batteries in INLAND:', 'blue'))
    n_cycle_min = min(char_sum, dischar_sum)/soc_cap
    print('Number of cycles of the batteries (minimum):', int(n_cycle_min))
    n_cycle_avg = (char_sum + dischar_sum)/(2 * soc_cap)
    print('Number of cycles of the batteries (average):', int(n_cycle_avg))
    print('')

    # Depth of discharge
    print(colored('Depth of discharge of the batteries in INLAND:', 'blue'))
    dod = (max(soc) - min(soc)) / soc_cap * 100
    print('Depth of discharge:', round(dod, 2), '%')
    print('')

    # Sollicitation
    print(colored('Sollicitation of the batteries in INLAND:', 'blue'))
    char_pow_sollicitation = (max(char) / char_cap) * 100
    print('Charge power sollicitation:', round(char_pow_sollicitation, 2), '%')
    dischar_pow_sollicitation = (max(dischar) / dischar_cap) * 100
    print('Discharge power sollicitation:', round(dischar_pow_sollicitation, 2), '%')
    energy_sollicitation = ((max(soc)-min(soc)) / soc_cap) * 100
    print('Energy sollicitation:', round(energy_sollicitation, 2), '%')
    print('')
    

def state_of_charge(model_dict, cluster, node, capacity = 'new_energy_capacity',
                    zoom='week', variable='state_of_charge', figsave = None):

    storage = model_dict['solution']['elements'][cluster]["sub_elements"][node]['variables']
    soc_over_time = pf.zoom_with_timestep(storage[variable]['values'], zoom=zoom)  

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Get max capacity value - if it's a list, get the first value or the maximum value
    if isinstance(storage[capacity]['values'], list):
        max_capacity = storage[capacity]['values'][0]  # or use max(batt['new_energy_capacity']['values'])
    else:
        max_capacity = storage[capacity]['values']

    # Plot state of charge on primary axis
    ax1.plot(soc_over_time, label='State of Charge (zoomed)', color='blue')
    ax1.axhline(max_capacity, label=f'Max Energy Capacity ({max_capacity:.1f})', color='red', linestyle='--')
    ax1.set_ylabel('State of Charge [GWh]')
    ax1.set_xlabel(f'Time [{zoom}]')

    # Create secondary y-axis for percentage
    secax = ax1.secondary_yaxis(
        'right',
        functions=(lambda x: x/max_capacity*100, lambda x: x*max_capacity/100)
    )
    secax.set_ylabel('State of Charge [%]')
    secax.set_yticks(np.arange(0, 101, 10))  # Set y-ticks for percentage

    # Add legend
    ax1.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=2)
    plt.tight_layout()

    # Save figure if a path is provided
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")

    plt.show()



#%% ENERGY NOT SERVED FUNCTION:

def ens_func(model_dict):
    """
    Function to calculate energy not served for each scenario.
    
    Parameters:
    model (list): List of model dictionaries for different scenarios.
    
    Returns:
    None
    """ 
    ens_dict = {} 

    objective = model_dict['solution']["elements"]['INLAND']["objectives"]["named"] 
    
    e_ens = model_dict['solution']["elements"]['INLAND']['variables']['e_ens']['values']
    h2_ens = model_dict['solution']["elements"]['INLAND']['variables']['h2_ens']['values']
    ng_ens = model_dict['solution']["elements"]['INLAND']['variables']['ng_ens']['values']
    try:
        methanol_ens = model_dict['solution']["elements"]['INLAND']['variables']['methanol_ens']['values']
    except: 
        pass
    
    # # Wrap scalar values in lists to avoid ValueError
    objective_wrapped = {k: [round(v, 2)] for k, v in objective.items()}
    objective_table = pf.transform_dict_into_table_several_column(objective_wrapped, show='no')
    objective_table.index = ['Energy not served cost (M€):']
    display(objective_table)
    
    # Calculate energy not served statistics for this scenario
    total_e_ens = sum(e_ens)
    max_e_ens = max(e_ens)
    cost_e_ens = objective['cost_e_ens']
    
    total_h2_ens = sum(h2_ens)
    max_h2_ens = max(h2_ens)
    cost_h2_ens = objective['cost_h2_ens']
    
    total_ng_ens = sum(ng_ens)
    max_ng_ens = max(ng_ens)
    cost_ng_ens = objective['cost_ng_ens']
    
    try:
        total_methanol_ens = sum(methanol_ens)
        max_methanol_ens = max(methanol_ens)
        cost_methanol_ens = objective['cost_methanol_ens']
    except KeyError:
        total_methanol_ens = 0
        max_methanol_ens = 0
        cost_methanol_ens = 0
    
    # Find hours with energy not served
    e_ens_hours = [i for i, val in enumerate(e_ens) if val > 0]
    h2_ens_hours = [i for i, val in enumerate(h2_ens) if val > 0]
    ng_ens_hours = [i for i, val in enumerate(ng_ens) if val > 0]
    try: 
        methanol_ens_hours = [i for i, val in enumerate(methanol_ens) if val > 0]
    except:
        pass

    # Print summary of hours with energy not served
    print(f"Hours with electricity not served: {len(e_ens_hours)}")
    # if e_ens_hours:
    #     display(e_ens_hours)

    print(f"Hours with hydrogen not served: {len(h2_ens_hours)}")
    # if h2_ens_hours:
    #     display(h2_ens_hours)

    print(f"Hours with natural gas not served: {len(ng_ens_hours)}")
    # if ng_ens_hours:
    #     display(ng_ens_hours)
    
    
    try:
        print(f"Hours with methanol not served: {len(methanol_ens_hours)}")
    except:
        pass
    
    
    # Store energy not served statistics
    try:
        ens_dict[f'Energy not served statistics'] = {
            'Electricity not served (GWh/y)': round(total_e_ens, 2),
            'Hydrogen not served (GWh/y)': round(total_h2_ens, 2),
            'Natural gas not served (GWh/y)': round(total_ng_ens, 2),
            'Methanol not served (GWh/y)': round(total_methanol_ens, 2),
            
            'Cost of electricity not served (M€)': round(cost_e_ens, 2),
            'Cost of hydrogen not served (M€)': round(cost_h2_ens, 2),
            'Cost of natural gas not served (M€)': round(cost_ng_ens, 2),
            'Cost of methanol not served (M€)': round(cost_methanol_ens, 2),
            
            'Max electricity not served (GWh)': round(max_e_ens, 2),
            'Max hydrogen not served (GWh)': round(max_h2_ens, 2),
            'Max natural gas not served (GWh)': round(max_ng_ens, 2), 
            'Max methanol not served (GWh)': round(max_methanol_ens, 2),
            
            }
        
    except:
        ens_dict[f'Energy not served statistics'] = {
            'Electricity not served (GWh/y)': round(total_e_ens, 2),
            'Hydrogen not served (GWh/y)': round(total_h2_ens, 2),
            'Natural gas not served (GWh/y)': round(total_ng_ens, 2),
            
            'Cost of electricity not served (M€)': round(cost_e_ens, 2),
            'Cost of hydrogen not served (M€)': round(cost_h2_ens, 2),
            'Cost of natural gas not served (M€)': round(cost_ng_ens, 2),
            
            'Max electricity not served (GWh)': round(max_e_ens, 2),
            'Max hydrogen not served (GWh)': round(max_h2_ens, 2),
            'Max natural gas not served (GWh)': round(max_ng_ens, 2), 
            }

    plt.figure(figsize=(10, 2))
    plt.plot(h2_ens, color = 'blue')
    plt.plot(ng_ens, color = 'gray')
    plt.plot(e_ens, color = 'orange')
    try:
        plt.plot(methanol_ens, color = 'green')
    except:
        pass
    plt.xlabel('Time [hour]')
    plt.ylabel('Energy not served [GWh]', fontsize = 9) 
    plt.title(f'Energy not served over time')
    try: 
        plt.legend(['Hydrogen', 'Natural gas','Electricity', 'Methanol'])
    except:
        plt.legend(['Hydrogen', 'Natural gas','Electricity'])
    plt.grid(True)
    plt.show()

    ens_table = pf.transform_dict_into_table_several_column(ens_dict, show='no')
    return ens_table


def ens_func_no_efuel(model_dict):
    """
    Function to calculate energy not served for each scenario.
    
    Parameters:
    model (list): List of model dictionaries for different scenarios.
    
    Returns:
    None
    """ 
    ens_dict = {} 

    objective = model_dict['solution']["elements"]['INLAND']["objectives"]["named"] 
    
    e_ens = model_dict['solution']["elements"]['INLAND']['variables']['e_ens']['values']
    h2_ens = model_dict['solution']["elements"]['INLAND']['variables']['h2_ens']['values']
    ng_ens = model_dict['solution']["elements"]['INLAND']['variables']['ng_ens']['values'] 
    
    # # Wrap scalar values in lists to avoid ValueError
    objective_wrapped = {k: [round(v, 2)] for k, v in objective.items()}
    objective_table = pf.transform_dict_into_table_several_column(objective_wrapped, show='no')
    objective_table.index = ['Energy not served cost (M€):']
    display(objective_table)
    
    # Calculate energy not served statistics for this scenario
    total_e_ens = sum(e_ens)
    max_e_ens = max(e_ens)
    cost_e_ens = objective['cost_e_ens']
    
    total_h2_ens = sum(h2_ens)
    max_h2_ens = max(h2_ens)
    cost_h2_ens = objective['cost_h2_ens']
    
    total_ng_ens = sum(ng_ens)
    max_ng_ens = max(ng_ens)
    cost_ng_ens = objective['cost_ng_ens']
    
    
    
    # Find hours with energy not served
    e_ens_hours = [i for i, val in enumerate(e_ens) if val > 0]
    h2_ens_hours = [i for i, val in enumerate(h2_ens) if val > 0]
    ng_ens_hours = [i for i, val in enumerate(ng_ens) if val > 0]

    # Print summary of hours with energy not served
    print(f"Hours with electricity not served: {len(e_ens_hours)}")
    # if e_ens_hours:
    #     display(e_ens_hours)

    print(f"Hours with hydrogen not served: {len(h2_ens_hours)}")
    # if h2_ens_hours:
    #     display(h2_ens_hours)

    print(f"Hours with natural gas not served: {len(ng_ens_hours)}")
    # if ng_ens_hours:
    #     display(ng_ens_hours)
    

    
    # Store energy not served statistics

    ens_dict[f'Energy not served statistics'] = {
            'Electricity not served (GWh/y)': round(total_e_ens, 2),
            'Hydrogen not served (GWh/y)': round(total_h2_ens, 2),
            'Natural gas not served (GWh/y)': round(total_ng_ens, 2),
            
            'Cost of electricity not served (M€)': round(cost_e_ens, 2),
            'Cost of hydrogen not served (M€)': round(cost_h2_ens, 2),
            'Cost of natural gas not served (M€)': round(cost_ng_ens, 2),
            
            'Max electricity not served (GWh)': round(max_e_ens, 2),
            'Max hydrogen not served (GWh)': round(max_h2_ens, 2),
            'Max natural gas not served (GWh)': round(max_ng_ens, 2), 
            }

    plt.figure(figsize=(10, 2))
    plt.plot(h2_ens, color = 'blue')
    plt.plot(ng_ens, color = 'gray')
    plt.plot(e_ens, color = 'orange')
    plt.xlabel('Time [hour]')
    plt.ylabel('Energy not served [GWh]', fontsize = 9) 
    plt.title(f'Energy not served over time')
    plt.legend(['Hydrogen', 'Natural gas','Electricity'])
    plt.grid(True)
    plt.show()

    ens_table = pf.transform_dict_into_table_several_column(ens_dict, show='no')
    return ens_table

#%% ELECTRICITY NOT SERVED FUNCTION:

def balance_electricity(model_e, model_dict, start=0, end=8760, steps=1, figsize= (12, 5)):
    
    print(f"Electricity balanced (INLAND)")
    
    # Define the data categories and variables to extract
    data_categories = {
        'e_produced': ['PV', 'WIND_ONSHORE', 'NUCLEAR', 'BIOMASS', 'WASTE', 'CHP', 'CCGT', 'OCGT', 'FUEL_CELLS'],
        'e_consumed': ['ELECTROLYSIS_PLANTS', 'BIOMETHANE', 'SMR', 'PCCC_SMR', 'PCCC_BM', 'PCCC_WS', 'PCCC_CCGT', 'PCCC_OCGT', 'PCCC_CHP', 'DAC', 'H2_STORAGE'],
        'e_discharged': ['PUMPED_HYDRO', 'BATTERIES'],
        'e_charged': ['PUMPED_HYDRO', 'BATTERIES'],
        'load_increase': ['LOAD_SHIFTING'],
        'load_reduction': ['LOAD_SHIFTING', 'LOAD_SHEDDING_1', 'LOAD_SHEDDING_2', 'LOAD_SHEDDING_4', 'LOAD_SHEDDING_8', 'LOAD_SHEDDING_UNLIM']
    }
    
    # Initialize dictionary to store formatted data
    zoom_data = {}
    
    # Extract and format all data
    for category, variables in data_categories.items():
        for var in variables:
            key = f"{category}_{var}"
            data = model_e['variables']['INLAND'][category][var]
            zoom_data[key], xticks = pf.get_new_format(data=data, start_index=start, end_index=end, step=steps, xticks='yes')
    
    # Prepare data for plotting
    e_prod = [
        np.array(zoom_data['e_produced_PV']), np.array(zoom_data['e_produced_WIND_ONSHORE']), np.array(zoom_data['e_produced_NUCLEAR']),
        np.array(zoom_data['e_produced_BIOMASS']), np.array(zoom_data['e_produced_WASTE']), np.array(zoom_data['e_produced_CHP']),
        np.array(zoom_data['e_produced_CCGT']), np.array(zoom_data['e_produced_OCGT']), -np.array(zoom_data['e_consumed_ELECTROLYSIS_PLANTS']),
        np.array(zoom_data['e_produced_FUEL_CELLS']), -np.array(zoom_data['e_consumed_BIOMETHANE']), -np.array(zoom_data['e_consumed_SMR']),
        np.array(zoom_data['e_discharged_PUMPED_HYDRO']), -np.array(zoom_data['e_charged_PUMPED_HYDRO']), np.array(zoom_data['e_discharged_BATTERIES']),
        -np.array(zoom_data['e_charged_BATTERIES']), -np.array(zoom_data['e_consumed_PCCC_SMR']) - np.array(zoom_data['e_consumed_PCCC_BM']),
        -np.array(zoom_data['e_consumed_PCCC_WS']), -np.array(zoom_data['e_consumed_PCCC_CCGT']) - np.array(zoom_data['e_consumed_PCCC_OCGT']), 
        -np.array(zoom_data['e_consumed_PCCC_CHP']), -np.array(zoom_data['e_consumed_DAC']), 
        np.array(zoom_data['load_reduction_LOAD_SHIFTING']) - np.array(zoom_data['load_increase_LOAD_SHIFTING']),
        np.array(zoom_data['load_reduction_LOAD_SHEDDING_1']) + np.array(zoom_data['load_reduction_LOAD_SHEDDING_2']) + np.array(zoom_data['load_reduction_LOAD_SHEDDING_4'])
        + np.array(zoom_data['load_reduction_LOAD_SHEDDING_8']) + np.array(zoom_data['load_reduction_LOAD_SHEDDING_UNLIM']),-np.array(zoom_data['e_consumed_H2_STORAGE'])
    ]

    e_prod_label = ['PV', 'Wind Onshore', 'Nuclear', 'Biomass', 'Waste', 'CHP', 'CCGT', 'OCGT', 'Electrolysis', 'Fuel Cells', 'Biomethane', 'SMR', 'Discharged Pumped Hydro', 
                    'Charged Pumped Hydro ', 'Discharged Batteries', 'Charged Batteries', 'All PCCCs', 'DAC', 'Load Shifting', 'Load Shedding', 'hydro storage']

    woff_zoom = pf.get_new_format(data=model_e['variables']['OFFSHORE']['e_produced']['WIND_OFFSHORE'], start_index=start, end_index=end, step=steps, xticks='yes')[0]

    data_bal = np.sum(e_prod, axis=0)

    # Get real balance data
    e_real_bal = model_e['variables']["INLAND"]["e_balanced"]["BALANCE"]
    data_real_bal, _ = pf.get_new_format(data=e_real_bal, start_index=start, end_index=end, step=steps, xticks='yes')


    #----------------------------------------------------------------------------------------------------------------------------------------
    

    # Plot electricity production and consumption in INLAND
    plt.figure(figsize=figsize)
    
    for data_inl, label in zip(e_prod, e_prod_label):
        if data_inl is not None and len(data_inl) > 0 and np.any(data_inl):
            plt.plot(xticks, data_inl, label=label)  
        
    plt.plot(xticks, woff_zoom, label='Wind offshore')
    plt.plot(xticks, data_bal, label='Total Balance', color='black', linestyle='--') 
    plt.plot(xticks, np.array(zoom_data['load_reduction_LOAD_SHIFTING']) - np.array(zoom_data['load_increase_LOAD_SHIFTING']), label='Load Shifting' ) 
    plt.plot(xticks, np.array(zoom_data['load_reduction_LOAD_SHEDDING_1']) + np.array(zoom_data['load_reduction_LOAD_SHEDDING_2']) + 
            np.array(zoom_data['load_reduction_LOAD_SHEDDING_4']) + np.array(zoom_data['load_reduction_LOAD_SHEDDING_8']) + 
            np.array(zoom_data['load_reduction_LOAD_SHEDDING_UNLIM']), label='Load Shedding' )

    
            
    plt.title(f'Electricity production and consumption in the Inland cluster ', fontsize=14)
    plt.xlabel('Time [hours]')
    plt.ylabel('Electricity [GWh]')
    plt.xticks(xticks, rotation=90, fontsize = 8)
    plt.tight_layout()
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=5, frameon=False)
    plt.show()
    
    
    
    # Plot electricity DRS in INLAND
    plt.figure(figsize=figsize) 
    plt.plot(xticks, np.array(zoom_data['load_reduction_LOAD_SHIFTING']), label='Load Shifting reduction')
    plt.plot(xticks, -np.array(zoom_data['load_increase_LOAD_SHIFTING']), label='Load Shifting increase')  
    plt.plot(xticks, np.array(zoom_data['load_reduction_LOAD_SHEDDING_1']), label='Load Shedding 1h') if np.any(np.array(zoom_data['load_reduction_LOAD_SHEDDING_1'])) else None
    plt.plot(xticks, np.array(zoom_data['load_reduction_LOAD_SHEDDING_2']), label='Load Shedding 2h') if np.any(np.array(zoom_data['load_reduction_LOAD_SHEDDING_2'])) else None
    plt.plot(xticks, np.array(zoom_data['load_reduction_LOAD_SHEDDING_4']), label='Load Shedding 4h') if np.any(np.array(zoom_data['load_reduction_LOAD_SHEDDING_4'])) else None
    plt.plot(xticks, np.array(zoom_data['load_reduction_LOAD_SHEDDING_8']), label='Load Shedding 8h') if np.any(np.array(zoom_data['load_reduction_LOAD_SHEDDING_8'])) else None
    plt.plot(xticks, np.array(zoom_data['load_reduction_LOAD_SHEDDING_UNLIM']), label='Load Shedding 24h') if np.any(np.array(zoom_data['load_reduction_LOAD_SHEDDING_UNLIM'])) else None
    plt.plot(xticks, np.array(zoom_data['load_reduction_LOAD_SHEDDING_1']) + np.array(zoom_data['load_reduction_LOAD_SHEDDING_2']) + 
            np.array(zoom_data['load_reduction_LOAD_SHEDDING_4']) + np.array(zoom_data['load_reduction_LOAD_SHEDDING_8']) + 
            np.array(zoom_data['load_reduction_LOAD_SHEDDING_UNLIM']), label='Load Shedding total', color='black', linestyle='--')        
            
    plt.title(f'Electricity DRS in the Inland cluster ', fontsize=14)
    plt.xlabel('Time [hours]')
    plt.ylabel('Electricity [GWh]')
    plt.xticks(xticks, rotation=90, fontsize = 8)
    plt.tight_layout()
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=5, frameon=False)
    plt.show()

    # Get and format data for second part of the function
    grid_data = { 
        'bal': model_e["variables"]["INLAND"]["e_balanced"]["BALANCE"],
        'neth': model_e['variables']['NETHERLANDS']['e_imported'],
        'deut': model_e['variables']['DEUTSCHLAND']['e_imported'],
        'lux': model_e['variables']['LUXEMBOURG']['e_imported'],
        'fr': model_e['variables']['FRANCE']['e_imported'],
        'den': model_e['variables']['DENMARK']['e_imported'],
        'uk': model_e['variables']['UNITED_KINGDOM']['e_imported'],
        'inst_pow': model_e['variables']['INLAND']['inst_power']['BALANCE'],
        'zb_inl': model_e['variables']['HV_ZB_INL']['e_forward_out'],
        'inl_zb': model_e['variables']['HV_ZB_INL']['e_reverse_in'], 
        'wind_offshore': model_e['variables']['OFFSHORE']['e_produced']['WIND_OFFSHORE'],
    } 
    
    
    formatted_grid_data = {}
    for key, data in grid_data.items():
        formatted_grid_data[key], xticks = pf.get_new_format(data=data, start_index=start, end_index=end, step=steps, xticks='yes')
    
    # Get demand data
    e_ens = pf.get_cluster_variable('INLAND', 'e_ens', model_dict)
    data_ens, xticks = pf.get_new_format(data=e_ens['values'], start_index=start, end_index=end, step=steps, xticks='yes')
    
    demand_data = {
        'demand_el': model_e['global_parameters']['demand_el']['demand_el'],
        'demand_el_ht': model_e['global_parameters']['demand_el_ht']['demand_el_ht']
    }
    
    formatted_demand_data = {}
    for key, data in demand_data.items():
        formatted_demand_data[key], xticks = pf.get_new_format(data=data, start_index=start, end_index=end, step=steps, xticks='yes')
    
    e_demand_el_tr = pf.get_cluster_variable('INLAND', 'demand_el_tr', model_dict)
    data_demand_el_tr, xticks = pf.get_new_format(data=e_demand_el_tr['values'], start_index=start, end_index=end, step=steps, xticks='yes')

    # Calculate sums
    data_sum = np.sum([formatted_grid_data['bal'], formatted_grid_data['neth'], formatted_grid_data['deut'], formatted_grid_data['lux'], formatted_grid_data['fr'],
                        formatted_grid_data['zb_inl'], formatted_grid_data['inl_zb'], ], axis=0)
    
    data_max_grid_sum = np.sum([formatted_grid_data['inst_pow'], formatted_grid_data['neth'], formatted_grid_data['deut'], formatted_grid_data['lux'],
                                formatted_grid_data['fr'], formatted_grid_data['zb_inl']], axis=0)
    
    data_demand_sum = np.sum([formatted_demand_data['demand_el'], formatted_demand_data['demand_el_ht'], data_demand_el_tr], axis=0)

    max_grid = model_e["global_parameters"]["grid_limit"]
    max_grid = max_grid['grid_limit'] if isinstance(max_grid, dict) else max_grid
    
    
    #----------------------------------------------------------------------------------------------------------------------------------------
    
    
    
    # Plot Electricity demand in BELGIUM
    plt.figure(figsize=figsize) 
    plt.plot(xticks, formatted_demand_data['demand_el'], label='Electricity demand', color='blue')
    plt.plot(xticks, formatted_demand_data['demand_el_ht'], label='Heating electricity demand', color='orange')
    plt.plot(xticks, data_demand_el_tr, label='Transport electricity demand', color='green') 
    plt.plot(xticks, data_demand_sum, label='Total electricity demand', color='black', linestyle='--')
    plt.title(f'Electricity demands in the Inland cluster', fontsize = 14)
    plt.xlabel('Time')
    plt.ylabel('Electricity [GWh]')
    plt.xticks(xticks, rotation=90, fontsize = 8)
    # plt.yticks(np.arange(0, 26, 1))
    plt.tight_layout()
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
    plt.show() 
    
    # Plot Electricity production and import in BELGIUM
    plt.figure(figsize=figsize) 
    plt.plot(xticks, formatted_grid_data['bal'], label='INLAND balanced', color='blue')
    plt.plot(xticks, formatted_grid_data['neth'], label='NETHERLANDS import', color='pink')
    plt.plot(xticks, formatted_grid_data['deut'], label='DEUTSCHLAND import', color='green')
    plt.plot(xticks, formatted_grid_data['lux'], label='LUXEMBOURG import', color='cyan')
    plt.plot(xticks, formatted_grid_data['fr'], label='FRANCE import', color='red')
    plt.plot(xticks, formatted_grid_data['den'], label='DENMARK import', color='purple')
    plt.plot(xticks, formatted_grid_data['uk'], label='UNITED KINGDOM import', color='brown')
    # plt.plot(xticks, formatted_grid_data['zb_inl'], label='ZEEBRUGGE import', color='purple')
    # plt.plot(xticks, formatted_grid_data['inl_zb'], label='ZEEBRUGGE export', color='brown')
    plt.plot(xticks, formatted_grid_data['wind_offshore'], label='Offshore wind', color='orange')
    plt.plot(xticks, data_sum, label='Total electricity', color='black', linestyle='--')
    plt.title(f'Electricity production and imports over time in the Inland cluster', fontsize = 14)
    plt.xlabel('Time [hours]')
    plt.ylabel('Electricity [GWh]')
    plt.xticks(xticks, rotation=90, fontsize = 8)
    # plt.yticks(np.arange(0, 26, 1))
    plt.tight_layout()
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
    plt.show()
    
    
    # Plot Electricity not served in BELGIUM
    fig, ax1 = plt.subplots(figsize=figsize)
    ax1.plot(xticks, data_sum, label='Total electricity production', color='blue')
    ax1.plot(xticks, data_demand_sum, label='Total electricity demand', color='red')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Electricity [GWh]')
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(xticks, rotation=90)
    # ax1.set_yticks(np.arange(15, 30, 1))

    ax2 = ax1.twinx()
    ax2.bar(xticks, data_ens, width=0.8, alpha=0.3, color='gray', label='Energy not served', bottom=0)
    ax2.set_ylabel('Energy not served [GWh]')

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
    plt.xticks(xticks, rotation=90, fontsize = 8)
    plt.title(f'Electricity demand (INLAND)')
    plt.tight_layout()
    plt.show()
    

#%% GRID CHECK FUNCTION:

def balance_electricity_max_grid(model_e, model_dict, start=0, end=8760, steps=1, figsize= (12, 5), special_tick = 'no'):
    
    print(f"Electricity Grid check (INLAND):")

    # Get and format data for second part of the function
    grid_data = { 
        'bal': model_e["variables"]["INLAND"]["e_balanced"]["BALANCE"],
        'neth': model_e['variables']['NETHERLANDS']['e_imported'],
        'deut': model_e['variables']['DEUTSCHLAND']['e_imported'],
        'lux': model_e['variables']['LUXEMBOURG']['e_imported'],
        'fr': model_e['variables']['FRANCE']['e_imported'],
        'inst_pow': model_e['variables']['INLAND']['inst_power']['BALANCE'],
        'zb_inl': model_e['variables']['HV_ZB_INL']['e_forward_out'],
        'inl_zb': model_e['variables']['HV_ZB_INL']['e_reverse_in']
    } 
    
    
    formatted_grid_data = {}
    for key, data in grid_data.items():
        formatted_grid_data[key], xticks = pf.get_new_format(data=data, start_index=start, end_index=end, step=steps, xticks='yes')
    
    # Get demand data
    e_ens = pf.get_cluster_variable('INLAND', 'e_ens', model_dict)
    data_ens, xticks = pf.get_new_format(data=e_ens['values'], start_index=start, end_index=end, step=steps, xticks='yes')
    
    demand_data = {
        'demand_el': model_e['global_parameters']['demand_el']['demand_el'],
        'demand_el_ht': model_e['global_parameters']['demand_el_ht']['demand_el_ht']
    }
    
    formatted_demand_data = {}
    for key, data in demand_data.items():
        formatted_demand_data[key], xticks = pf.get_new_format(data=data, start_index=start, end_index=end, step=steps, xticks='yes')
    
    e_demand_el_tr = pf.get_cluster_variable('INLAND', 'demand_el_tr', model_dict)
    data_demand_el_tr, xticks = pf.get_new_format(data=e_demand_el_tr['values'], start_index=start, end_index=end, step=steps, xticks='yes')

    # Calculate sums
    data_sum = np.sum([formatted_grid_data['bal'], formatted_grid_data['neth'], formatted_grid_data['deut'], formatted_grid_data['lux'], formatted_grid_data['fr'],
                        formatted_grid_data['zb_inl'], formatted_grid_data['inl_zb']], axis=0)
    
    data_sum_max = np.sum([grid_data['bal'], grid_data['neth'], grid_data['deut'], grid_data['lux'], grid_data['fr'], grid_data['zb_inl'], grid_data['inl_zb']], axis=0)
    
    count_max = int(np.count_nonzero(data_sum_max == data_sum_max.max()))
    
    data_max_grid_sum = np.sum([formatted_grid_data['inst_pow'], formatted_grid_data['neth'], formatted_grid_data['deut'], formatted_grid_data['lux'],
                                formatted_grid_data['fr'], formatted_grid_data['zb_inl']], axis=0)
    
    data_demand_sum = np.sum([formatted_demand_data['demand_el'], formatted_demand_data['demand_el_ht'], data_demand_el_tr], axis=0)

    max_grid = model_e["global_parameters"]["grid_limit"]
    max_grid = max_grid['grid_limit'] if isinstance(max_grid, dict) else max_grid
    
    print(f'The grid limit is set to: {round(max_grid[0],3)} GW')
    print(f'The max capacity on the grid is: {round(max(data_max_grid_sum),2)} GW')
    print(f'The number of hours where the grid is at its maximum capacity is: {count_max}')


    #----------------------------------------------------------------------------------------------------------------------------------------
    
    # Plot Electricity production and import in BELGIUM
    plt.figure(figsize=figsize) 
    plt.plot(xticks, formatted_grid_data['bal'], label='INLAND balanced', color='blue')
    plt.plot(xticks, formatted_grid_data['neth'], label='NETHERLANDS import', color='orange')
    plt.plot(xticks, formatted_grid_data['deut'], label='DEUTSCHLAND import', color='green')
    plt.plot(xticks, formatted_grid_data['lux'], label='LUXEMBOURG import', color='cyan')
    plt.plot(xticks, formatted_grid_data['fr'], label='FRANCE import', color='red')
    plt.plot(xticks, formatted_grid_data['zb_inl'], label='ZEEBRUGGE import', color='purple')
    plt.plot(xticks, formatted_grid_data['inl_zb'], label='ZEEBRUGGE export', color='brown')
    plt.plot(xticks, data_sum, label='Total electricity', color='black', linestyle='--')
    plt.title(f'Electricity production and imports over time in the Inland cluster', fontsize = 14)
    plt.xlabel('Time [hours]')
    plt.ylabel('Electricity [GWh]')
    plt.xticks(xticks, rotation=90, fontsize = 8)
    plt.yticks(np.arange(0, max(data_sum), 1), fontsize = 8)
    plt.tight_layout()
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
    plt.show()
    

    # Plot Electricity max grid in BELGIUM
    plt.figure(figsize=figsize) 
    plt.plot(xticks, formatted_grid_data['inst_pow'], label='INLAND instant power', color='blue')
    plt.plot(xticks, formatted_grid_data['neth'], label='NETHERLANDS import', color='orange')
    plt.plot(xticks, formatted_grid_data['deut'], label='DEUTSCHLAND import', color='green')
    plt.plot(xticks, formatted_grid_data['lux'], label='LUXEMBOURG import', color='brown')
    plt.plot(xticks, formatted_grid_data['fr'], label='FRANCE import', color='magenta')
    plt.plot(xticks, formatted_grid_data['zb_inl'], label='ZEEBRUGGE import', color='purple') 
    plt.plot(xticks, data_max_grid_sum, label='Total instant power', color='black', linestyle='--') 
    plt.axhline(y=max(data_max_grid_sum), color='red', linestyle=':', linewidth=2, label=f'Max grid limit: {round(max(data_max_grid_sum),2)} GW') 
    # plt.axhline(y=max_grid, color='red', linestyle=':', linewidth=2, label=f'Grid limit: {round(max_grid[0],2)} GW') 
    plt.title(f'Instantaneous grid power flow (INLAND)')
    plt.xlabel('Time [hours]')
    plt.ylabel('Power [GW]')
    plt.xticks(xticks, rotation=90, fontsize = 8) 
    plt.yticks(np.arange(0, max(data_max_grid_sum)+2, 5), fontsize = 8)
    plt.tight_layout()
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=5, frameon=False)
    plt.show()
    

#%% HYDROGEN NOT SERVED FUNCTION:

def balance_hydrogen(model_h2, model_dict, start=0, end=8760, steps=1, figsize=(12, 5)): 


    print(f"Hydrogen balanced (INLAND)")

    h2_flow_out, xticks = pf.get_new_format(
        data=model_h2["variables"]["PIPE_H2_ZB_INL"]["flow_forward_out"], start_index=start, end_index=end, step=steps, xticks='yes'
    )
    h2_flow_in, _ = pf.get_new_format(
        data=model_h2["variables"]["PIPE_H2_ZB_INL"]["flow_reverse_in"], start_index=start, end_index=end, step=steps, xticks='yes'
    )
    h2_balanced, _ = pf.get_new_format(
        data=model_h2["variables"]["INLAND"]["h2_balanced"]["BALANCE"], start_index=start, end_index=end, step=steps, xticks='yes'
    )
    h2_ens, _ = pf.get_new_format(
        data=pf.get_cluster_variable('INLAND', 'h2_ens', model_dict)['values'], start_index=start, end_index=end, step=steps, xticks='yes'
    )

    # 2. Extraction des demandes H2
    try:
        demand_keys = ['demand_h2_id', 'demand_h2_ht', 'demand_h2_tr_road', 'demand_h2_tr_av', 'demand_h2_tr_sh', 'demand_h2_tr_rail', "demand_h2_industry", 
                    "demand_h2_heat", "demand_h2_transport", "demand_h2_transport2", 'demand_efuel_tr_aviation','demand_efuel_tr_truck', 'demand_efuel_tr_shipping']
        
        demand_data = {}
        for key in demand_keys:
            try:
                demand_data[key] = model_h2["global_parameters"][key][key]
            except (KeyError, TypeError):
                demand_data[key] = np.zeros(end - start + 1)
        
        formatted_demand = {}
        for key, data in demand_data.items():
            try:
                formatted_data = np.array(pf.get_new_format(
                    data=data, start_index=start, end_index=end, step=steps, xticks='yes')[0], dtype=float)
                # Only include non-zero demand data
                if np.any(formatted_data):
                    formatted_demand[key] = formatted_data
            except Exception as e:
                    pass
        
        # Calculate total demand, handling empty dictionary case
        if formatted_demand:
            h2_demand_total = np.sum(list(formatted_demand.values()), axis=0)
        else:
            h2_demand_total = np.zeros(len(xticks))
    
    except Exception as e: 
        # Create empty structures to allow function to continue
        formatted_demand = {}
        h2_demand_total = np.zeros(len(xticks))

    # 3. Composantes internes de l'équilibre hydrogène (imports, production, stockage, consommation)
    interco_data = {
        'import_de': model_h2['variables']['INLAND']['h2_imported']['H2_INTERCONNECTION_DE'],
        'export_de': model_h2['variables']['INLAND']['h2_exported']['H2_INTERCONNECTION_DE'],
        'import_nl': model_h2['variables']['INLAND']['h2_imported']['H2_INTERCONNECTION_NL'],
        'export_nl': model_h2['variables']['INLAND']['h2_exported']['H2_INTERCONNECTION_NL'],
        'import_other': model_h2['variables']['INLAND']['h2_imported']['H2_INTERCONNECTION'],
        'export_other': model_h2['variables']['INLAND']['h2_exported']['H2_INTERCONNECTION'],
        'electrolysis': model_h2['variables']['INLAND']['h2_produced']['ELECTROLYSIS_PLANTS'],
        'smr': model_h2['variables']['INLAND']['h2_produced']['SMR'],
        'storage_dis': model_h2['variables']['INLAND']['h2_discharged']['H2_STORAGE'],
        'storage_chg': model_h2['variables']['INLAND']['h2_charged']['H2_STORAGE'],
        'fuel_cells': model_h2['variables']['INLAND']['h2_consumed']['FUEL_CELLS'],
        'methanation': model_h2['variables']['INLAND']['h2_consumed']['METHANATION'],
    }

    formatted_internal = {}
    for key, data in interco_data.items():
        formatted_data = np.array(pf.get_new_format(data=data, start_index=start, end_index=end, step=steps, xticks='yes')[0], dtype=float)
        # Only include non-zero components
        if np.any(formatted_data):
            formatted_internal[key] = formatted_data

    # 4. Calcul des bilans
    h2_internal_balance = np.zeros(len(xticks))
    
    if 'import_de' in formatted_internal:
        h2_internal_balance += formatted_internal['import_de']
    if 'export_de' in formatted_internal:
        h2_internal_balance -= formatted_internal['export_de']
    if 'import_nl' in formatted_internal:
        h2_internal_balance += formatted_internal['import_nl']
    if 'export_nl' in formatted_internal:
        h2_internal_balance -= formatted_internal['export_nl']
    if 'import_other' in formatted_internal:
        h2_internal_balance += formatted_internal['import_other']
    if 'export_other' in formatted_internal:
        h2_internal_balance -= formatted_internal['export_other']
    if 'electrolysis' in formatted_internal:
        h2_internal_balance += formatted_internal['electrolysis']
    if 'smr' in formatted_internal:
        h2_internal_balance += formatted_internal['smr']
    if 'storage_dis' in formatted_internal:
        h2_internal_balance += formatted_internal['storage_dis']
    if 'storage_chg' in formatted_internal:
        h2_internal_balance -= formatted_internal['storage_chg']
    if 'fuel_cells' in formatted_internal:
        h2_internal_balance -= formatted_internal['fuel_cells']
    if 'methanation' in formatted_internal:
        h2_internal_balance -= formatted_internal['methanation']

    h2_flow_net = np.array(h2_flow_out) - np.array(h2_flow_in)
    h2_flow_lhs = h2_flow_net + np.array(h2_balanced) + np.array(h2_ens)

    # 5. GRAPHIQUE 1 : Comparaison équilibre interne simulé vs balance
    plt.figure(figsize=figsize)
    plt.plot(xticks, h2_internal_balance, label="H2 Internal Balance (calculated)", color='blue')
    plt.plot(xticks, h2_balanced, label="H2 Balanced (model)", color='black', linestyle='--')
    plt.title(f"Hydrogen Balance - Internal vs Model (Scenario {i})")
    plt.xlabel("Time [hours]")
    plt.ylabel("Hydrogen [GWh]")
    plt.xticks(xticks, rotation=90, fontsize=8)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
    plt.tight_layout()
    plt.show()

    # 6. GRAPHIQUE 2 : Détail des demandes
    plt.figure(figsize=figsize)
    has_nonzero_demand = False
    for key, data in formatted_demand.items():
        if np.any(data):  # Only plot non-zero demand
            has_nonzero_demand = True
            label = key.replace("demand_h2_", "").replace("demand_efuel_", "efuel_").capitalize()
            plt.plot(xticks, data, label=f"H2 Demand - {label}")
    
    if has_nonzero_demand or np.any(h2_demand_total):
        plt.plot(xticks, h2_demand_total, label="Total Demand", color="black", linestyle="--")
        plt.title(f"Hydrogen Demand Breakdown (INLAND)")
        plt.xlabel("Time [hours]")
        plt.ylabel("Hydrogen [GWh]")
        plt.xticks(xticks, rotation=90, fontsize=8)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.tight_layout()
        plt.show() 

    # 7. GRAPHIQUE 3 : LHS vs Demande totale + non-servi with two y-axes
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # Left y-axis for supply and demand
    ax1.plot(xticks, h2_flow_lhs, label="Supply side (LHS)", color='blue')
    ax1.plot(xticks, h2_demand_total, label="Demand side (RHS)", color='red')
    ax1.set_xlabel("Time [hours]")
    ax1.set_ylabel("Hydrogen [GWh]", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    
    # Only create second y-axis if there's non-zero ENS data
    if np.any(h2_ens):
        ax2 = ax1.twinx()
        ax2.bar(xticks, h2_ens, label="Not Served H2", color='gray', alpha=0.3)
        ax2.set_ylabel("Hydrogen Not Served [GWh]", color='gray')
        ax2.tick_params(axis='y', labelcolor='gray')
        
        # Combine legends from both axes
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, 
                loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
    else:
        ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
    
    plt.title(f"Hydrogen Supply vs Demand (INLAND)")
    plt.xticks(xticks, rotation=90, fontsize=8)
    plt.tight_layout()
    plt.show()


#%% ELECTRICITY OFFSHORE BALANCE: 

def elec_offshore_balance(model, e_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):

    # Initialize lists to store tables for production, consumption, and storage
    
    prod_tables = []
    cons_tables = [] 
    flex_tables_storage = [] 
    bal_tables = [] 

    for i, m in enumerate(model):

        # Production 
        _, prod = node_stat(m, ['OFFSHORE'], variable='e_produced',all_var='no', zero_node=zero_nodes, show ='no')  
        elec_prod = pf.remove_string(prod,' (OFFSHORE)')
        prod_tables.append(table(elec_prod,show='no'))
        elec_prod_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.OFFSHORE.e_produced)

        # Consommation
        _, cons = node_stat(m, ['OFFSHORE'], variable='e_consumed', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')  
        elec_cons = pf.remove_string(cons,' (OFFSHORE)')
        cons_tables.append(table(elec_cons,show='no'))  
        elec_cons_over_time = pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.OFFSHORE.e_consumed))

        # Storage (charged / discharged)
        _, storage = node_stat(m, ['OFFSHORE'], variable=['e_charged','e_discharged'], all_var='no', zero_node=zero_nodes, show ='no')
        elec_storage = pf.remove_string(storage,' (OFFSHORE)')  
        flex_tables_storage.append(table(elec_storage,show='no'))  
        elec_charged_over_time = pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.OFFSHORE.e_charged))
        elec_discharged_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.OFFSHORE.e_discharged)
        
        ##### Balance 
        elec_balance = convert(e_obj[i].prod.OFFSHORE.e_balanced.BALANCE)  
        elec_balance = pf.merge_dictionaries_replace_keys(elec_balance, name=['OFFSHORE BALANCE' ]) 
        bal_tables.append((elec_balance)) 
        elec_balance_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.OFFSHORE.e_balanced.BALANCE) 
        
        

    print(colored('\n=== Electricity production ===', 'black', 'on_green'))
    for t in prod_tables:
        display(t)

    print(colored('\n=== Electricity consumption ===', 'black', 'on_green'))
    for t in cons_tables:
        display(t)

    print(colored('\n=== Storage charged/discharged ===', 'black', 'on_green'))
    for t in flex_tables_storage:
        display(t) 
        
    print(colored('\n=== Electricity Balance ===', 'black', 'on_green'))
    for t in bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Electricity exchange [TWh]", zero_print="yes").T.round(2))
        
    if zoom is not None:
        elec_prod_over_time = pf.zoom_with_timestep(elec_prod_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        elec_cons_over_time = pf.zoom_with_timestep(elec_cons_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_charged_over_time = pf.zoom_with_timestep(elec_charged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_discharged_over_time = pf.zoom_with_timestep(elec_discharged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_balance_over_time = pf.zoom_with_timestep(elec_balance_over_time, zero_nodes=zero_nodes, zoom=zoom)
    
    
    plt.figure(figsize=figsize)
    for key in elec_prod_over_time.keys():
        plt.plot(elec_prod_over_time[key], label=f'{key}')
        
    for key in elec_cons_over_time.keys():
        plt.plot(elec_cons_over_time[key], label=f'{key}')
    
    for key in elec_charged_over_time.keys():
        plt.plot(elec_charged_over_time[key], label=f'Battery charged')
        
    plt.plot(elec_balance_over_time, label=f'Offshore balance', linestyle='--')
        
    for key in elec_discharged_over_time.keys():
        plt.plot(elec_discharged_over_time[key], label=f'Battery discharged')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(elec_discharged_over_time[key]), 1), rotation=90)
            
        else:
            plt.xlabel('Time (hours)')
        
    plt.title('Offshore electricity balance')
    
        
    plt.ylabel('Electricity (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
        
        
#%% ELECTRICITY OFFSHORE HYPEREDGE: 

def elec_offshore_hyperedge(e_obj, model, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):
    
    exch_tables = []
    bal_tables = [] 
    pipe_tables = [] 

    for i, m in enumerate(e_obj):
        
        ##### Exchange
        elec_off_zb = {'e_forward_out': sum(convert(m.variables.HV_OFF_ZB.e_forward_in))/1000}
        elec_zb_off = {'e_reverse_in': sum(convert(m.variables.HV_OFF_ZB.e_reverse_out))/1000}

        elec_exchange = pf.merge_dictionaries_replace_keys(elec_off_zb,elec_zb_off,name=['HV_OFF_ZB', 'HV_ZB_OFF']) 
        exch_tables.append((elec_exchange))  
        elec_exchange_over_time = pf.merge_dictionaries_replace_keys(pf.convert_mmr_to_dict(e_obj[i].variables.HV_OFF_ZB.e_forward_in),
                                                                    pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.HV_OFF_ZB.e_reverse_out)),
                                                                    name=['HV_OFF_ZB', 'HV_ZB_OFF'])


        ##### Balance 
        elec_balance = convert(m.prod.OFFSHORE.e_balanced.BALANCE)  
        
        elec_balance = pf.merge_dictionaries_replace_keys(elec_balance, name=['OFFSHORE BALANCE' ]) 
        bal_tables.append((elec_balance)) 
        elec_balance_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.OFFSHORE.e_balanced.BALANCE) 
        

        ##### Pipe
        elec_pipe = {'e_consumed': sum(model[i]['solution']['elements']['PIPE_H2_OFF_ZB']['variables']["e_consumed"]['values'])/1000}
        
        elec_pipe = pf.merge_dictionaries_replace_keys( pf.negate_values(elec_pipe), name=['PIPE_H2_OFF_ZB' ]) 
        pipe_tables.append((elec_pipe))   
        elec_pipe_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.PIPE_H2_OFF_ZB.e_consumed) 

        
        
    print(colored('\n=== Electricity Exchange ===', 'black', 'on_green'))
    for t in exch_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Electricity exchange [TWh]", zero_print="yes").T.round(2))
        
    print(colored('\n=== Electricity Balance ===', 'black', 'on_green'))
    for t in bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Electricity exchange [TWh]", zero_print="yes").T.round(2))
        
    print(colored('\n=== H2 Pipe ===', 'black', 'on_green'))
    for t in pipe_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Electricity exchange [TWh]", zero_print="yes").T.round(2))
        
        
    if zoom is not None:
        elec_exchange_over_time = pf.zoom_with_timestep(elec_exchange_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        elec_balance_over_time = pf.zoom_with_timestep(elec_balance_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_pipe_over_time = pf.zoom_with_timestep(elec_pipe_over_time, zero_nodes=zero_nodes, zoom=zoom) 
    
    plt.figure(figsize=figsize)
    for key in elec_exchange_over_time.keys():
        plt.plot(elec_exchange_over_time[key], label=f'{key}')
        
    plt.plot(elec_balance_over_time, label=f'Offshore balance', linestyle='--')
    
    plt.plot(elec_pipe_over_time, label=f'PIPE_H2_OFF_ZB') 
    if zoom is not None:
        plt.xlabel(f'Time ({zoom})')
        plt.xticks(np.arange(0, len(elec_pipe_over_time), 1), rotation=90)
        
    else:
        plt.xlabel('Time (hours)')
        
    plt.title('Offshore electricity hyperedge balance')
    
        
    plt.ylabel('Electricity (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
    
    
#%% ELECTRICITY ZEEBRUGGE BALANCE: 

def elec_zeebrugge_balance(model, e_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):
    
    prod_tables = []
    cons_tables = [] 
    flex_tables_storage = []
    bal_tables = []

    for i, m in enumerate(model):

        # Production 
        _, prod = node_stat(m, ['ZEEBRUGGE'], variable='e_produced',all_var='no', zero_node=zero_nodes, show ='no')  
        elec_prod = pf.remove_string(prod,' (ZEEBRUGGE)')
        prod_tables.append(table(elec_prod,show='no'))
        elec_prod_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.ZEEBRUGGE.e_produced)

        # Consommation
        _, cons = node_stat(m, ['ZEEBRUGGE'], variable='e_consumed', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')  
        elec_cons = pf.remove_string(cons,' (ZEEBRUGGE)')
        cons_tables.append(table(elec_cons,show='no'))  
        elec_cons_over_time = pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.ZEEBRUGGE.e_consumed))

        # Storage (charged / discharged)
        _, storage = node_stat(m, ['ZEEBRUGGE'], variable=['e_charged','e_discharged'], all_var='no', zero_node=zero_nodes, show ='no')
        elec_storage = pf.remove_string(storage,' (ZEEBRUGGE)')  
        flex_tables_storage.append(table(elec_storage,show='no')) 
        elec_charged_over_time = pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.ZEEBRUGGE.e_charged))
        elec_discharged_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.ZEEBRUGGE.e_discharged)
        
        ##### BALANCE
        elec_balance = convert(e_obj[i].prod.ZEEBRUGGE.e_balanced.BALANCE)
        elec_balance = pf.merge_dictionaries_replace_keys(elec_balance, name=['ZEEBRUGGE BALANCE'])
        bal_tables.append(elec_balance)
        elec_balance_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.ZEEBRUGGE.e_balanced.BALANCE) 
        

    print(colored('\n=== Electricity production ===', 'black', 'on_cyan'))
    for t in prod_tables:
        display(t)

    print(colored('\n=== Electricity consumption ===', 'black', 'on_cyan'))
    for t in cons_tables:
        display(t)

    print(colored('\n=== Storage charged/discharged ===', 'black', 'on_cyan'))
    for t in flex_tables_storage:
        display(t)
        
    print(colored('\n=== Electricity Balance ===', 'black', 'on_cyan'))
    for t in bal_tables:
        v = (table(pf.transform_dict_into_table(t, column_name="Electricity [TWh]", zero_print="yes").T.round(2)))
        
        
    if zoom is not None:
        elec_prod_over_time = pf.zoom_with_timestep(elec_prod_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        elec_cons_over_time = pf.zoom_with_timestep(elec_cons_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_charged_over_time = pf.zoom_with_timestep(elec_charged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_discharged_over_time = pf.zoom_with_timestep(elec_discharged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_balance_over_time = pf.zoom_with_timestep(elec_balance_over_time, zero_nodes=zero_nodes, zoom=zoom)
    
    plt.figure(figsize=figsize)
    for key in elec_prod_over_time.keys():
        plt.plot(elec_prod_over_time[key], label=f'{key}')
        
    for key in elec_cons_over_time.keys():
        plt.plot(elec_cons_over_time[key], label=f'{key}')
    
    for key in elec_charged_over_time.keys():
        plt.plot(elec_charged_over_time[key], label=f'Battery charged')
    
    plt.plot(elec_balance_over_time, label=f'Offshore balance', linestyle='--')
        
    for key in elec_discharged_over_time.keys():
        plt.plot(elec_discharged_over_time[key], label=f'Battery discharged')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(elec_discharged_over_time[key]), 1), rotation=90)
            
        else:
            plt.xlabel('Time (hours)')
        
    plt.title('Zeebrugge electricity balance')
    
        
    plt.ylabel('Electricity (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
        
        
#%% ELECTRICITY ZEEBRUGGE HYPEREDGE: 

def elec_zeebrugge_hyperedge(e_obj, model, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):
    
    # Initialisation des listes de tableaux
    exch_tables = []
    bal_tables = [] 
    pipe_tables = [] 
    imp_tables = []

    # Boucle pour un ou plusieurs scénarios (ici un seul)
    for i,m in enumerate(e_obj):

        ##### IMPORT
        elec_imp_denmark = convert(m.prod.DENMARK.e_imported)
        elec_imp_uk = convert(m.prod.UNITED_KINGDOM.e_imported)

        elec_imp = pf.merge_dictionaries_replace_keys(elec_imp_denmark, elec_imp_uk, name=['DENMARK', 'UNITED_KINGDOM'])
        imp_tables.append(elec_imp)
        elec_imp_over_time = pf.merge_dictionaries_replace_keys(pf.convert_mmr_to_dict(m.variables.DENMARK.e_imported),
                                                                    pf.convert_mmr_to_dict(m.variables.UNITED_KINGDOM.e_imported),
                                                                    name=['DENMARK', 'UNITED_KINGDOM'])

        ##### EXCHANGE
        elec_zb_inl = {'e_forward_out': sum(convert(m.variables.HV_ZB_INL.e_forward_out)) / 1000}
        elec_inl_zb = {'e_reverse_in': sum(convert(m.variables.HV_ZB_INL.e_reverse_in)) / 1000}
        elec_off_zb = {'e_forward_out': sum(convert(m.variables.HV_OFF_ZB.e_forward_out)) / 1000}
        elec_zb_off = {'e_reverse_in': sum(convert(m.variables.HV_OFF_ZB.e_reverse_in)) / 1000}

        elec_exchange = pf.merge_dictionaries_replace_keys(elec_zb_inl, elec_inl_zb, elec_off_zb, elec_zb_off, name=['HV_ZB_INL', 'HV_INL_ZB', 'HV_OFF_ZB', 'HV_ZB_OFF'])
        exch_tables.append(elec_exchange)
        elec_exchange_over_time = pf.merge_dictionaries_replace_keys(pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.HV_ZB_INL.e_forward_out)),
                                                                    pf.convert_mmr_to_dict(e_obj[i].variables.HV_ZB_INL.e_reverse_in),
                                                                    pf.convert_mmr_to_dict(e_obj[i].variables.HV_OFF_ZB.e_forward_out),
                                                                    pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.HV_OFF_ZB.e_reverse_in)),
                                                                    name=['HV_ZB_INL', 'HV_INL_ZB', 'HV_OFF_ZB', 'HV_ZB_OFF'])

        ##### BALANCE
        elec_balance = convert(e_obj[i].prod.ZEEBRUGGE.e_balanced.BALANCE)
        elec_balance = pf.merge_dictionaries_replace_keys(elec_balance, name=['ZEEBRUGGE BALANCE'])
        bal_tables.append(elec_balance)
        elec_balance_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.ZEEBRUGGE.e_balanced.BALANCE) 

        ##### PIPE
        elec_pipe = {'e_consumed': sum(model[i]['solution']['elements']['PIPE_H2_ZB_INL']['variables']["e_consumed"]['values']) / 1000}
        elec_pipe = pf.merge_dictionaries_replace_keys(elec_pipe, name=['PIPE_H2_ZB_INL'])
        pipe_tables.append(elec_pipe)
        elec_pipe_over_time = pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.PIPE_H2_OFF_ZB.e_consumed))
        

    print(colored('\n=== Electricity Import ===', 'black', 'on_cyan'))
    for t in imp_tables:
        v = (table(pf.transform_dict_into_table(t, column_name="Electricity import [TWh]", zero_print="yes").T.round(2)))

    print(colored('\n=== Electricity Exchange ===', 'black', 'on_cyan'))
    for t in exch_tables:
        v = (table(pf.transform_dict_into_table(t, column_name="Electricity exchange [TWh]", zero_print="yes").T.round(2)))

    print(colored('\n=== Electricity Balance ===', 'black', 'on_cyan'))
    for t in bal_tables:
        v = (table(pf.transform_dict_into_table(t, column_name="Electricity [TWh]", zero_print="yes").T.round(2)))

    print(colored('\n=== H2 Pipe ===', 'black', 'on_cyan'))
    for t in pipe_tables:
        v = (table(pf.transform_dict_into_table(t, column_name="Electricity [TWh]", zero_print="yes").T.round(5)))
        
    
    if zoom is not None:
        elec_imp_over_time = pf.zoom_with_timestep(elec_imp_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        elec_exchange_over_time = pf.zoom_with_timestep(elec_exchange_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        elec_balance_over_time = pf.zoom_with_timestep(elec_balance_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_pipe_over_time = pf.zoom_with_timestep(elec_pipe_over_time, zero_nodes=zero_nodes, zoom=zoom) 
    
    plt.figure(figsize=figsize)
    for key in elec_imp_over_time.keys():
        plt.plot(elec_imp_over_time[key], label=f'{key}')
        
    for key in elec_exchange_over_time.keys():
        plt.plot(elec_exchange_over_time[key], label=f'{key}')
    
    plt.plot(elec_balance_over_time, label=f'Offshore balance', linestyle='--')
    
    plt.plot(elec_pipe_over_time, label=f'PIPE_H2_ZB_INL') 
    if zoom is not None:
        plt.xlabel(f'Time ({zoom})')
        plt.xticks(np.arange(0, len(elec_pipe_over_time), 1), rotation=90)
        
    else:
        plt.xlabel('Time (hours)')
        
    plt.title('Zeebrugge electricity hyperedge balance')
    
        
    plt.ylabel('Electricity (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
        
        
#%% ELECTRICITY INLAND BALANCE: 

def elec_inland_balance(model, e_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):  

    prod_tables = []
    cons_tables = []
    flex_tables_load = []
    flex_tables_storage = []
    bal_tables = []

    for i, m in enumerate(model):

        # Production 
        _, prod = node_stat(m, ['INLAND'], variable='e_produced',all_var='no', zero_node=zero_nodes, show ='no')  
        elec_prod = pf.remove_string(prod,' (INLAND)')
        prod_tables.append(table(elec_prod,show='no'))
        elec_prod_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.INLAND.e_produced)

        # Consommation
        _, cons = node_stat(m, ['INLAND'], variable='e_consumed', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')  
        elec_cons = pf.remove_string(cons,' (INLAND)')
        cons_tables.append(table(elec_cons,show='no'))  
        elec_cons_over_time = pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.INLAND.e_consumed))

        # Storage (charged / discharged)
        _, storage = node_stat(m, ['INLAND'], variable=['e_charged','e_discharged'], all_var='no', zero_node=zero_nodes, show ='no')
        elec_storage = pf.remove_string(storage,' (INLAND)')  
        flex_tables_storage.append(table(elec_storage,show='no'))
        elec_charged_over_time = pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.INLAND.e_charged))
        elec_discharged_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.INLAND.e_discharged)
        
        # Load shifting 
        _, load_inc = node_stat(m, ['INLAND'], variable='load_increase', all_var='no', zero_node=zero_nodes, show ='no')
        _, load_red = node_stat(m, ['INLAND'], variable='load_reduction', all_var='no', zero_node=zero_nodes, show ='no') 
        elec_load_inc = pf.remove_string(load_inc,' (INLAND)')
        elec_load_red = pf.remove_string(load_red,' (INLAND)')
        elec_load = pf.merge_dictionaries(elec_load_inc, elec_load_red)
        flex_tables_load.append(table(elec_load,show='no'))
        elec_load_inc_over_time = pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.INLAND.load_increase))
        elec_load_red_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.INLAND.load_reduction) 
        
        ##### BALANCE
        elec_balance = convert(e_obj[i].prod.INLAND.e_balanced.BALANCE)
        elec_balance = pf.merge_dictionaries_replace_keys(elec_balance, name=['INLAND BALANCE'])
        bal_tables.append(elec_balance)
        elec_balance_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.INLAND.e_balanced.BALANCE) 



    print(colored('\n=== Electricity production ===', 'black', 'on_red'))
    for t in prod_tables:
        display(t)

    print(colored('\n=== Electricity consumption ===', 'black', 'on_red'))
    for t in cons_tables:
        display(t)

    print(colored('\n=== Storage charged/discharged ===', 'black', 'on_red'))
    for t in flex_tables_storage:
        display(t)
        
    print(colored('\n=== Load shifting/shedding ===', 'black', 'on_red'))
    for t in flex_tables_load:
        display(t)
    
    print(colored('\n=== Electricity Balance ===', 'black', 'on_red'))
    for t in bal_tables:
        v = (table(pf.transform_dict_into_table(t, column_name="Electricity [TWh]", zero_print="yes").T.round(2))) 
    
    if zoom is not None:
        elec_prod_over_time = pf.zoom_with_timestep(elec_prod_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        elec_cons_over_time = pf.zoom_with_timestep(elec_cons_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_charged_over_time = pf.zoom_with_timestep(elec_charged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_discharged_over_time = pf.zoom_with_timestep(elec_discharged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_load_inc_over_time = pf.zoom_with_timestep(elec_load_inc_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_load_red_over_time = pf.zoom_with_timestep(elec_load_red_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_balance_over_time = pf.zoom_with_timestep(elec_balance_over_time, zero_nodes=zero_nodes, zoom=zoom)
        
    
    plt.figure(figsize=figsize)
    for key in elec_prod_over_time.keys():
        plt.plot(elec_prod_over_time[key], label=f'{key}')
        
    for key in elec_cons_over_time.keys():
        plt.plot(elec_cons_over_time[key], label=f'{key}')
    
    for key in elec_charged_over_time.keys():
        plt.plot(elec_charged_over_time[key], label=f'Battery charged')
        
    for key in elec_discharged_over_time.keys():
        plt.plot(elec_discharged_over_time[key], label=f'Battery discharged')
        
    plt.plot(elec_balance_over_time, label=f'Inland balance', linestyle='--')
    
    for key in elec_load_inc_over_time.keys():
        plt.plot(elec_load_inc_over_time[key], label=f'{key}')
        
    for key in elec_load_red_over_time.keys():
        plt.plot(elec_load_red_over_time[key], label=f'{key}')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(elec_load_red_over_time[key]), 1), rotation=90)
            
        else:
            plt.xlabel('Time (hours)')
        
    plt.title('Inland electricity balance')
    
        
    plt.ylabel('Electricity (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
        
#%% ELECTRICITY INLAND HYPEREDGE: 

def elec_inland_hyperedge(model, e_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):

    # Initialisation des listes de tableaux
    imp_tables = []
    exch_tables = []
    bal_tables = []
    ens_tables = []
    demand_tables = []

    # Boucle pour un ou plusieurs scénarios
    for i, m in enumerate(e_obj):

        ##### IMPORT
        elec_imp_de = convert(m.prod.DEUTSCHLAND.e_imported)
        elec_imp_nl = convert(m.prod.NETHERLANDS.e_imported)
        elec_imp_lux = convert(m.prod.LUXEMBOURG.e_imported)
        elec_imp_fr = convert(m.prod.FRANCE.e_imported)
        elec_imp = pf.merge_dictionaries_replace_keys(elec_imp_de, elec_imp_nl, elec_imp_lux, elec_imp_fr, name=['DEUTSCHLAND', 'NETHERLANDS', 'LUXEMBOURG', 'FRANCE'])
        imp_tables.append(elec_imp)
        elec_imp_over_time = pf.merge_dictionaries_replace_keys(pf.convert_mmr_to_dict(m.variables.DEUTSCHLAND.e_imported),
                                                                    pf.convert_mmr_to_dict(m.variables.NETHERLANDS.e_imported),
                                                                    pf.convert_mmr_to_dict(m.variables.LUXEMBOURG.e_imported),
                                                                    pf.convert_mmr_to_dict(m.variables.FRANCE.e_imported),
                                                                    name=['DEUTSCHLAND', 'NETHERLANDS', 'LUXEMBOURG', 'FRANCE'])

        ##### EXCHANGE
        elec_zb_inl = {'e_forward_out': sum(convert(m.variables.HV_ZB_INL.e_forward_out)) / 1000}
        elec_inl_zb = {'e_reverse_in': sum(convert(m.variables.HV_ZB_INL.e_reverse_in)) / 1000}
        elec_exchange = pf.merge_dictionaries_replace_keys(elec_zb_inl, elec_inl_zb, name=['HV_ZB_INL', 'HV_INL_ZB'])
        exch_tables.append(elec_exchange)
        elec_exchange_over_time = pf.merge_dictionaries_replace_keys(pf.convert_mmr_to_dict(e_obj[i].variables.HV_ZB_INL.e_forward_out),
                                                                    pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].variables.HV_ZB_INL.e_reverse_in)), 
                                                                    name=['HV_ZB_INL', 'HV_INL_ZB' ])

        ##### BALANCE + ENS
        elec_balance = convert(m.prod.INLAND.e_balanced.BALANCE)
        elec_ens = {'e_ens': sum(model[i]['solution']['elements']['INLAND']["variables"]['e_ens']["values"]) / 1000}
        elec_bal_ens = pf.merge_dictionaries_replace_keys(elec_balance, elec_ens, name=['INLAND BALANCE', 'INLAND ELECTRICITY NOT SERVED'])
        bal_tables.append(elec_bal_ens)
        elec_balance_over_time = pf.convert_mmr_to_dict(e_obj[i].variables.INLAND.e_balanced.BALANCE)

        ##### DEMAND
        elec_demand_el = {'demand_el': sum(m.global_parameters.demand_el.demand_el) / 1000}
        elec_demand_el_ht = {'demand_el_ht': sum(m.global_parameters.demand_el_ht.demand_el_ht) / 1000}
        elec_demand_el_tr = {'demand_el_tr': sum(model[i]['solution']['elements']['INLAND']["variables"]['demand_el_tr']["values"]) / 1000}
        elec_demand = pf.merge_dictionaries_replace_keys(elec_demand_el, elec_demand_el_ht, elec_demand_el_tr, name=['Electricity demand', 'Electricity heating demand', 'Electricity transport demand'])
        demand_tables.append(elec_demand)
        elec_demand_over_time = pf.merge_dictionaries_replace_keys(pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].global_parameters.demand_el.demand_el)),
                                                                    pf.negate_values(pf.convert_mmr_to_dict(e_obj[i].global_parameters.demand_el_ht.demand_el_ht)),
                                                                    pf.negate_values(model[i]['solution']['elements']['INLAND']["variables"]['demand_el_tr']["values"]),
                                                                    name=['Electricity demand', 'Electricity heating demand', 'Electricity transport demand'])

    # === AFFICHAGE DES TABLEAUX ===

    print(colored('\n=== Electricity Import ===', 'black', 'on_red'))
    for t in imp_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Electricity import [TWh]", zero_print="yes").T.round(2))

    print(colored('\n=== Electricity Exchange ===', 'black', 'on_red'))
    for t in exch_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Electricity exchange [TWh]", zero_print="yes").T.round(2))

    print(colored('\n=== Electricity Balance + Not Served ===', 'black', 'on_red'))
    for t in bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Electricity [TWh]", zero_print="yes").T.round(3))

    print(colored('\n=== Electricity Demand ===', 'black', 'on_red'))
    demand_elec = 0
    for t in demand_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Electricity demand [TWh]", zero_print="yes").T.round(2))      
        
    
    if zoom is not None:
        elec_imp_over_time = pf.zoom_with_timestep(elec_imp_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        elec_exchange_over_time = pf.zoom_with_timestep(elec_exchange_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        elec_balance_over_time = pf.zoom_with_timestep(elec_balance_over_time, zero_nodes=zero_nodes, zoom=zoom)
        elec_demand_over_time = pf.zoom_with_timestep(elec_demand_over_time, zero_nodes=zero_nodes, zoom=zoom) 
    
    plt.figure(figsize=figsize)
    for key in elec_imp_over_time.keys():
        plt.plot(elec_imp_over_time[key], label=f'{key}')
        
    for key in elec_exchange_over_time.keys():
        plt.plot(elec_exchange_over_time[key], label=f'{key}')
    
    plt.plot(elec_balance_over_time, label=f'Inland balance', linestyle='--')
    
    for key in elec_demand_over_time.keys():
        plt.plot(elec_demand_over_time[key], label=f'{key}')
        
    if zoom is not None:
        plt.xlabel(f'Time ({zoom})')
        plt.xticks(np.arange(0, len(elec_balance_over_time), 1), rotation=90)
        
    else:
        plt.xlabel('Time (hours)')
        
    plt.title('Inland electricity hyperedge balance')
    
        
    plt.ylabel('Electricity (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
    
        
#%% HYDROGEN OFFSHORE BALANCE:     

def h2_offshore_balance(model, h2_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):
    
    prod_tables = []
    cons_tables = [] 
    flex_tables_storage = [] 
    bal_tables = [] 
    
    for i, m in enumerate(model):

        # Production 
        _, prod = node_stat(m, ['OFFSHORE'], variable='h2_produced', all_var='no', zero_node=zero_nodes, show='no')  
        h2_prod = pf.remove_string(prod, ' (OFFSHORE)')
        prod_tables.append(table(h2_prod, show='no'))
        h2_prod_over_time = pf.convert_mmr_to_dict(h2_obj[i].variables.OFFSHORE.h2_produced)

        # Consumption
        _, cons = node_stat(m, ['OFFSHORE'], variable='h2_consumed', all_var='no', zero_node=zero_nodes, show='no', just_prod='yes')  
        h2_cons = pf.remove_string(cons, ' (OFFSHORE)')
        cons_tables.append(table(h2_cons, show='no'))  
        h2_cons_over_time = pf.negate_values(pf.convert_mmr_to_dict(h2_obj[i].variables.OFFSHORE.h2_consumed))

        # Storage (charged / discharged)
        _, storage = node_stat(m, ['OFFSHORE'], variable=['h2_charged', 'h2_discharged'], all_var='no', zero_node=zero_nodes, show='no')
        h2_storage = pf.remove_string(storage, ' (OFFSHORE)')  
        flex_tables_storage.append(table(h2_storage, show='no'))  
        h2_charged_over_time = pf.negate_values(pf.convert_mmr_to_dict(h2_obj[i].variables.OFFSHORE.h2_charged))
        h2_discharged_over_time = pf.convert_mmr_to_dict(h2_obj[i].variables.OFFSHORE.h2_discharged)
        
        ##### Balance 
        h2_balance = convert(h2_obj[i].prod.OFFSHORE.h2_balanced.BALANCE)  
        h2_balance = pf.merge_dictionaries_replace_keys(h2_balance, name=['OFFSHORE BALANCE' ]) 
        bal_tables.append((h2_balance)) 
        h2_balance_over_time = pf.convert_mmr_to_dict(h2_obj[i].variables.OFFSHORE.h2_balanced.BALANCE) 
        

    print(colored('\n=== Hydrogen production ===', 'black', 'on_green'))
    for t in prod_tables:
        display(t)

    print(colored('\n=== Hydrogen consumption ===', 'black', 'on_green'))
    for t in cons_tables:
        display(t)

    print(colored('\n=== Hydrogen storage charged/discharged ===', 'black', 'on_green'))
    for t in flex_tables_storage:
        display(t)   
        
    print(colored('\n=== Hydrogen Balance ===', 'black', 'on_green'))
    for t in bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Hydrogen [TWh]", zero_print="yes").T.round(2))       
        
    if zoom is not None:
        h2_prod_over_time = pf.zoom_with_timestep(h2_prod_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        h2_cons_over_time = pf.zoom_with_timestep(h2_cons_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_charged_over_time = pf.zoom_with_timestep(h2_charged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_discharged_over_time = pf.zoom_with_timestep(h2_discharged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_balance_over_time = pf.zoom_with_timestep(h2_balance_over_time, zero_nodes=zero_nodes, zoom=zoom)
    
    
    plt.figure(figsize=figsize)
    for key in h2_prod_over_time.keys():
        plt.plot(h2_prod_over_time[key], label=f'{key}')
        
    for key in h2_cons_over_time.keys():
        plt.plot(h2_cons_over_time[key], label=f'{key}')
    
    for key in h2_charged_over_time.keys():
        plt.plot(h2_charged_over_time[key], label=f'Battery charged')
        
    plt.plot(h2_balance_over_time, label=f'Offshore balance', linestyle='--')
        
    for key in h2_discharged_over_time.keys():
        plt.plot(h2_discharged_over_time[key], label=f'Battery discharged')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(h2_discharged_over_time[key]), 1), rotation=90)
            
        else:
            plt.xlabel('Time (hours)')
        
    plt.title('Offshore hydrogen balance')
    
    plt.ylabel('Hydrogen (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
        
            
#%% HYDROGEN OFFSHORE HYPEREDGE: 
    
def h2_offshore_hyperedge(model, h2_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):
        
    h2_exch_tables = []
    h2_bal_tables = []

    # Boucle pour un ou plusieurs scénarios
    for i, m in enumerate(h2_obj):

        ##### EXCHANGE
        h2_off_zb = {'flow_forward_out': sum(convert(m.variables.PIPE_H2_OFF_ZB.flow_forward_out))/1000}
        h2_zb_off = {'flow_reverse_in': sum(convert(m.variables.PIPE_H2_OFF_ZB.flow_reverse_in))/1000}
        h2_exchange = pf.merge_dictionaries_replace_keys(h2_off_zb, h2_zb_off, name=['PIPE_H2_OFF_ZB', 'PIPE_H2_ZB_OFF'])
        h2_exch_tables.append(h2_exchange)
        h2_exch_over_time = pf.merge_dictionaries_replace_keys(pf.negate_values(pf.convert_mmr_to_dict(m.variables.PIPE_H2_OFF_ZB.flow_forward_out)),
                                                                pf.convert_mmr_to_dict(m.variables.PIPE_H2_OFF_ZB.flow_reverse_in),
                                                                name=['PIPE_H2_OFF_ZB', 'PIPE_H2_ZB_OFF'])

        ##### BALANCE
        h2_balance = convert(m.prod.OFFSHORE.h2_balanced.BALANCE)
        h2_balance = pf.merge_dictionaries_replace_keys(h2_balance, name=['OFFSHORE BALANCE'])
        h2_bal_tables.append(h2_balance)
        h2_bal_over_time = pf.convert_mmr_to_dict(m.variables.OFFSHORE.h2_balanced.BALANCE)


    # === AFFICHAGE DES TABLEAUX ===

    print(colored('\n=== Hydrogen Exchange ===', 'black', 'on_green'))
    for t in h2_exch_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Hydrogen exchange [TWh]", zero_print="yes").T.round(2))

    print(colored('\n=== Hydrogen Balance ===', 'black', 'on_green'))
    for t in h2_bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Hydrogen [TWh]", zero_print="yes").T.round(2))

    if zoom is not None:
        h2_exch_over_time = pf.zoom_with_timestep(h2_exch_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        h2_bal_over_time = pf.zoom_with_timestep(h2_bal_over_time, zero_nodes=zero_nodes, zoom=zoom)
    
    
    plt.figure(figsize=figsize)
    for key in h2_exch_over_time.keys():
        plt.plot(h2_exch_over_time[key], label=f'{key}')
        
    plt.plot(h2_bal_over_time, label=f'Offshore balance', linestyle='--')

    if zoom is not None:
        plt.xlabel(f'Time ({zoom})')
        plt.xticks(np.arange(0, len(h2_exch_over_time[key]), 1), rotation=90)
        
    else:
        plt.xlabel('Time (hours)')
        
    plt.title('Offshore hydrogen balance')
    
        
    plt.ylabel('Hydrogen (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()

#%% HYDROGEN ZEEBRUGGE BALANCE:

def h2_zeebrugge_balance(model, h2_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):
    
    prod_tables = []
    cons_tables = [] 
    flex_tables_storage = []
    imp_tables = []
    exp_tables = []
    bal_tables = [] 

    for i, m in enumerate(model):

        # Production 
        _, prod = node_stat(m, ['ZEEBRUGGE'], variable='h2_produced',all_var='no', zero_node=zero_nodes, show ='no')  
        h2_prod = pf.remove_string(prod,' (ZEEBRUGGE)')
        prod_tables.append(table(h2_prod,show='no'))
        h2_prod_over_time = pf.convert_mmr_to_dict(h2_obj[i].variables.ZEEBRUGGE.h2_produced)

        # Consommation
        _, cons = node_stat(m, ['ZEEBRUGGE'], variable='h2_consumed', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')  
        h2_cons = pf.remove_string(cons,' (ZEEBRUGGE)')
        cons_tables.append(table(h2_cons,show='no'))  
        h2_cons_over_time = pf.negate_values(pf.convert_mmr_to_dict(h2_obj[i].variables.ZEEBRUGGE.h2_consumed))

        # Storage (charged / discharged)
        _, storage = node_stat(m, ['ZEEBRUGGE'], variable=['h2_charged','h2_discharged'], all_var='no', zero_node=zero_nodes, show ='no')
        h2_storage = pf.remove_string(storage,' (ZEEBRUGGE)')  
        flex_tables_storage.append(table(h2_storage,show='no'))
        h2_charged_over_time = pf.negate_values(pf.convert_mmr_to_dict(h2_obj[i].variables.ZEEBRUGGE.h2_charged))
        h2_discharged_over_time = pf.convert_mmr_to_dict(h2_obj[i].variables.ZEEBRUGGE.h2_discharged) 
        
        # Import 
        _, imp = node_stat(m, ['ZEEBRUGGE'], variable='h2_imported', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')
        h2_imp = pf.remove_string(imp,' (ZEEBRUGGE)')
        imp_tables.append(table(h2_imp,show='no'))
        h2_imp_over_time = pf.convert_mmr_to_dict(h2_obj[i].variables.ZEEBRUGGE.h2_imported)
        
        # Export 
        _, exp = node_stat(m, ['ZEEBRUGGE'], variable='h2_exported', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')
        h2_exp = pf.remove_string(exp,' (ZEEBRUGGE)')
        exp_tables.append(table(h2_exp,show='no'))
        h2_exp_over_time = pf.negate_values(pf.convert_mmr_to_dict(h2_obj[i].variables.ZEEBRUGGE.h2_exported))
        
        ##### Balance 
        h2_balance = convert(h2_obj[i].prod.OFFSHORE.h2_balanced.BALANCE)  
        h2_balance = pf.merge_dictionaries_replace_keys(h2_balance, name=['OFFSHORE BALANCE' ]) 
        bal_tables.append((h2_balance)) 
        h2_balance_over_time = pf.convert_mmr_to_dict(h2_obj[i].variables.ZEEBRUGGE.h2_balanced.BALANCE) 
        
        

    print(colored('\n=== Hydrogen production ===', 'black', 'on_cyan'))
    for t in prod_tables:
        display(t)

    print(colored('\n=== Hydrogen consumption ===', 'black', 'on_cyan'))
    for t in cons_tables:
        display(t)

    print(colored('\n=== Storage charged/discharged ===', 'black', 'on_cyan'))
    for t in flex_tables_storage:
        display(t)
        
    print(colored('\n=== Hydrogen Import ===', 'black', 'on_cyan'))
    for t in imp_tables:
        display(t)
        
    print(colored('\n=== Hydrogen Export ===', 'black', 'on_cyan'))
    for t in exp_tables:
        display(t)
        
    print(colored('\n=== Hydrogen Balance ===', 'black', 'on_cyan'))
    for t in bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Hydrogen [TWh]", zero_print="yes").T.round(2))

    if zoom is not None:
        h2_prod_over_time = pf.zoom_with_timestep(h2_prod_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        h2_cons_over_time = pf.zoom_with_timestep(h2_cons_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_charged_over_time = pf.zoom_with_timestep(h2_charged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_discharged_over_time = pf.zoom_with_timestep(h2_discharged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_balance_over_time = pf.zoom_with_timestep(h2_balance_over_time, zero_nodes=zero_nodes, zoom=zoom)
    
    
    plt.figure(figsize=figsize)
    for key in h2_prod_over_time.keys():
        plt.plot(h2_prod_over_time[key], label=f'{key}')
        
    for key in h2_cons_over_time.keys():
        plt.plot(h2_cons_over_time[key], label=f'{key}')
    
    for key in h2_charged_over_time.keys():
        plt.plot(h2_charged_over_time[key], label=f'Battery charged')
        
    plt.plot(h2_balance_over_time, label=f'Zeebrugge balance', linestyle='--')
        
    for key in h2_discharged_over_time.keys():
        plt.plot(h2_discharged_over_time[key], label=f'Battery discharged')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(h2_discharged_over_time[key]), 1), rotation=90)
            
        else:
            plt.xlabel('Time (hours)')
        
    plt.title('Zeebrugge hydrogen balance')
    
        
    plt.ylabel('Hydrogen (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
    
    
#%% HYDROGEN ZEEBRUGGE HYPEREDGE:

def h2_zeebrugge_hyperedge(model, h2_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):
    
    # Initialisation des listes de tableaux
    h2_exch_tables = []
    h2_bal_tables = []

    # Boucle pour un ou plusieurs scénarios
    for i, m in enumerate(h2_obj):

        ##### EXCHANGE
        h2_off_zb = {'flow_forward_out': sum(convert(m.variables.PIPE_H2_OFF_ZB.flow_forward_out)) / 1000}
        h2_zb_off = {'flow_reverse_in': sum(convert(m.variables.PIPE_H2_OFF_ZB.flow_reverse_in)) / 1000}
        h2_zb_inl = {'flow_forward_out': sum(convert(m.variables.PIPE_H2_ZB_INL.flow_forward_out)) / 1000}
        h2_inl_zb = {'flow_reverse_in': sum(convert(m.variables.PIPE_H2_ZB_INL.flow_reverse_in)) / 1000}
        h2_exchange = pf.merge_dictionaries_replace_keys(h2_off_zb, h2_zb_off, h2_zb_inl, h2_inl_zb, name=['PIPE_H2_OFF_ZB', 'PIPE_H2_ZB_OFF', 'PIPE_H2_ZB_INL', 'PIPE_H2_INL_ZB'])
        h2_exch_tables.append(h2_exchange)
        h2_exch_over_time = pf.merge_dictionaries_replace_keys(pf.negate_values(pf.convert_mmr_to_dict(m.variables.PIPE_H2_OFF_ZB.flow_forward_out)),
                                                                pf.convert_mmr_to_dict(m.variables.PIPE_H2_OFF_ZB.flow_reverse_in),
                                                                pf.negate_values(pf.convert_mmr_to_dict(m.variables.PIPE_H2_ZB_INL.flow_forward_out)),
                                                                pf.convert_mmr_to_dict(m.variables.PIPE_H2_ZB_INL.flow_reverse_in),
                                                                name=['PIPE_H2_OFF_ZB', 'PIPE_H2_ZB_OFF', 'PIPE_H2_ZB_INL', 'PIPE_H2_INL_ZB'])

        ##### BALANCE
        h2_balance = convert(m.prod.ZEEBRUGGE.h2_balanced.BALANCE)
        h2_balance = pf.merge_dictionaries_replace_keys(h2_balance, name=['ZEEBRUGGE BALANCE'])
        h2_bal_tables.append(h2_balance)
        h2_bal_over_time = pf.convert_mmr_to_dict(m.variables.ZEEBRUGGE.h2_balanced.BALANCE)

    # === AFFICHAGE DES TABLEAUX ===

    print(colored('\n=== Hydrogen Exchange ===', 'black', 'on_cyan'))
    for t in h2_exch_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Hydrogen exchange [TWh]", zero_print="yes").T.round(2))

    print(colored('\n=== Hydrogen Balance ===', 'black', 'on_cyan'))
    for t in h2_bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Hydrogen [TWh]", zero_print="yes").T.round(2))

    if zoom is not None:
        h2_exch_over_time = pf.zoom_with_timestep(h2_exch_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        h2_bal_over_time = pf.zoom_with_timestep(h2_bal_over_time, zero_nodes=zero_nodes, zoom=zoom)
    
    
    plt.figure(figsize=figsize)
    for key in h2_exch_over_time.keys():
        plt.plot(h2_exch_over_time[key], label=f'{key}')
        
    plt.plot(h2_bal_over_time, label=f'Zeebrugge balance', linestyle='--')

    if zoom is not None:
        plt.xlabel(f'Time ({zoom})')
        plt.xticks(np.arange(0, len(h2_exch_over_time[key]), 1), rotation=90)
        
    else:
        plt.xlabel('Time (hours)')
        
    plt.title('Zeebrugge hydrogen balance')
    
        
    plt.ylabel('Hydrogen (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()

#%% HYDROGEN INLAND BALANCE:

def h2_inland_balance(model, h2_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):
    
    prod_tables = []
    cons_tables = []
    imp_tables = []
    exp_tables = []
    flex_tables_storage = []
    bal_tables = []

    for i, m in enumerate(model):

        # Production 
        _, prod = node_stat(m, ['INLAND'], variable='h2_produced',all_var='no', zero_node=zero_nodes, show ='no')  
        h2_prod = pf.remove_string(prod,' (INLAND)')
        prod_tables.append(table(h2_prod,show='no'))
        h2_prod_over_time = pf.convert_mmr_to_dict(h2_obj[i].variables.INLAND.h2_produced)

        # Consommation
        _, cons = node_stat(m, ['INLAND'], variable='h2_consumed', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')  
        h2_cons = pf.remove_string(cons,' (INLAND)')
        cons_tables.append(table(h2_cons,show='no'))  
        h2_cons_over_time = pf.negate_values(pf.convert_mmr_to_dict(h2_obj[i].variables.INLAND.h2_consumed))

        # Storage (charged / discharged)
        _, storage = node_stat(m, ['INLAND'], variable=['h2_charged','h2_discharged'], all_var='no', zero_node=zero_nodes, show ='no')
        h2_storage = pf.remove_string(storage,' (INLAND)')  
        flex_tables_storage.append(table(h2_storage,show='no'))
        h2_charged_over_time = pf.negate_values(pf.convert_mmr_to_dict(h2_obj[i].variables.INLAND.h2_charged))
        h2_discharged_over_time = pf.convert_mmr_to_dict(h2_obj[i].variables.INLAND.h2_discharged)
        
        # Import 
        _, imp = node_stat(m, ['INLAND'], variable='h2_imported', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')
        h2_imp = pf.remove_string(imp,' (INLAND)')  
        imp_tables.append(table(h2_imp,show='no'))
        h2_imp_over_time = pf.convert_mmr_to_dict(h2_obj[i].variables.INLAND.h2_imported)
        
        # Export 
        _, exp = node_stat(m, ['INLAND'], variable='h2_exported', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')
        h2_exp = pf.remove_string(exp,' (INLAND)')  
        exp_tables.append(table(h2_exp,show='no'))
        h2_exp_over_time = pf.negate_values(pf.convert_mmr_to_dict(h2_obj[i].variables.INLAND.h2_exported))

        ##### Balance
        h2_balance = convert(h2_obj[i].prod.INLAND.h2_balanced.BALANCE)  
        h2_balance = pf.merge_dictionaries_replace_keys(h2_balance, name=['INLAND BALANCE' ]) 
        bal_tables.append((h2_balance)) 
        h2_balance_over_time = pf.convert_mmr_to_dict(h2_obj[i].variables.INLAND.h2_balanced.BALANCE)

    print(colored('\n=== Hydrogen production ===', 'black', 'on_red'))
    for t in prod_tables:
        display(t)

    print(colored('\n=== Hydrogen consumption ===', 'black', 'on_red'))
    for t in cons_tables:
        display(t)

    print(colored('\n=== Storage charged/discharged ===', 'black', 'on_red'))
    for t in flex_tables_storage:
        display(t)
        
    print(colored('\n=== Hydrogen Import ===', 'black', 'on_red'))
    for t in imp_tables:
        display(t)
        
    print(colored('\n=== Hydrogen Export ===', 'black', 'on_red'))
    for t in exp_tables:
        display(t) 
    
    print(colored('\n=== Hydrogen Balance ===', 'black', 'on_red'))
    for t in bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Hydrogen [TWh]", zero_print="yes").T.round(2))
        
    if zoom is not None:
        h2_prod_over_time = pf.zoom_with_timestep(h2_prod_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        h2_cons_over_time = pf.zoom_with_timestep(h2_cons_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_charged_over_time = pf.zoom_with_timestep(h2_charged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_discharged_over_time = pf.zoom_with_timestep(h2_discharged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_imp_over_time = pf.zoom_with_timestep(h2_imp_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_exp_over_time = pf.zoom_with_timestep(h2_exp_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_balance_over_time = pf.zoom_with_timestep(h2_balance_over_time, zero_nodes=zero_nodes, zoom=zoom)
        
    plt.figure(figsize=figsize)
    for key in h2_prod_over_time.keys():
        plt.plot(h2_prod_over_time[key], label=f'{key}')
        
    for key in h2_cons_over_time.keys():
        plt.plot(h2_cons_over_time[key], label=f'{key}')
        
    for key in h2_charged_over_time.keys():
        plt.plot(h2_charged_over_time[key], label=f'Battery charged')
    
    plt.plot(h2_balance_over_time, label=f'Inland balance', linestyle='--')
    
    for key in h2_exp_over_time.keys():
        plt.plot(h2_exp_over_time[key])
        
    for key in h2_imp_over_time.keys():
        plt.plot(h2_imp_over_time[key] )
    
    for key in h2_discharged_over_time.keys():
        plt.plot(h2_discharged_over_time[key], label=f'Battery discharged')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(h2_discharged_over_time[key]), 1), rotation=90)
        else:
            plt.xlabel('Time (hours)')
            
    plt.title('Inland hydrogen balance')
    plt.ylabel('Hydrogen (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()  
        
#%% HYDROGEN INLAND HYPEREDGE:

def h2_inland_hyperedge(model, h2_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):
    
    # Initialisation des listes de tableaux
    h2_exch_tables = []
    h2_bal_tables = []
    h2_demand_tables = []

    # Boucle pour un ou plusieurs scénarios
    for i, m in enumerate(h2_obj):

        ##### EXCHANGE
        h2_zb_inl = {'flow_forward_out': sum(convert(m.variables.PIPE_H2_ZB_INL.flow_forward_out)) / 1000}
        h2_inl_zb = {'flow_reverse_in': sum(convert(m.variables.PIPE_H2_ZB_INL.flow_reverse_in)) / 1000}
        h2_exchange = pf.merge_dictionaries_replace_keys(h2_zb_inl, h2_inl_zb, name=['PIPE_H2_ZB_INL', 'PIPE_H2_INL_ZB'])
        h2_exch_tables.append(h2_exchange)
        h2_exch_over_time = pf.merge_dictionaries_replace_keys(pf.negate_values(pf.convert_mmr_to_dict(m.variables.PIPE_H2_ZB_INL.flow_forward_out)),
                                                                pf.convert_mmr_to_dict(m.variables.PIPE_H2_ZB_INL.flow_reverse_in),
                                                                name=['PIPE_H2_ZB_INL', 'PIPE_H2_INL_ZB'])

        ##### BALANCE + ENS
        h2_balance = convert(m.prod.INLAND.h2_balanced.BALANCE)
        h2_ens = {'h2_ens': sum(model[i]['solution']['elements']['INLAND']["variables"]['h2_ens']["values"]) / 1000}
        h2_bal_ens = pf.merge_dictionaries_replace_keys(h2_balance, h2_ens, name=['INLAND BALANCE', 'INLAND Hydrogen NOT SERVED'])
        h2_bal_tables.append(h2_bal_ens) 
        h2_bal_over_time = pf.convert_mmr_to_dict(m.variables.INLAND.h2_balanced.BALANCE)
        h2_ens_over_time = model[i]['solution']['elements']['INLAND']['variables']['h2_ens']['values']

        ##### DEMAND
        h2_demand_ind = {'demand_h2_industry': sum(m.global_parameters.demand_h2_industry.demand_h2_industry) / 1000}
        h2_demand_heat = {'demand_h2_heat': sum(m.global_parameters.demand_h2_heat.demand_h2_heat) / 1000}
        h2_demand_tr = {'demand_h2_transport': sum(m.global_parameters.demand_h2_transport.demand_h2_transport) / 1000}
        h2_demand_tr2 = {'demand_h2_transport2': sum(m.global_parameters.demand_h2_transport2.demand_h2_transport2) / 1000}
        h2_demand = pf.merge_dictionaries_replace_keys(h2_demand_ind, h2_demand_heat, h2_demand_tr, h2_demand_tr2, 
                                                        name=['Hydrogen industry demand', 'Hydrogen heating demand', 'Hydrogen transport demand', 'Hydrogen heavy transport demand'])
        
        h2_demand_tables.append(h2_demand)
        h2_demand_over_time = pf.merge_dictionaries_replace_keys(pf.negate_values(pf.convert_mmr_to_dict(m.global_parameters.demand_h2_industry.demand_h2_industry)),
                                                                pf.negate_values(pf.convert_mmr_to_dict(m.global_parameters.demand_h2_heat.demand_h2_heat)),
                                                                pf.negate_values(pf.convert_mmr_to_dict(m.global_parameters.demand_h2_transport.demand_h2_transport)),
                                                                pf.negate_values(pf.convert_mmr_to_dict(m.global_parameters.demand_h2_transport2.demand_h2_transport2)),
                                                                name=['Hydrogen industry demand', 'Hydrogen heating demand', 'Hydrogen transport demand', 'Hydrogen heavy transport demand'])   
        
    # === AFFICHAGE DES TABLEAUX ===

    print(colored('\n=== Hydrogen Exchange ===', 'black', 'on_red'))
    for t in h2_exch_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Hydrogen exchange [TWh]", zero_print="yes").T.round(2))

    print(colored('\n=== Hydrogen INLAND Balance + Not Served ===', 'black', 'on_red'))
    for t in h2_bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Hydrogen [TWh]", zero_print="yes").T.round(3))

    print(colored('\n=== Hydrogen Demand ===', 'black', 'on_red'))
    for t in h2_demand_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Hydrogen demand [TWh]", zero_print="yes").T.round(2))
        
    if zoom is not None:
        h2_exch_over_time = pf.zoom_with_timestep(h2_exch_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        h2_bal_over_time = pf.zoom_with_timestep(h2_bal_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_demand_over_time = pf.zoom_with_timestep(h2_demand_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_ens_over_time = pf.zoom_with_timestep(h2_ens_over_time, zero_nodes=zero_nodes, zoom=zoom)
    
    plt.figure(figsize=figsize)
    
    for key in h2_exch_over_time.keys():
        plt.plot(h2_exch_over_time[key], label=f'{key}')
    
    
    plt.plot(h2_bal_over_time, label=f'Inland balance', linestyle='--')
    
    plt.plot(h2_ens_over_time, label=f'Inland Hydrogen NOT SERVED')
    
    for key in h2_demand_over_time.keys():
        plt.plot(h2_demand_over_time[key], label=f'{key}')
        
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(h2_demand_over_time[key]), 1), rotation=90)
        else:
            plt.xlabel('Time (hours)')
            
    plt.title('Inland hydrogen balance')
    plt.ylabel('Hydrogen (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
    
#%% NATURAL GAS ZEEBRUGGE BALANCE:    

def ng_zeebrugge_balance(model, ng_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):
    
    prod_tables = [] 
    imp_tables = []
    exp_tables = []
    bal_tables = []

    for i, m in enumerate(model):

        # Production 
        _, prod = node_stat(m, ['ZEEBRUGGE'], variable='ng_produced',all_var='no', zero_node=zero_nodes, show ='no')  
        ng_prod = pf.remove_string(prod,' (ZEEBRUGGE)')
        prod_tables.append(table(ng_prod,show='no')) 
        prod_over_time = pf.convert_mmr_to_dict(ng_obj[i].variables.ZEEBRUGGE.ng_produced)
        
        # Import 
        _, imp = node_stat(m, ['ZEEBRUGGE'], variable='ng_imported', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')
        ng_imp = pf.remove_string(imp,' (ZEEBRUGGE)')
        imp_tables.append(table(ng_imp,show='no'))
        imp_over_time = pf.convert_mmr_to_dict(ng_obj[i].variables.ZEEBRUGGE.ng_imported)
        
        # Export 
        _, exp = node_stat(m, ['ZEEBRUGGE'], variable='ng_exported', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')
        ng_exp = pf.remove_string(exp,' (ZEEBRUGGE)')
        exp_tables.append(table(ng_exp,show='no'))
        exp_over_time = pf.negate_values(pf.convert_mmr_to_dict(ng_obj[i].variables.ZEEBRUGGE.ng_exported))
        
        ##### Balance
        ng_balance = convert(ng_obj[i].prod.ZEEBRUGGE.ng_balanced.BALANCE)  
        ng_balance = pf.merge_dictionaries_replace_keys(ng_balance, name=['ZEEBRUGGE BALANCE' ]) 
        bal_tables.append((ng_balance)) 
        bal_over_time = pf.convert_mmr_to_dict(ng_obj[i].variables.ZEEBRUGGE.ng_balanced.BALANCE)
        

    print(colored('\n=== Natural gas production ===', 'black', 'on_cyan'))
    for t in prod_tables:
        display(t) 
        
    print(colored('\n=== Natural gas Import ===', 'black', 'on_cyan'))
    for t in imp_tables:
        display(t)
        
    print(colored('\n=== Natural gas Export ===', 'black', 'on_cyan'))
    for t in exp_tables:
        display(t)
        
    print(colored('\n=== Natural gas Balance ===', 'black', 'on_cyan'))
    for t in bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Natural gas [TWh]", zero_print="yes").T.round(2))
        
        
    if zoom is not None:
        prod_over_time = pf.zoom_with_timestep(prod_over_time, zero_nodes='yes', zoom=zoom)  
        imp_over_time = pf.zoom_with_timestep(imp_over_time, zero_nodes='yes', zoom=zoom)
        exp_over_time = pf.zoom_with_timestep(exp_over_time, zero_nodes='yes', zoom=zoom)
        bal_over_time = pf.zoom_with_timestep(bal_over_time, zero_nodes='yes', zoom=zoom)
        
    plt.figure(figsize=figsize)
    
    for key in prod_over_time.keys():
        plt.plot(prod_over_time[key], label=f'{key}')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(prod_over_time[key]), 1), rotation=90)
        else:
            plt.xlabel('Time (hours)')
    
    for key in imp_over_time.keys():
        plt.plot(imp_over_time[key], label=f'{key}')
        
    for key in exp_over_time.keys():
        plt.plot(exp_over_time[key], label=f'{key}')
        
    plt.plot(bal_over_time, label=f'Zeebrugge balance', linestyle='--')
    
    
        
    plt.title('Zeebrugge natural gas balance')
    plt.ylabel('Natural gas (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
    
        
#%% NATURAL GAS ZEEBRUGGE HYPEREDGE:  

def ng_zeebrugge_hyperedge(model, ng_obj, zoom = None, figsize = (12, 6), zero_nodes='yes', figsave = None):
    
    # Initialisation des listes de tableaux
    ng_exch_tables = []
    ng_bal_tables = []

    # Boucle pour un ou plusieurs scénarios
    for i, m in enumerate(ng_obj):

        ##### EXCHANGE
        ng_zb_inl = {'flow_forward_in': sum(convert(m.variables.PIPE_NG_ZB_INL.flow_forward_in)) / 1000}
        ng_inl_zb = {'flow_reverse_out': sum(convert(m.variables.PIPE_NG_ZB_INL.flow_reverse_out)) / 1000}
        ng_exchange = pf.merge_dictionaries_replace_keys(ng_zb_inl, ng_inl_zb, name=['PIPE_NG_ZB_INL', 'PIPE_NG_INL_ZB'])
        ng_exch_tables.append(ng_exchange)
        ng_exch_over_time = pf.merge_dictionaries_replace_keys(pf.negate_values(pf.convert_mmr_to_dict(m.variables.PIPE_NG_ZB_INL.flow_forward_in)),
                                                                pf.convert_mmr_to_dict(m.variables.PIPE_NG_ZB_INL.flow_reverse_out),
                                                                name=['PIPE_NG_ZB_INL', 'PIPE_NG_INL_ZB'])

        ##### BALANCE
        ng_balance = convert(m.prod.ZEEBRUGGE.ng_balanced.BALANCE)
        ng_balance = pf.merge_dictionaries_replace_keys(ng_balance, name=['ZEEBRUGGE BALANCE'])
        ng_bal_tables.append(ng_balance)
        ng_bal_over_time = pf.convert_mmr_to_dict(m.variables.ZEEBRUGGE.ng_balanced.BALANCE)
        

    # === AFFICHAGE DES TABLEAUX ===

    print(colored('\n=== Natural gas Exchange ===', 'black', 'on_cyan'))
    for t in ng_exch_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Natural gas exchange [TWh]", zero_print="yes").T.round(2))

    print(colored('\n=== Natural gas Balance ===', 'black', 'on_cyan'))
    for t in ng_bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Natural gas [TWh]", zero_print="yes").T.round(2))

    if zoom is not None:
        ng_exch_over_time = pf.zoom_with_timestep(ng_exch_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        ng_bal_over_time = pf.zoom_with_timestep(ng_bal_over_time, zero_nodes=zero_nodes, zoom=zoom)
        
    plt.figure(figsize=figsize)
    
    for key in ng_exch_over_time.keys():
        plt.plot(ng_exch_over_time[key], label=f'{key}')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(ng_exch_over_time[key]), 1), rotation=90)
        else:
            plt.xlabel('Time (hours)')
            
    plt.plot(ng_bal_over_time, label=f'Zeebrugge balance', linestyle='--')
    
    plt.title('Zeebrugge natural gas balance')
    plt.ylabel('Natural gas (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
    

#%% NATURAL GAS INLAND BALANCE:

def ng_inland_balance(model, ng_obj, zoom= 'week', figsize=(12, 5), zero_nodes='yes', figsave = None):
    
    prod_tables = []
    cons_tables = []
    imp_tables = []
    exp_tables = []
    flex_tables_storage = []
    bal_tables = []


    for i, m in enumerate(model):

        # Production 
        _, prod = node_stat(m, ['INLAND'], variable='ng_produced',all_var='no', zero_node=zero_nodes, show ='no')  
        ng_prod = pf.remove_string(prod,' (INLAND)')
        prod_tables.append(table(ng_prod,show='no'))
        prod_over_time = pf.convert_mmr_to_dict(ng_obj[i].variables.INLAND.ng_produced)

        # Consommation
        _, cons = node_stat(m, ['INLAND'], variable='ng_consumed', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')  
        ng_cons = pf.remove_string(cons,' (INLAND)')
        cons_tables.append(table(ng_cons,show='no'))  
        cons_over_time = pf.negate_values(pf.convert_mmr_to_dict(ng_obj[i].variables.INLAND.ng_consumed))

        # Storage (charged / discharged)
        _, storage = node_stat(m, ['INLAND'], variable=['ng_charged','ng_discharged'], all_var='no', zero_node=zero_nodes, show ='no')
        ng_storage = pf.remove_string(storage,' (INLAND)')  
        flex_tables_storage.append(table(ng_storage,show='no'))
        ng_charged_over_time = pf.negate_values(pf.convert_mmr_to_dict(ng_obj[i].variables.INLAND.ng_charged))
        ng_discharged_over_time = pf.convert_mmr_to_dict(ng_obj[i].variables.INLAND.ng_discharged)
        
        # Import 
        _, imp = node_stat(m, ['INLAND'], variable='ng_imported', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')
        ng_imp = pf.remove_string(imp,' (INLAND)')  
        imp_tables.append(table(ng_imp,show='no'))
        ng_imp_over_time = pf.convert_mmr_to_dict(ng_obj[i].variables.INLAND.ng_imported)
        
        # Export 
        _, exp = node_stat(m, ['INLAND'], variable='ng_exported', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes')
        ng_exp = pf.remove_string(exp,' (INLAND)')  
        exp_tables.append(table(ng_exp,show='no'))
        ng_exp_over_time = pf.negate_values(pf.convert_mmr_to_dict(ng_obj[i].variables.INLAND.ng_exported))
        
        ##### Balance
        ng_balance = convert(ng_obj[i].prod.INLAND.ng_balanced.BALANCE)  
        ng_balance = pf.merge_dictionaries_replace_keys(ng_balance, name=['INLAND BALANCE' ]) 
        bal_tables.append((ng_balance)) 
        ng_balance_over_time = pf.convert_mmr_to_dict(ng_obj[i].variables.INLAND.ng_balanced.BALANCE)


    print(colored('\n=== Natural gas production ===', 'black', 'on_red'))
    for t in prod_tables:
        display(t)

    print(colored('\n=== Natural gas consumption ===', 'black', 'on_red'))
    for t in cons_tables:
        display(t)

    print(colored('\n=== Storage charged/discharged ===', 'black', 'on_red'))
    for t in flex_tables_storage:
        display(t)
        
    print(colored('\n=== Natural gas Import ===', 'black', 'on_red'))
    for t in imp_tables:
        display(t)
        
    print(colored('\n=== Natural gas Export ===', 'black', 'on_red'))
    for t in exp_tables:
        display(t)
        
    print(colored('\n=== Natural gas Balance ===', 'black', 'on_red'))
    for t in bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Natural gas [TWh]", zero_print="yes").T.round(2))
        
        
    if zoom is not None:
        prod_over_time = pf.zoom_with_timestep(prod_over_time, zero_nodes='yes', zoom=zoom)  
        cons_over_time = pf.zoom_with_timestep(cons_over_time, zero_nodes='yes', zoom=zoom)
        ng_charged_over_time = pf.zoom_with_timestep(ng_charged_over_time, zero_nodes='yes', zoom=zoom)
        ng_discharged_over_time = pf.zoom_with_timestep(ng_discharged_over_time, zero_nodes='yes', zoom=zoom)
        ng_imp_over_time = pf.zoom_with_timestep(ng_imp_over_time, zero_nodes='yes', zoom=zoom)
        ng_exp_over_time = pf.zoom_with_timestep(ng_exp_over_time, zero_nodes='yes', zoom=zoom)
        ng_balance_over_time = pf.zoom_with_timestep(ng_balance_over_time, zero_nodes='yes', zoom=zoom)
        
    plt.figure(figsize=figsize)
    
    for key in prod_over_time.keys():
        plt.plot(prod_over_time[key], label=f'{key}')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(prod_over_time[key]), 1), rotation=90)
        else:
            plt.xlabel('Time (hours)')
            
    for key in cons_over_time.keys():
        plt.plot(cons_over_time[key], label=f'{key}')
        
    for key in ng_charged_over_time.keys():
        plt.plot(ng_charged_over_time[key], label=f'Battery charged')
        
    plt.plot(ng_balance_over_time, label=f'Inland balance', linestyle='--')
    
    for key in ng_exp_over_time.keys():
        plt.plot(ng_exp_over_time[key], label=f'{key}')
        
    for key in ng_imp_over_time.keys():
        plt.plot(ng_imp_over_time[key], label=f'{key}')
        
    for key in ng_discharged_over_time.keys():
        plt.plot(ng_discharged_over_time[key], label=f'Battery discharged')
        
    plt.title('Inland natural gas balance')
    plt.ylabel('Natural gas (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
        
        
#%% NATURAL GAS INLAND HYPEREDGE:

def ng_inland_hyperedge(model, ng_obj, zoom= 'week', figsize=(12, 5), zero_nodes='yes', figsave = None):
    
    # Initialisation des listes de tableaux
    ng_exch_tables = []
    ng_bal_tables = []
    ng_demand_tables = []
    ng_ens_tables = []

    # Boucle pour un ou plusieurs scénarios
    for i, m in enumerate(ng_obj):

        ##### EXCHANGE
        ng_zb_inl = {'flow_forward_out': sum(convert(m.variables.PIPE_NG_ZB_INL.flow_forward_out)) / 1000}
        ng_inl_zb = {'flow_reverse_in': sum(convert(m.variables.PIPE_NG_ZB_INL.flow_reverse_in)) / 1000}
        ng_exchange = pf.merge_dictionaries_replace_keys(ng_zb_inl, ng_inl_zb, name=['PIPE_NG_ZB_INL', 'PIPE_NG_INL_ZB'])
        ng_exch_tables.append(ng_exchange)
        ng_exch_over_time = pf.merge_dictionaries_replace_keys(pf.convert_mmr_to_dict(m.variables.PIPE_NG_ZB_INL.flow_forward_out),
                                                                pf.negate_values(pf.convert_mmr_to_dict(m.variables.PIPE_NG_ZB_INL.flow_reverse_in)),
                                                                name=['PIPE_NG_ZB_INL', 'PIPE_NG_INL_ZB'])

        ##### BALANCE + ENS
        ng_balance = convert(m.prod.INLAND.ng_balanced.BALANCE)
        ng_ens = {'ng_ens': sum(model[i]['solution']['elements']['INLAND']["variables"]['ng_ens']["values"]) / 1000}
        ng_bal_ens = pf.merge_dictionaries_replace_keys(ng_balance, ng_ens, name=['INLAND BALANCE', 'INLAND Natural Gas NOT SERVED'])
        ng_bal_tables.append(ng_bal_ens)
        ng_bal_over_time = pf.convert_mmr_to_dict(m.variables.INLAND.ng_balanced.BALANCE)
        ng_ens_over_time = model[i]['solution']['elements']['INLAND']['variables']['ng_ens']['values']

        ##### DEMAND
        ng_demand_ind = {'demand_ng_industry': sum(m.global_parameters.demand_ng_industry.demand_ng_industry) / 1000}
        ng_demand_heat = {'demand_ng_heat': sum(m.global_parameters.demand_ng_heat.demand_ng_heat) / 1000}
        try:
            ng_demand_tr = {'demand_ng_transport': sum(m.global_parameters.demand_ng_transport.demand_ng_transport) / 1000}
            ng_demand_tr2 = {'demand_ng_transport2': sum(m.global_parameters.demand_ng_transport2.demand_ng_transport2) / 1000}
            ng_demand = pf.merge_dictionaries_replace_keys(ng_demand_ind, ng_demand_heat, ng_demand_tr, ng_demand_tr2, 
                                                        name=['Natural gas industry demand', 'Natural gas heating demand', 'Natural gas transport demand', 'Natural gas heavy transport demand'])
        except: 
            ng_demand = pf.merge_dictionaries_replace_keys(ng_demand_ind, ng_demand_heat, 
                                                        name=['Natural gas industry demand', 'Natural gas heating demand'])
        ng_demand_tables.append(ng_demand)
        ng_demand_over_time = pf.merge_dictionaries_replace_keys(pf.negate_values(pf.convert_mmr_to_dict(m.global_parameters.demand_ng_industry.demand_ng_industry)),
                                                                pf.negate_values(pf.convert_mmr_to_dict(m.global_parameters.demand_ng_heat.demand_ng_heat)),
                                                                pf.negate_values(pf.convert_mmr_to_dict(m.global_parameters.demand_ng_transport.demand_ng_transport)),
                                                                pf.negate_values(pf.convert_mmr_to_dict(m.global_parameters.demand_ng_transport2.demand_ng_transport2)),
                                                                name=['Natural gas industry demand', 'Natural gas heating demand', 'Natural gas transport demand', 'Natural gas heavy transport demand'])
        

    # === AFFICHAGE DES TABLEAUX ===

    print(colored('\n=== Natural Gas Exchange ===', 'black', 'on_red'))
    for t in ng_exch_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Natural gas exchange [TWh]", zero_print="yes").T.round(2))

    print(colored('\n=== Natural Gas Balance + Not Served ===', 'black', 'on_red'))
    for t in ng_bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Natural gas [TWh]", zero_print="yes").T.round(3))

    print(colored('\n=== Natural Gas Demand ===', 'black', 'on_red'))
    for t in ng_demand_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Natural gas demand [TWh]", zero_print="yes").T.round(2))
        
    if zoom is not None:
        ng_exch_over_time = pf.zoom_with_timestep(ng_exch_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        ng_bal_over_time = pf.zoom_with_timestep(ng_bal_over_time, zero_nodes=zero_nodes, zoom=zoom)
        ng_demand_over_time = pf.zoom_with_timestep(ng_demand_over_time, zero_nodes=zero_nodes, zoom=zoom)
        ng_ens_over_time = pf.zoom_with_timestep(ng_ens_over_time, zero_nodes=zero_nodes, zoom=zoom)
        
    plt.figure(figsize=figsize)
    
    for key in ng_exch_over_time.keys():
        plt.plot(ng_exch_over_time[key], label=f'{key}')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(ng_exch_over_time[key]), 1), rotation=90)
        else:
            plt.xlabel('Time (hours)')
        
    plt.plot(ng_bal_over_time, label=f'Inland balance', linestyle='--')
    
    plt.plot(ng_ens_over_time, label=f'Inland Natural Gas NOT SERVED')
    
    for key in ng_demand_over_time.keys():
        plt.plot(ng_demand_over_time[key], label=f'{key}')
        
    plt.title('Inland natural gas balance')
    plt.ylabel('Natural gas (GWh)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()


#%% CARBON DIOXIDE ZEEBRUGGE BALANCE:

def co2_zeebrugge_balance(model, co2_obj, zoom= 'week', figsize=(12, 5), zero_nodes='yes', figsave = None):
    
    capt_tables = []
    cons_tables = []  
    bal_tables = []

    for i, m in enumerate(model):

        # CO2 Capture 
        _, capt = node_stat(m, ['ZEEBRUGGE'], variable='co2_captured',all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes', type_node='kton')  
        co2_capt = pf.remove_string(capt,' (ZEEBRUGGE)')
        capt_tables.append(table(co2_capt,show='no'))
        capt_over_time = pf.convert_mmr_to_dict(co2_obj[i].variables.ZEEBRUGGE.co2_captured)

        # CO2 Consumption
        _, cons = node_stat(m, ['ZEEBRUGGE'], variable='co2_consumed', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes', type_node='kton')  
        co2_cons = pf.remove_string(cons,' (ZEEBRUGGE)')
        cons_tables.append(table(co2_cons,show='no'))  
        cons_over_time = pf.negate_values(pf.convert_mmr_to_dict(co2_obj[i].variables.ZEEBRUGGE.co2_consumed))
        
        # Balance
        co2_balance = convert(co2_obj[i].prod.ZEEBRUGGE.co2_balanced.BALANCE)
        co2_balance = pf.merge_dictionaries_replace_keys(co2_balance, name=['ZEEBRUGGE BALANCE'])
        bal_tables.append(co2_balance)
        bal_over_time = pf.convert_mmr_to_dict(co2_obj[i].variables.ZEEBRUGGE.co2_balanced.BALANCE)

    print(colored('\n=== Carbon dioxide captured ===', 'black', 'on_cyan'))
    for t in capt_tables:
        display(t)

    print(colored('\n=== Carbon dioxide consumption ===', 'black', 'on_cyan'))
    for t in cons_tables:
        display(t)
        
    print(colored('\n=== Carbon dioxide Balance ===', 'black', 'on_cyan'))
    for t in bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Carbon dioxide [Mton]", zero_print="yes").T.round(2))
        
    if zoom is not None:
        capt_over_time = pf.zoom_with_timestep(capt_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        cons_over_time = pf.zoom_with_timestep(cons_over_time, zero_nodes=zero_nodes, zoom=zoom)
        bal_over_time = pf.zoom_with_timestep(bal_over_time, zero_nodes=zero_nodes, zoom=zoom)
        
    plt.figure(figsize=figsize)
    for key in capt_over_time.keys():
        plt.plot(capt_over_time[key], label=f'{key}')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(capt_over_time[key]), 1), rotation=90)
        else:
            plt.xlabel('Time (hours)')
            
    for key in cons_over_time.keys():
        plt.plot(cons_over_time[key], label=f'{key}')
        
    plt.plot(bal_over_time, label=f'Zeebrugge balance', linestyle='--')
    
    plt.title('Zeebrugge carbon dioxide balance')
    plt.ylabel('Carbon dioxide (kton)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    plt.tight_layout()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
        
        
#%% CARBON DIOXIDE ZEEBRUGGE HYPEREDGE:

def co2_zeebrugge_hyperedge(model, co2_obj, zoom= 'week', figsize=(12, 5), zero_nodes='yes', figsave = None):
    
    # Initialisation de la liste de tableaux
    co2_bal_tables = []

    # Boucle pour un ou plusieurs scénarios
    for i, m in enumerate(co2_obj):

        ##### BALANCE
        co2_balance = convert(m.prod.ZEEBRUGGE.co2_balanced.BALANCE)
        co2_balance = pf.merge_dictionaries_replace_keys(co2_balance, name=['ZEEBRUGGE BALANCE'])
        co2_bal_tables.append(co2_balance)
        co2_bal_over_time = pf.convert_mmr_to_dict(m.variables.ZEEBRUGGE.co2_balanced.BALANCE)

    # === AFFICHAGE DES TABLEAUX ===

    print(colored('\n=== CO2 Balance ===', 'black', 'on_cyan'))
    for t in co2_bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Carbon dioxide [Mton]", zero_print="yes").T.round(2))


    if zoom is not None:
        co2_bal_over_time = pf.zoom_with_timestep(co2_bal_over_time, zero_nodes=zero_nodes, zoom=zoom)
        
    plt.figure(figsize=figsize)
    
    plt.plot(co2_bal_over_time, label=f'Carbon dioxide balance')
    if zoom is not None:
        plt.xlabel(f'Time ({zoom})')
        plt.xticks(np.arange(0, len(co2_bal_over_time), 1), rotation=90)
    else:
        plt.xlabel('Time (hours)')
        
    plt.title('Zeebrugge carbon dioxide balance')
    plt.ylabel('Carbon dioxide (kton)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    plt.tight_layout()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()

#%% CARBON DIOXIDE INLAND BALANCE: 

def co2_inland_balance(model, co2_obj, zoom= 'week', figsize=(12, 5), zero_nodes='yes', figsave = None):
    
    prod_tables = []
    capt_tables = []
    cons_tables = [] 
    flex_tables_storage = []
    exp_tables = []
    released_tables = []
    bal_tables = []

    for i, m in enumerate(model):
        
        # CO2 production
        _, prod = node_stat(m, ['INLAND'], variable='co2_produced',all_var='no', zero_node=zero_nodes, show ='no', type_node='kton')  
        co2_prod = pf.remove_string(prod,' (INLAND)')
        prod_tables.append(table(co2_prod,show='no'))
        prod_over_time = pf.convert_mmr_to_dict(co2_obj[i].variables.INLAND.co2_produced)

        # CO2 Capture 
        _, capt = node_stat(m, ['INLAND'], variable='co2_captured',all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'no', type_node='kton')  
        co2_capt = pf.remove_string(capt,' (INLAND)')
        capt_tables.append(table(co2_capt,show='no'))
        capt_over_time = pf.convert_mmr_to_dict(co2_obj[i].variables.INLAND.co2_captured)

        # CO2 Consumption
        _, cons = node_stat(m, ['INLAND'], variable='co2_consumed', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes', type_node='kton')  
        co2_cons = pf.remove_string(cons,' (INLAND)')
        cons_tables.append(table(co2_cons,show='no'))  
        cons_over_time = pf.negate_values(pf.convert_mmr_to_dict(co2_obj[i].variables.INLAND.co2_consumed))
        
        # Storage (charged / discharged)
        _, storage = node_stat(m, ['INLAND'], variable=['co2_charged','co2_discharged'], all_var='no', zero_node=zero_nodes, show ='no', type_node='kton')
        co2_storage = pf.remove_string(storage,' (INLAND)')  
        flex_tables_storage.append(table(co2_storage,show='no'))
        co2_charged_over_time = pf.negate_values(pf.convert_mmr_to_dict(co2_obj[i].variables.INLAND.co2_charged))
        co2_discharged_over_time = pf.convert_mmr_to_dict(co2_obj[i].variables.INLAND.co2_discharged)
        
        # Export 
        _, exp = node_stat(m, ['INLAND'], variable='co2_exported', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes', type_node='kton')
        co2_exp = pf.remove_string(exp,' (INLAND)')  
        exp_tables.append(table(co2_exp,show='no'))
        co2_exp_over_time = pf.negate_values(pf.convert_mmr_to_dict(co2_obj[i].variables.INLAND.co2_exported))
        
        # Released 
        _, released = node_stat(m, ['INLAND'], variable='co2_released', all_var='no', zero_node=zero_nodes, show ='no', just_prod = 'yes', type_node='kton')
        co2_released = pf.remove_string(released,' (INLAND)')  
        released_tables.append(table(co2_released,show='no'))
        co2_released_over_time = pf.negate_values(pf.convert_mmr_to_dict(co2_obj[i].variables.INLAND.co2_released))
        
        print(colored('\n=== total_co2_emitted ===', 'black', 'on_red')) 
        total_co2_emitted = m['solution']['elements']['INLAND']["variables"]["total_co2_emitted"]["values"][0]
        print(f'Total CO2 Emitted: {total_co2_emitted:.2f} kton')
        
        # Balance
        co2_balance = convert(co2_obj[i].prod.INLAND.co2_balanced.BALANCE)  
        co2_balance = pf.merge_dictionaries_replace_keys(co2_balance, name=['INLAND BALANCE' ]) 
        bal_tables.append((co2_balance)) 
        bal_over_time = pf.convert_mmr_to_dict(co2_obj[i].variables.INLAND.co2_balanced.BALANCE)


    print(colored('\n=== Carbon dioxide production ===', 'black', 'on_red'))
    for t in prod_tables:
        display(t)

    print(colored('\n=== Carbon dioxide captured ===', 'black', 'on_red'))
    for t in capt_tables:
        display(t)

    print(colored('\n=== Carbon dioxide consumption ===', 'black', 'on_red'))
    for t in cons_tables:
        display(t)

    print(colored('\n=== Storage charged/discharged ===', 'black', 'on_red'))
    for t in flex_tables_storage:
        display(t)
        
    print(colored('\n=== Carbon dioxide Export ===', 'black', 'on_red'))
    for t in exp_tables:
        display(t)
        
    print(colored('\n=== Carbon dioxide Released ===', 'black', 'on_red'))
    for t in released_tables:
        display(t)
        
    print(colored('\n=== Carbon dioxide Balance ===', 'black', 'on_red'))
    for t in bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Carbon dioxide [kton]", zero_print="yes").T.round(2))
        
    if zoom is not None:
        capt_over_time = pf.zoom_with_timestep(capt_over_time, zero_nodes='yes', zoom=zoom)  
        cons_over_time = pf.zoom_with_timestep(cons_over_time, zero_nodes='yes', zoom=zoom)
        co2_charged_over_time = pf.zoom_with_timestep(co2_charged_over_time, zero_nodes='yes', zoom=zoom)
        co2_discharged_over_time = pf.zoom_with_timestep(co2_discharged_over_time, zero_nodes='yes', zoom=zoom)
        co2_exp_over_time = pf.zoom_with_timestep(co2_exp_over_time, zero_nodes='yes', zoom=zoom)
        co2_released_over_time = pf.zoom_with_timestep(co2_released_over_time, zero_nodes='yes', zoom=zoom)
        bal_over_time = pf.zoom_with_timestep(bal_over_time, zero_nodes='yes', zoom=zoom)
        
    plt.figure(figsize=figsize)
    
    for key in capt_over_time.keys():
        plt.plot(capt_over_time[key], label=f'{key}')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(capt_over_time[key]), 1), rotation=90)
        else:
            plt.xlabel('Time (hours)')
    
    for key in cons_over_time.keys():
        plt.plot(cons_over_time[key], label=f'{key}')
    
    for key in co2_charged_over_time.keys():
        plt.plot(co2_charged_over_time[key], label=f'Battery charged')
        
    plt.plot(bal_over_time, label=f'Inland balance', linestyle='--')
    
    for key in co2_exp_over_time.keys():
        plt.plot(co2_exp_over_time[key], label=f'{key}')
        
    for key in co2_released_over_time.keys():
        plt.plot(co2_released_over_time[key], label=f'{key}')
        
    for key in co2_discharged_over_time.keys():
        plt.plot(co2_discharged_over_time[key], label=f'Battery discharged')
        
    plt.title('Inland carbon dioxide balance')
    plt.ylabel('Carbon dioxide (kton)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    plt.tight_layout()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
        
        
#%% CARBON DIOXIDE INLAND HYPEREDGE:

def co2_inland_hyperedge(model, co2_obj, zoom= 'week', figsize=(12, 5)):
    
    # Initialisation des listes de tableaux
    co2_bal_tables = []
    co2_quota_tables = []

    # Boucle pour un ou plusieurs scénarios
    for i, d in enumerate(co2_obj):

        ##### BALANCE + CAPTURE
        co2_emitted_inl = {'total_co2_emitted': sum(model[i]['solution']['elements']['INLAND']["variables"]['total_co2_emitted']["values"]) / 1000}
        co2_captured_zee = {'total_co2_captured': sum(model[i]['solution']['elements']['ZEEBRUGGE']["variables"]['total_co2_captured']["values"]) / 1000}
        co2_bal_ens = pf.merge_dictionaries_replace_keys(co2_emitted_inl, co2_captured_zee, name=['INLAND EMISSIONS', 'ZEEBRUGGE CAPTURED'])
        co2_bal_tables.append(co2_bal_ens) 

        ##### QUOTA
        co2_quota = {'co2_quota_emission': d.global_parameters.co2_quota_emission.co2_quota_emission}
        co2_demand = pf.merge_dictionaries_replace_keys(co2_quota, name=['CO2 quota'])
        co2_quota_tables.append(co2_demand)
        

    # === AFFICHAGE DES TABLEAUX ===

    print(colored('\n=== Carbon dioxide balance ===', 'black', 'on_red'))
    for t in co2_bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Carbon dioxide [kton]", zero_print="yes").T.round(3))

    print(colored('\n=== Carbon dioxide quota ===', 'black', 'on_red'))
    for t in co2_quota_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Carbon dioxide quota [kton]", zero_print="yes").T.round(2))


#%% WATER OFFSHORE:

def water_offshore(model, h2o_obj, zoom= 'week', figsize=(12, 5), zero_nodes='yes', figsave = None):
    
    prod_tables = []
    cons_tables = [] 
    flex_tables_storage = [] 
    bal_tables = []

    for i, m in enumerate(model):

        # Production 
        _, prod = node_stat(m, ['OFFSHORE'], variable='h2o_produced', all_var='no', zero_node=zero_nodes, show='no', type_node='kton')  
        h2_prod = pf.remove_string(prod, ' (OFFSHORE)')
        prod_tables.append(table(h2_prod, show='no'))
        prod_over_time = pf.convert_mmr_to_dict(h2o_obj[i].variables.OFFSHORE.h2o_produced)

        # Consumption
        _, cons = node_stat(m, ['OFFSHORE'], variable='h2o_consumed', all_var='no', zero_node=zero_nodes, show='no', just_prod='yes', type_node='kton') 
        h2_cons = pf.remove_string(cons, ' (OFFSHORE)')
        cons_tables.append(table(h2_cons, show='no'))  
        cons_over_time = pf.negate_values(pf.convert_mmr_to_dict(h2o_obj[i].variables.OFFSHORE.h2o_consumed))

        # Storage (charged / discharged)
        _, storage = node_stat(m, ['OFFSHORE'], variable=['h2o_charged', 'h2o_discharged'], all_var='no', zero_node=zero_nodes, show='no', type_node='kton')
        h2_storage = pf.remove_string(storage, ' (OFFSHORE)')  
        flex_tables_storage.append(table(h2_storage, show='no'))  
        h2_charged_over_time = pf.negate_values(pf.convert_mmr_to_dict(h2o_obj[i].variables.OFFSHORE.h2o_charged))
        h2_discharged_over_time = pf.convert_mmr_to_dict(h2o_obj[i].variables.OFFSHORE.h2o_discharged)
        
        # Balance
        h2_balance = convert(h2o_obj[i].prod.OFFSHORE.h2o_balanced.BALANCE)  
        h2_balance = pf.merge_dictionaries_replace_keys(h2_balance, name=['OFFSHORE BALANCE']) 
        bal_tables.append(h2_balance) 
        h2_balance_over_time = pf.convert_mmr_to_dict(h2o_obj[i].variables.OFFSHORE.h2o_balanced.BALANCE)
        
        

    print(colored('\n=== Water production ===', 'black', 'on_green'))
    for t in prod_tables:
        display(t)

    print(colored('\n=== Water consumption ===', 'black', 'on_green'))
    for t in cons_tables:
        display(t)

    print(colored('\n=== Water storage charged/discharged ===', 'black', 'on_green'))
    for t in flex_tables_storage:
        display(t) 
        
    print(colored('\n=== Water Balance ===', 'black', 'on_green'))
    for t in bal_tables:
        v = table(pf.transform_dict_into_table(t, column_name="Water [kton]", zero_print="yes").T.round(2))
        
    if zoom is not None:
        prod_over_time = pf.zoom_with_timestep(prod_over_time, zero_nodes=zero_nodes, zoom=zoom)  
        cons_over_time = pf.zoom_with_timestep(cons_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_charged_over_time = pf.zoom_with_timestep(h2_charged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_discharged_over_time = pf.zoom_with_timestep(h2_discharged_over_time, zero_nodes=zero_nodes, zoom=zoom)
        h2_balance_over_time = pf.zoom_with_timestep(h2_balance_over_time, zero_nodes=zero_nodes, zoom=zoom)
        
    plt.figure(figsize=figsize)
    
    for key in prod_over_time.keys():
        plt.plot(prod_over_time[key], label=f'{key}')
        if zoom is not None:
            plt.xlabel(f'Time ({zoom})')
            plt.xticks(np.arange(0, len(prod_over_time[key]), 1), rotation=90)
        else:
            plt.xlabel('Time (hours)')
            
    for key in cons_over_time.keys():
        plt.plot(cons_over_time[key], label=f'{key}')
        
    for key in h2_charged_over_time.keys():
        plt.plot(h2_charged_over_time[key], label=f'Battery charged')
        
    plt.plot(h2_balance_over_time, label=f'Offshore balance', linestyle='--')
    
    for key in h2_discharged_over_time.keys():
        plt.plot(h2_discharged_over_time[key], label=f'Battery discharged')
        
    plt.title('Offshore water balance')
    plt.ylabel('Water (kton)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    plt.grid()
    plt.tight_layout()
    if figsave is not None:
        plt.savefig(figsave, format="pdf", bbox_inches="tight")
    plt.show()
    