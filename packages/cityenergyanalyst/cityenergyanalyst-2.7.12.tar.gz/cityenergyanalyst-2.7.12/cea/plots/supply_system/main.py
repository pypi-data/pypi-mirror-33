"""
This is the dashboard of CEA
"""
from __future__ import division
from __future__ import print_function

import json
import os

import pandas as pd
import numpy as np
import cea.config
import cea.inputlocator
from cea.plots.supply_system.individual_activation_curve import individual_activation_curve
from cea.plots.supply_system.cost_analysis_curve_decentralized import cost_analysis_curve_decentralized
from cea.plots.supply_system.thermal_storage_curve import thermal_storage_activation_curve
from cea.analysis.multicriteria.optimization_post_processing.electricity_imports_exports_script import electricity_import_and_exports
from cea.analysis.multicriteria.optimization_post_processing.energy_mix_based_on_technologies_script import energy_mix_based_on_technologies_script
from cea.analysis.multicriteria.optimization_post_processing.individual_configuration import supply_system_configuration
from cea.plots.thermal_networks.main import Plots as Plots_thermal_network
from cea.technologies.thermal_network.network_layout.main import network_layout
from cea.technologies.thermal_network.thermal_network_matrix import thermal_network_main
from cea.analysis.multicriteria.optimization_post_processing.natural_gas_imports_script import natural_gas_imports
from cea.plots.supply_system.likelihood_chart import likelihood_chart
from cea.analysis.multicriteria.optimization_post_processing.locating_individuals_in_generation_script import locating_individuals_in_generation_script



from cea.plots.supply_system.map_chart import map_chart
from cea.plots.supply_system.pie_chart_import_exports import pie_chart_imports_exports
from cea.plots.supply_system.bar_chart_costs import bar_chart_costs
from cea.optimization.constants import SIZING_MARGIN
from math import ceil

__author__ = "Jimeno A. Fonseca"
__copyright__ = "Copyright 2018, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Jimeno A. Fonseca", "Sreepathi Bhargava Krishna"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "cea@arch.ethz.ch"
__status__ = "Production"


def plots_main(locator, config):
    # local variables
    scenario = config.scenario
    generation = config.plots_supply_system.generation
    individual = config.plots_supply_system.individual
    type_of_network = config.plots_supply_system.network_type
    categories = config.plots_supply_system.categories

    # initialize class
    category = "optimization-detailed"

    if not os.path.exists(locator.get_address_of_individuals_of_a_generation(generation, category)):
        data_address = locating_individuals_in_generation_script(generation, locator)
    else:
        data_address = pd.read_csv(locator.get_address_of_individuals_of_a_generation(generation, category))
    data_address = data_address[data_address['individual_list'] == individual]

    generation_pointer = data_address['generation_number_address'].values[0] # points to the correct file to be referenced from optimization folders
    individual_pointer = data_address['individual_number_address'].values[0]
    individual_pointer = 'ind' + str(individual_pointer) # updating the individual based on its correct path from the checkpoint

    plots = Plots(locator, individual, generation, individual_pointer, generation_pointer, config, type_of_network, category)

    if "thermal_dispatch_curves" in categories:
        if type_of_network == 'DH':
            plots.individual_heating_dispatch_curve(category)
            plots.individual_heating_storage_dispatch_curve(category)
        if type_of_network == 'DC':
            plots.individual_cooling_dispatch_curve(category)

    if "electrical_dispatch_curves" in categories:
        if type_of_network == 'DH':
            plots.individual_electricity_dispatch_curve_heating(category)
        if type_of_network == 'DC':
            plots.individual_electricity_dispatch_curve_cooling(category)

    if "costs_analysis" in categories:
        plots.bar_total_costs(category)
        if type_of_network == 'DH':
            plots.cost_analysis_heating_decentralized(config, category)
        if type_of_network == 'DC':
            plots.cost_analysis_cooling_decentralized(config, category)

    if "system_sizes" in categories:
        plots.map_location_size_customers_energy_system(type_of_network, category)

    if "supply_mix" in categories:
        plots.pie_energy_supply_mix(category)

    if "imports_exports" in categories:
        plots.pie_import_exports(category)
        plots.impact_in_the_local_grid(category)

    if "thermal_network" in categories:
        network_name = "gen%s_%s" % (generation, individual)
        network_type = type_of_network
        preprocessing_run_thermal_network(config, locator, network_name, network_type)
        plots = Plots_thermal_network(locator, network_type, network_name)
        # create plots
        plots.loss_curve(category)
        plots.loss_curve_relative(category)
        plots.supply_return_ambient_curve(category)
        plots.loss_duration_curve(category)
        plots.energy_loss_bar_plot(category)
        plots.energy_loss_bar_substation_plot(category)
        plots.heat_network_plot(category)
        plots.pressure_network_plot(category)
        plots.network_layout_plot(category)
        print("thermal network plots successfully saved in plots folder of scenario: ", config.scenario)

    return

def preprocessing_run_thermal_network(config, locator, output_name_network, output_type_network):

    # configure thermal network (reduced simulation and create diagram of new network.
    network_name = output_name_network
    network_type = output_type_network  # set to either 'DH' or 'DC'
    file_type = 'shp'  # set to csv or shp
    set_diameter = config.thermal_network.set_diameter  # boolean
    config.thermal_network.use_representative_week_per_month = False

    if network_type == 'DC':
        substation_cooling_systems = ['ahu', 'aru', 'scu', 'data',
                                      're']  # list of cooling demand types supplied by network to substation
        substation_heating_systems = []
    else:
        substation_cooling_systems = []
        substation_heating_systems = ['ahu', 'aru', 'shu',
                                      'ww']  # list of heating demand types supplied by network to substation

    # combine into a dictionary to pass fewer arguments
    substation_systems = {'heating': substation_heating_systems, 'cooling': substation_cooling_systems}
    thermal_network_main(locator, network_type, network_name, file_type, set_diameter, config, substation_systems)

class Plots():

    def __init__(self, locator, individual, generation, individual_pointer, generation_pointer, config, output_type_network, category):
        # local variables
        self.locator = locator
        self.individual = individual
        self.config = config
        self.category = category
        self.generation = generation
        self.individual_pointer = individual_pointer
        self.generation_pointer = generation_pointer
        self.output_type_network = output_type_network
        # fields of loads in the systems of heating, cooling and electricity
        self.analysis_fields_electricity_loads_heating = ['Electr_netw_total_W', "E_HPSew_req_W", "E_HPLake_req_W",
                                                  "E_GHP_req_W",
                                                  "E_BaseBoiler_req_W",
                                                  "E_PeakBoiler_req_W",
                                                  "E_AddBoiler_req_W",
                                                  "E_aux_storage_solar_and_heat_recovery_req_W",
                                                  "E_total_req_W"]
        self.analysis_fields_electricity_loads_cooling = ["E_total_req_W"]
        self.analysis_fields_heating_loads = ['Q_DHNf_W']
        self.analysis_fields_cooling_loads = ['Q_total_cooling_W']
        self.analysis_fields_heating = ["Q_PVT_to_directload_W",
                                        "Q_SC_ET_to_directload_W",
                                        "Q_SC_FP_to_directload_W",
                                        "Q_server_to_directload_W",
                                        "Q_compair_to_directload_W",
                                        "Q_from_storage_used_W",
                                        "Q_HPLake_W",
                                        "Q_HPSew_W",
                                        "Q_GHP_W",
                                        "Q_CHP_W",
                                        "Q_Furnace_W",
                                        "Q_BaseBoiler_W",
                                        "Q_PeakBoiler_W",
                                        "Q_AddBoiler_W"]
        self.analysis_fields_heating_storage_charging = ["Q_PVT_to_storage_W",
                                                         "Q_SC_ET_to_storage_W",
                                                         "Q_SC_FP_to_storage_W",
                                                         "Q_server_to_storage_W"]
        self.analysis_fields_cost_cooling_centralized = ["Capex_a_ACH",
                                                   "Capex_a_CCGT",
                                                   "Capex_a_CT",
                                                   "Capex_a_Tank",
                                                   "Capex_a_VCC",
                                                   "Capex_a_VCC_backup",
                                                   "Capex_a_pump",
                                                   "Opex_var_ACH",
                                                   "Opex_var_CCGT",
                                                   "Opex_var_CT",
                                                   "Opex_var_Lake",
                                                   "Opex_var_VCC",
                                                   "Opex_var_VCC_backup",
                                                   "Opex_var_pump",
                                                   "Electricity_Costs"]
        self.analysis_fields_heating_storage_discharging = ["Q_from_storage_used_W"]
        self.analysis_fields_heating_storage_status = ["Q_storage_content_W"]
        self.analysis_fields_cooling = ['Q_from_Lake_W',
                                        'Q_from_VCC_W',
                                        'Q_from_ACH_W',
                                        'Q_from_VCC_backup_W',
                                        'Q_from_storage_tank_W']
        self.analysis_fields_electricity_heating = ["E_PV_to_directload_W",
                                            "E_PVT_to_directload_W",
                                            "E_CHP_to_directload_W",
                                            "E_Furnace_to_directload_W",
                                            "E_PV_to_grid_W",
                                            "E_PVT_to_grid_W",
                                            "E_CHP_to_grid_W",
                                            "E_Furnace_to_grid_W",
                                                    "E_from_grid_W"]
        self.analysis_fields_electricity_cooling = ["E_CHP_to_directload_W",
                                                    "E_PV_to_directload_W",
                                                    "E_from_grid_W",
                                                    "E_CHP_to_grid_W",
                                                    "E_PV_to_grid_W"]
        self.renewable_sources_fields = ['Base_boiler_BG_capacity_W', 'CHP_BG_capacity_W',
                                         'Furnace_dry_capacity_W', 'Furnace_wet_capacity_W',
                                         'GHP_capacity_W', 'HP_Lake_capacity_W', 'HP_Sewage_capacity_W',
                                         'PVT_capacity_W', 'PV_capacity_W', 'Peak_boiler_BG_capacity_W',
                                         'SC_ET_capacity_W', 'SC_FP_capacity_W',
                                         'Disconnected_Boiler_BG_capacity_W',
                                         'Disconnected_FC_capacity_W',
                                         'Disconnected_GHP_capacity_W']
        self.cost_analysis_cooling_fields = ['Capex_a_ACH', 'Capex_a_CCGT', 'Capex_a_CT', 'Capex_a_Tank', 'Capex_a_VCC',
                                             'Capex_a_VCC_backup', 'Capex_pump', 'Opex_fixed_ACH', 'Opex_fixed_CCGT',
                                             'Opex_fixed_CT', 'Opex_fixed_Tank', 'Opex_fixed_VCC',
                                             'Opex_fixed_VCC_backup', 'Opex_fixed_pump',
                                             'Opex_var_Lake', 'Opex_var_VCC', 'Opex_var_ACH',
                                             'Opex_var_VCC_backup', 'Opex_var_CT', 'Opex_var_CCGT']

        self.data_processed = self.preprocessing_generations_data()
        self.data_processed_individual = self.preprocessing_individual_data(self.locator,
                                                                            self.data_processed['generation'],
                                                                            self.individual, self.generation,
                                                                            self.individual_pointer, self.generation_pointer,
                                                                            self.config)
        self.data_processed_cost_centralized = self.preprocessing_individual_data_cost_centralized(self.locator,
                                                                                                   self.data_processed['generation'],
                                                                                                   self.individual, self.generation,
                                                                                                   self.individual_pointer, self.generation_pointer,
                                                                                                   self.config, self.category)
        self.data_processed_cost_decentralized = self.preprocessing_individual_data_decentralized(self.locator,
                                                                                                  self.data_processed[
                                                                                                      'generation'],
                                                                                                  self.individual, self.generation,
                                                                                                  self.individual_pointer, self.generation_pointer,
                                                                                                  self.config, self.category)
        self.data_processed_imports_exports = self.preprocessing_import_exports(self.locator, self.generation,
                                                                                self.individual, self.generation_pointer, self.individual_pointer, config)
        self.data_energy_mix = self.preprocessing_energy_mix(self.locator, self.generation, self.individual, self.generation_pointer, self.individual_pointer, config)



    def preprocessing_generations_data(self):

        with open(self.locator.get_optimization_checkpoint(self.generation), "rb") as fp:
            data = json.load(fp)
        # get lists of data for performance values of the population
        costs_Mio = [round(objectives[0] / 1000000, 2) for objectives in
                     data['population_fitness']]  # convert to millions
        emissions_ton = [round(objectives[1] / 1000000, 2) for objectives in
                         data['population_fitness']]  # convert to tons x 10^3
        prim_energy_GJ = [round(objectives[2] / 1000000, 2) for objectives in
                          data['population_fitness']]  # convert to gigajoules x 10^3
        individual_names = ['ind' + str(i) for i in range(len(costs_Mio))]

        df_population = pd.DataFrame({'Name': individual_names, 'costs_Mio': costs_Mio,
                                      'emissions_ton': emissions_ton, 'prim_energy_GJ': prim_energy_GJ
                                      }).set_index("Name")

        individual_barcode = [[str(ind) if type(ind) == float else str(ind) for ind in
                               individual] for individual in data['population']]
        def_individual_barcode = pd.DataFrame({'Name': individual_names,
                                               'individual_barcode': individual_barcode}).set_index("Name")

        # get lists of data for performance values of the population (hall_of_fame
        costs_Mio_HOF = [round(objectives[0] / 1000000, 2) for objectives in
                         data['halloffame_fitness']]  # convert to millions
        emissions_ton_HOF = [round(objectives[1] / 1000000, 2) for objectives in
                             data['halloffame_fitness']]  # convert to tons x 10^3
        prim_energy_GJ_HOF = [round(objectives[2] / 1000000, 2) for objectives in
                              data['halloffame_fitness']]  # convert to gigajoules x 10^3
        individual_names_HOF = ['ind' + str(i) for i in range(len(costs_Mio_HOF))]
        df_halloffame = pd.DataFrame({'Name': individual_names_HOF, 'costs_Mio': costs_Mio_HOF,
                                      'emissions_ton': emissions_ton_HOF,
                                      'prim_energy_GJ': prim_energy_GJ_HOF}).set_index("Name")

        # get dataframe with capacity installed per individual
        for i, individual in enumerate(individual_names):
            dict_capacities = data['capacities'][i]
            dict_network = data['disconnected_capacities'][i]["network"]
            list_dict_disc_capacities = data['disconnected_capacities'][i]["disconnected_capacity"]
            for building, dict_disconnected in enumerate(list_dict_disc_capacities):
                if building == 0:
                    df_disc_capacities = pd.DataFrame(dict_disconnected, index=[dict_disconnected['building_name']])
                else:
                    df_disc_capacities = df_disc_capacities.append(
                        pd.DataFrame(dict_disconnected, index=[dict_disconnected['building_name']]))
            df_disc_capacities = df_disc_capacities.set_index('building_name')
            dict_disc_capacities = df_disc_capacities.sum(axis=0).to_dict()  # series with sum of capacities

            if i == 0:
                df_disc_capacities_final = pd.DataFrame(dict_disc_capacities, index=[individual])
                df_capacities = pd.DataFrame(dict_capacities, index=[individual])
                df_network = pd.DataFrame({"network": dict_network}, index=[individual])
            else:
                df_capacities = df_capacities.append(pd.DataFrame(dict_capacities, index=[individual]))
                df_network = df_network.append(pd.DataFrame({"network": dict_network}, index=[individual]))
                df_disc_capacities_final = df_disc_capacities_final.append(
                    pd.DataFrame(dict_disc_capacities, index=[individual]))

        data_processed = {'population': df_population, 'halloffame': df_halloffame, 'capacities_W': df_capacities,
             'disconnected_capacities_W': df_disc_capacities_final, 'network': df_network,
             'spread': data['spread'], 'euclidean_distance': data['euclidean_distance'],
             'individual_barcode': def_individual_barcode}

        return {'generation':data_processed}

    def preprocessing_individual_data(self, locator, data_raw, individual, generation, individual_pointer, generation_pointer, config):

        # get netwoork name
        string_network = data_raw['network'].loc[individual].values[0]
        total_demand = pd.read_csv(locator.get_total_demand())
        building_names = total_demand.Name.values

        # get data about hourly demands in these buildings
        building_demands_df = pd.read_csv(locator.get_optimization_network_results_summary(string_network)).set_index(
            "DATE")

        # get data about the dispatch patterns of these buildings
        individual_barcode_list = data_raw['individual_barcode'].loc[individual].values[0]

        # The current structure of CEA has the following columns saved, in future, this will be slightly changed and
        # correspondingly these columns_of_saved_files needs to be changed
        columns_of_saved_files = ['CHP/Furnace', 'CHP/Furnace Share', 'Base Boiler',
                                  'Base Boiler Share', 'Peak Boiler', 'Peak Boiler Share',
                                  'Heating Lake', 'Heating Lake Share', 'Heating Sewage', 'Heating Sewage Share', 'GHP',
                                  'GHP Share',
                                  'Data Centre', 'Compressed Air', 'PV', 'PV Area Share', 'PVT', 'PVT Area Share', 'SC_ET',
                                  'SC_ET Area Share', 'SC_FP', 'SC_FP Area Share', 'DHN Temperature', 'DHN unit configuration',
                                  'Lake Cooling', 'Lake Cooling Share', 'VCC Cooling', 'VCC Cooling Share',
                                  'Absorption Chiller', 'Absorption Chiller Share', 'Storage', 'Storage Share',
                                  'DCN Temperature', 'DCN unit configuration']
        for i in building_names:  # DHN
            columns_of_saved_files.append(str(i) + ' DHN')

        for i in building_names:  # DCN
            columns_of_saved_files.append(str(i) + ' DCN')


        df_current_individual = pd.DataFrame(np.zeros(shape = (1, len(columns_of_saved_files))), columns=columns_of_saved_files)
        for i, ind in enumerate((columns_of_saved_files)):
            df_current_individual[ind] = individual_barcode_list[i]

        individual_number = int(individual_pointer[-1])
        # get data about the dispatch patterns of these buildings (main units)
        if config.plots_supply_system.network_type == 'DH':
            data_dispatch_path = os.path.join(
                locator.get_optimization_slave_heating_activation_pattern(individual_number, generation_pointer))
            df_heating = pd.read_csv(data_dispatch_path).set_index("DATE")

            data_dispatch_path = os.path.join(
                locator.get_optimization_slave_electricity_activation_pattern_heating(individual_number, generation_pointer))
            df_electricity = pd.read_csv(data_dispatch_path).set_index("DATE")

            # get data about the dispatch patterns of these buildings (storage)
            data_storage_path = os.path.join(
                locator.get_optimization_slave_storage_operation_data(individual_number, generation_pointer))
            df_SO = pd.read_csv(data_storage_path).set_index("DATE")

            # join into one database
            data_processed = df_heating.join(df_electricity).join(df_SO).join(building_demands_df)

        elif config.plots_supply_system.network_type == 'DC':
            data_dispatch_path = os.path.join(
                locator.get_optimization_slave_cooling_activation_pattern(individual_number, generation_pointer))
            df_cooling = pd.read_csv(data_dispatch_path).set_index("DATE")

            data_dispatch_path = os.path.join(
                locator.get_optimization_slave_electricity_activation_pattern_cooling(individual_number, generation_pointer))
            df_electricity = pd.read_csv(data_dispatch_path).set_index("DATE")

            # join into one database
            data_processed = df_cooling.join(building_demands_df).join(df_electricity)

        return data_processed

    def preprocessing_individual_data_cost_centralized(self, locator, data_raw, individual, generation, individual_pointer, generation_pointer, config, category):

        total_demand = pd.read_csv(locator.get_total_demand())
        building_names = total_demand.Name.values

        df_all_generations = pd.read_csv(locator.get_optimization_all_individuals())
        preprocessing_costs = pd.read_csv(locator.get_preprocessing_costs())

        # The current structure of CEA has the following columns saved, in future, this will be slightly changed and
        # correspondingly these columns_of_saved_files needs to be changed
        columns_of_saved_files = ['CHP/Furnace', 'CHP/Furnace Share', 'Base Boiler',
                                  'Base Boiler Share', 'Peak Boiler', 'Peak Boiler Share',
                                  'Heating Lake', 'Heating Lake Share', 'Heating Sewage', 'Heating Sewage Share', 'GHP',
                                  'GHP Share',
                                  'Data Centre', 'Compressed Air', 'PV', 'PV Area Share', 'PVT', 'PVT Area Share', 'SC_ET',
                                  'SC_ET Area Share', 'SC_FP', 'SC_FP Area Share', 'DHN Temperature', 'DHN unit configuration',
                                  'Lake Cooling', 'Lake Cooling Share', 'VCC Cooling', 'VCC Cooling Share',
                                  'Absorption Chiller', 'Absorption Chiller Share', 'Storage', 'Storage Share',
                                  'DCN Temperature', 'DCN unit configuration']
        for i in building_names:  # DHN
            columns_of_saved_files.append(str(i) + ' DHN')

        for i in building_names:  # DCN
            columns_of_saved_files.append(str(i) + ' DCN')

        individual_index = data_raw['individual_barcode'].index.values
        if config.plots_supply_system.network_type == 'DH':
            data_dispatch_path = os.path.join(
                locator.get_optimization_slave_investment_cost_detailed(1, 1))
            df_heating_costs = pd.read_csv(data_dispatch_path)
            column_names = df_heating_costs.columns.values
            column_names = np.append(column_names, ['Opex_HP_Sewage', 'Opex_HP_Lake', 'Opex_GHP', 'Opex_CHP_BG',
                                                    'Opex_CHP_NG', 'Opex_Furnace_wet', 'Opex_Furnace_dry',
                                                    'Opex_BaseBoiler_BG', 'Opex_BaseBoiler_NG', 'Opex_PeakBoiler_BG',
                                                    'Opex_PeakBoiler_NG', 'Opex_BackupBoiler_BG', 'Opex_BackupBoiler_NG',
                                                    'Capex_SC', 'Capex_PVT', 'Capex_Boiler_backup', 'Capex_storage_HEX',
                                                    'Capex_furnace', 'Capex_Boiler', 'Capex_Boiler_peak', 'Capex_Lake', 'Capex_CHP',
                                                    'Capex_Sewage', 'Capex_pump', 'Opex_Total', 'Capex_Total', 'Capex_Boiler_Total',
                                                    'Opex_Boiler_Total', 'Opex_CHP_Total', 'Opex_Furnace_Total', 'Disconnected_costs',
                                                    'Capex_Decentralized', 'Opex_Decentralized', 'Capex_Centralized', 'Opex_Centralized', 'Electricity_Costs', 'Process_Heat_Costs'])

            data_processed = pd.DataFrame(np.zeros([len(data_raw['individual_barcode']), len(column_names)]), columns=column_names)

        elif config.plots_supply_system.network_type == 'DC':
            data_dispatch_path = os.path.join(
                locator.get_optimization_slave_investment_cost_detailed_cooling(1, 1))
            df_cooling_costs = pd.read_csv(data_dispatch_path)
            column_names = df_cooling_costs.columns.values
            column_names = np.append(column_names,
                                     ['Opex_var_ACH', 'Opex_var_CCGT', 'Opex_var_CT', 'Opex_var_Lake', 'Opex_var_VCC',
                                      'Opex_var_VCC_backup', 'Capex_ACH', 'Capex_CCGT', 'Capex_CT', 'Capex_Tank', 'Capex_VCC',
                                      'Capex_VCC_backup', 'Capex_a_pump', 'Opex_Total', 'Capex_Total', 'Opex_var_pump', 'Disconnected_costs',
                                      'Capex_Decentralized', 'Opex_Decentralized', 'Capex_Centralized', 'Opex_Centralized', 'Electricity_Costs', 'Process_Heat_Costs'])

            data_processed = pd.DataFrame(np.zeros([1, len(column_names)]), columns=column_names)


        individual_barcode_list = data_raw['individual_barcode'].loc[individual].values[0]
        df_current_individual = pd.DataFrame(np.zeros(shape = (1, len(columns_of_saved_files))), columns=columns_of_saved_files)
        for i, ind in enumerate((columns_of_saved_files)):
            df_current_individual[ind] = individual_barcode_list[i]

        generation_number = generation_pointer
        individual_number = int(individual_pointer[-1])

        if config.plots_supply_system.network_type == 'DH':
            data_dispatch_path = os.path.join(
                locator.get_optimization_slave_investment_cost_detailed(individual_number, generation_number))
            df_heating_costs = pd.read_csv(data_dispatch_path)

            data_dispatch_path = os.path.join(
                locator.get_optimization_slave_heating_activation_pattern(individual_number, generation_number))
            df_heating = pd.read_csv(data_dispatch_path).set_index("DATE")

            for column_name in df_heating_costs.columns.values:
                data_processed.loc[0][column_name] = df_heating_costs[column_name].values


            data_processed.loc[0]['Opex_HP_Sewage'] = np.sum(df_heating['Opex_var_HP_Sewage'])
            data_processed.loc[0]['Opex_HP_Lake'] = np.sum(df_heating['Opex_var_HP_Lake'])
            data_processed.loc[0]['Opex_GHP'] = np.sum(df_heating['Opex_var_GHP'])
            data_processed.loc[0]['Opex_CHP_BG'] = np.sum(df_heating['Opex_var_CHP_BG'])
            data_processed.loc[0]['Opex_CHP_NG'] = np.sum(df_heating['Opex_var_CHP_NG'])
            data_processed.loc[0]['Opex_Furnace_wet'] = np.sum(df_heating['Opex_var_Furnace_wet'])
            data_processed.loc[0]['Opex_Furnace_dry'] = np.sum(df_heating['Opex_var_Furnace_dry'])
            data_processed.loc[0]['Opex_BaseBoiler_BG'] = np.sum(df_heating['Opex_var_BaseBoiler_BG'])
            data_processed.loc[0]['Opex_BaseBoiler_NG'] = np.sum(df_heating['Opex_var_BaseBoiler_NG'])
            data_processed.loc[0]['Opex_PeakBoiler_BG'] = np.sum(df_heating['Opex_var_PeakBoiler_BG'])
            data_processed.loc[0]['Opex_PeakBoiler_NG'] = np.sum(df_heating['Opex_var_PeakBoiler_NG'])
            data_processed.loc[0]['Opex_BackupBoiler_BG'] = np.sum(df_heating['Opex_var_BackupBoiler_BG'])
            data_processed.loc[0]['Opex_BackupBoiler_NG'] = np.sum(df_heating['Opex_var_BackupBoiler_NG'])


            data_processed.loc[0]['Capex_SC'] = data_processed.loc[0]['Capex_a_SC'] + data_processed.loc[0]['Opex_fixed_SC']
            data_processed.loc[0]['Capex_PVT'] = data_processed.loc[0]['Capex_a_PVT'] + data_processed.loc[0]['Opex_fixed_PVT']
            data_processed.loc[0]['Capex_Boiler_backup'] = data_processed.loc[0]['Capex_a_Boiler_backup']+ data_processed.loc[0]['Opex_fixed_Boiler_backup']
            data_processed.loc[0]['Capex_storage_HEX'] = data_processed.loc[0]['Capex_a_storage_HEX'] + data_processed.loc[0]['Opex_fixed_storage_HEX']
            data_processed.loc[0]['Capex_furnace'] = data_processed.loc[0]['Capex_a_furnace']+ data_processed.loc[0]['Opex_fixed_furnace']
            data_processed.loc[0]['Capex_Boiler'] = data_processed.loc[0]['Capex_a_Boiler'] + data_processed.loc[0]['Opex_fixed_Boiler']
            data_processed.loc[0]['Capex_Boiler_peak'] = data_processed.loc[0]['Capex_a_Boiler_peak']+ data_processed.loc[0]['Opex_fixed_Boiler_peak']
            data_processed.loc[0]['Capex_Lake'] = data_processed.loc[0]['Capex_a_Lake']+ data_processed.loc[0]['Opex_fixed_Lake']
            data_processed.loc[0]['Capex_Sewage'] = data_processed.loc[0]['Capex_a_Sewage'] + data_processed.loc[0]['Opex_fixed_Boiler']
            data_processed.loc[0]['Capex_pump'] = data_processed.loc[0]['Capex_a_pump'] + data_processed.loc[0]['Opex_fixed_pump']
            data_processed.loc[0]['Capex_CHP'] = data_processed.loc[0]['Capex_a_CHP'] + data_processed.loc[0]['Opex_fixed_CHP']
            data_processed.loc[0]['Disconnected_costs'] = df_heating_costs['CostDiscBuild']

            data_processed.loc[0]['Capex_Boiler_Total'] = data_processed.loc[0]['Capex_Boiler'] + \
                                                                        data_processed.loc[0][
                                                                            'Capex_Boiler_peak'] + \
                                                                        data_processed.loc[0][
                                                                            'Capex_Boiler_backup']
            data_processed.loc[0]['Opex_Boiler_Total'] = data_processed.loc[0]['Opex_BackupBoiler_NG'] + \
                                                                       data_processed.loc[0][
                                                                           'Opex_BackupBoiler_BG'] + \
                                                                       data_processed.loc[0][
                                                                           'Opex_PeakBoiler_NG'] + \
                                                                       data_processed.loc[0][
                                                                           'Opex_PeakBoiler_BG'] + \
                                                                       data_processed.loc[0][
                                                                           'Opex_BaseBoiler_NG'] + \
                                                                       data_processed.loc[0][
                                                                           'Opex_BaseBoiler_BG']
            data_processed.loc[0]['Opex_CHP_Total'] = data_processed.loc[0]['Opex_CHP_NG'] + \
                                                                    data_processed.loc[0][
                                                                        'Opex_CHP_BG']

            data_processed.loc[0]['Opex_Furnace_Total'] = data_processed.loc[0]['Opex_Furnace_wet'] + \
                                                                      data_processed.loc[0]['Opex_Furnace_dry']

            data_processed.loc[0]['Electricity_Costs'] = preprocessing_costs['elecCosts'].values[0]
            data_processed.loc[0]['Process_Heat_Costs'] = preprocessing_costs['hpCosts'].values[0]




            data_processed.loc[0]['Opex_Centralized'] \
                = data_processed.loc[0]['Opex_HP_Sewage'] + data_processed.loc[0]['Opex_HP_Lake'] + \
                  data_processed.loc[0]['Opex_GHP'] + data_processed.loc[0]['Opex_CHP_BG'] + \
                  data_processed.loc[0]['Opex_CHP_NG'] + data_processed.loc[0]['Opex_Furnace_wet'] + \
                  data_processed.loc[0]['Opex_Furnace_dry'] + data_processed.loc[0]['Opex_BaseBoiler_BG'] + \
                  data_processed.loc[0]['Opex_BaseBoiler_NG'] + data_processed.loc[0]['Opex_PeakBoiler_BG'] + \
                  data_processed.loc[0]['Opex_PeakBoiler_NG'] + data_processed.loc[0]['Opex_BackupBoiler_BG'] + \
                  data_processed.loc[0]['Opex_BackupBoiler_NG'] + \
                  data_processed.loc[0]['Electricity_Costs'] + data_processed.loc[0][
                      'Process_Heat_Costs']

            data_processed.loc[0]['Capex_Centralized'] = data_processed.loc[0]['Capex_SC'] + \
                        data_processed.loc[0]['Capex_PVT'] + data_processed.loc[0]['Capex_Boiler_backup'] + \
                        data_processed.loc[0]['Capex_storage_HEX'] + data_processed.loc[0]['Capex_furnace'] + \
                        data_processed.loc[0]['Capex_Boiler'] + data_processed.loc[0]['Capex_Boiler_peak'] + \
                        data_processed.loc[0]['Capex_Lake'] + data_processed.loc[0]['Capex_Sewage'] + \
                        data_processed.loc[0]['Capex_pump']

            data_processed.loc[0]['Capex_Decentralized'] = df_heating_costs['Capex_Disconnected']
            data_processed.loc[0]['Opex_Decentralized'] = df_heating_costs['Opex_Disconnected']
            data_processed.loc[0]['Capex_Total'] = data_processed.loc[0]['Capex_Centralized'] + data_processed.loc[0]['Capex_Decentralized']
            data_processed.loc[0]['Opex_Total'] = data_processed.loc[0]['Opex_Centralized'] + data_processed.loc[0]['Opex_Decentralized']

        elif config.plots_supply_system.network_type == 'DC':
            data_dispatch_path = os.path.join(
                locator.get_optimization_slave_investment_cost_detailed(individual_number, generation_number))
            disconnected_costs = pd.read_csv(data_dispatch_path)

            data_dispatch_path = os.path.join(
                locator.get_optimization_slave_investment_cost_detailed_cooling(individual_number, generation_number))
            df_cooling_costs = pd.read_csv(data_dispatch_path)

            data_dispatch_path = os.path.join(
                locator.get_optimization_slave_cooling_activation_pattern(individual_number, generation_number))
            df_cooling = pd.read_csv(data_dispatch_path).set_index("DATE")

            data_load = pd.read_csv(os.path.join(
                locator.get_optimization_slave_cooling_activation_pattern(individual_number, generation_number)))

            for column_name in df_cooling_costs.columns.values:
                data_processed.loc[0][column_name] = df_cooling_costs[column_name].values

            data_processed.loc[0]['Opex_var_ACH'] = np.sum(df_cooling['Opex_var_ACH'])
            data_processed.loc[0]['Opex_var_CCGT'] = np.sum(df_cooling['Opex_var_CCGT'])
            data_processed.loc[0]['Opex_var_CT'] = np.sum(df_cooling['Opex_var_CT'])
            data_processed.loc[0]['Opex_var_Lake'] = np.sum(df_cooling['Opex_var_Lake'])
            data_processed.loc[0]['Opex_var_VCC'] = np.sum(df_cooling['Opex_var_VCC'])
            data_processed.loc[0]['Opex_var_VCC_backup'] = np.sum(df_cooling['Opex_var_VCC_backup'])
            data_processed.loc[0]['Opex_var_pump'] = data_processed.loc[0]['Opex_var_pump']

            Absorption_chiller_cost_data = pd.read_excel(locator.get_supply_systems(config.region),
                                                         sheetname="Absorption_chiller",
                                                         usecols=['type', 'code', 'cap_min', 'cap_max', 'a', 'b',
                                                                  'c', 'd', 'e', 'IR_%',
                                                                  'LT_yr', 'O&M_%'])
            Absorption_chiller_cost_data = Absorption_chiller_cost_data[
                Absorption_chiller_cost_data['type'] == 'double']
            max_chiller_size = max(Absorption_chiller_cost_data['cap_max'].values)

            Q_ACH_max_W = data_load['Q_from_ACH_W'].max()
            Q_ACH_max_W = Q_ACH_max_W * (1 + SIZING_MARGIN)
            number_of_ACH_chillers = int(ceil(Q_ACH_max_W / max_chiller_size))

            VCC_cost_data = pd.read_excel(locator.get_supply_systems(config.region), sheetname="Chiller")
            VCC_cost_data = VCC_cost_data[VCC_cost_data['code'] == 'CH3']
            max_VCC_chiller_size = max(VCC_cost_data['cap_max'].values)

            Q_VCC_max_W = data_load['Q_from_VCC_W'].max()
            Q_VCC_max_W = Q_VCC_max_W * (1 + SIZING_MARGIN)
            number_of_VCC_chillers = int(ceil(Q_VCC_max_W / max_VCC_chiller_size))

            data_processed.loc[0]['Capex_ACH'] = (data_processed.loc[0]['Capex_a_ACH'] + data_processed.loc[0]['Opex_fixed_ACH']) * number_of_ACH_chillers
            data_processed.loc[0]['Capex_CCGT'] = data_processed.loc[0]['Capex_a_CCGT'] + data_processed.loc[0]['Opex_fixed_CCGT']
            data_processed.loc[0]['Capex_CT'] = data_processed.loc[0]['Capex_a_CT']+ data_processed.loc[0]['Opex_fixed_CT']
            data_processed.loc[0]['Capex_Tank'] = data_processed.loc[0]['Capex_a_Tank'] + data_processed.loc[0]['Opex_fixed_Tank']
            data_processed.loc[0]['Capex_VCC'] = (data_processed.loc[0]['Capex_a_VCC']+ data_processed.loc[0]['Opex_fixed_VCC']) * number_of_VCC_chillers
            data_processed.loc[0]['Capex_VCC_backup'] = data_processed.loc[0]['Capex_a_VCC_backup'] + data_processed.loc[0]['Opex_fixed_VCC_backup']
            data_processed.loc[0]['Capex_a_pump'] = data_processed.loc[0]['Capex_pump']+ data_processed.loc[0]['Opex_fixed_pump']

            data_processed.loc[0]['Disconnected_costs'] = disconnected_costs['CostDiscBuild']
            data_processed.loc[0]['Capex_Decentralized'] = disconnected_costs['Capex_Disconnected']
            data_processed.loc[0]['Opex_Decentralized'] = disconnected_costs['Opex_Disconnected']

            data_processed.loc[0]['Electricity_Costs'] = preprocessing_costs['elecCosts'].values[0]
            data_processed.loc[0]['Process_Heat_Costs'] = preprocessing_costs['hpCosts'].values[0]

            data_processed.loc[0]['Opex_Centralized'] = data_processed.loc[0]['Opex_var_ACH'] + data_processed.loc[0]['Opex_var_CCGT'] + \
                                           data_processed.loc[0]['Opex_var_CT'] + data_processed.loc[0]['Opex_var_Lake'] + \
                                           data_processed.loc[0]['Opex_var_VCC'] + data_processed.loc[0]['Opex_var_VCC_backup'] + data_processed.loc[0]['Opex_var_pump'].values[0] + \
                                           data_processed.loc[0]['Electricity_Costs'] + data_processed.loc[0]['Process_Heat_Costs']

            data_processed.loc[0]['Capex_Centralized'] = data_processed.loc[0]['Capex_a_ACH'] + data_processed.loc[0]['Capex_a_CCGT'] + \
                                           data_processed.loc[0]['Capex_a_CT'] + data_processed.loc[0]['Capex_a_Tank'] + \
                                           data_processed.loc[0]['Capex_a_VCC'] + data_processed.loc[0]['Capex_a_VCC_backup'] + \
                                           data_processed.loc[0]['Capex_pump'] + data_processed.loc[0]['Opex_fixed_ACH'] + \
                                           data_processed.loc[0]['Opex_fixed_CCGT'] + data_processed.loc[0]['Opex_fixed_CT'] + \
                                           data_processed.loc[0]['Opex_fixed_Tank'] + data_processed.loc[0]['Opex_fixed_VCC'] + \
                                           data_processed.loc[0]['Opex_fixed_VCC_backup'] + data_processed.loc[0]['Opex_fixed_pump']


            data_processed.loc[0]['Capex_Total'] = data_processed.loc[0]['Capex_Centralized'] + data_processed.loc[0]['Capex_Decentralized']
            data_processed.loc[0]['Opex_Total'] = data_processed.loc[0]['Opex_Centralized'] + data_processed.loc[0]['Opex_Decentralized']

        return data_processed

    def preprocessing_individual_data_decentralized(self, locator, data_raw, individual, generation, individual_pointer, generation_pointer, config, category):

        total_demand = pd.read_csv(locator.get_total_demand())
        building_names = total_demand.Name.values

        df_all_generations = pd.read_csv(locator.get_optimization_all_individuals())

        # The current structure of CEA has the following columns saved, in future, this will be slightly changed and
        # correspondingly these columns_of_saved_files needs to be changed
        columns_of_saved_files = ['CHP/Furnace', 'CHP/Furnace Share', 'Base Boiler',
                                  'Base Boiler Share', 'Peak Boiler', 'Peak Boiler Share',
                                  'Heating Lake', 'Heating Lake Share', 'Heating Sewage', 'Heating Sewage Share', 'GHP',
                                  'GHP Share',
                                  'Data Centre', 'Compressed Air', 'PV', 'PV Area Share', 'PVT', 'PVT Area Share',
                                  'SC_ET',
                                  'SC_ET Area Share', 'SC_FP', 'SC_FP Area Share', 'DHN Temperature',
                                  'DHN unit configuration',
                                  'Lake Cooling', 'Lake Cooling Share', 'VCC Cooling', 'VCC Cooling Share',
                                  'Absorption Chiller', 'Absorption Chiller Share', 'Storage', 'Storage Share',
                                  'DCN Temperature', 'DCN unit configuration']
        for i in building_names:  # DHN
            columns_of_saved_files.append(str(i) + ' DHN')

        for i in building_names:  # DCN
            columns_of_saved_files.append(str(i) + ' DCN')

        column_names_decentralized = []
        if config.plots_supply_system.network_type == 'DH':
            data_dispatch_path = os.path.join(
                locator.get_optimization_disconnected_folder_building_result_heating(building_names[0]))
            df_heating_costs = pd.read_csv(data_dispatch_path)
            column_names = df_heating_costs.columns.values
            column_names = column_names[1:]
            for i in building_names:
                for j in range(len(column_names)):
                    column_names_decentralized.append(str(i) + " " + column_names[j])

            data_processed = pd.DataFrame(np.zeros([1, len(column_names_decentralized)]),
                                          columns=column_names_decentralized)

        elif config.plots_supply_system.network_type == 'DC':
            data_dispatch_path = os.path.join(
                locator.get_optimization_disconnected_folder_building_result_cooling(building_names[0], 'AHU_ARU_SCU'))
            df_cooling_costs = pd.read_csv(data_dispatch_path)
            column_names = df_cooling_costs.columns.values
            for i in building_names:
                for j in range(len(column_names)):
                    column_names_decentralized.append(str(i) + " " + column_names[j])

            data_processed = pd.DataFrame(np.zeros([1, len(column_names_decentralized)]),
                                          columns=column_names_decentralized)


        individual_barcode_list = data_raw['individual_barcode'].loc[individual].values[0]
        df_current_individual = pd.DataFrame(np.zeros(shape=(1, len(columns_of_saved_files))),
                                             columns=columns_of_saved_files)
        for i, ind in enumerate((columns_of_saved_files)):
            df_current_individual[ind] = individual_barcode_list[i]

        generation_number = generation_pointer
        individual_number = int(individual_pointer[-1])

        df_decentralized = df_all_generations[df_all_generations['generation'] == generation_number]
        df_decentralized = df_decentralized[df_decentralized['individual'] == individual_number]


        if config.plots_supply_system.network_type == 'DH':
            for i in building_names:  # DHN
                if df_decentralized[str(i) + ' DHN'].values[0] == 0:
                    data_dispatch_path = os.path.join(
                        locator.get_optimization_disconnected_folder_building_result_heating(i))
                    df_heating_costs = pd.read_csv(data_dispatch_path)
                    df_heating_costs = df_heating_costs[df_heating_costs["Best configuration"] == 1]
                    for j in range(len(column_names)):
                        name_of_column = str(i) + " " + column_names[j]
                        data_processed.loc[0][name_of_column] = df_heating_costs[column_names[j]].values


        elif config.plots_supply_system.network_type == 'DC':
            for i in building_names:  # DCN
                if df_decentralized[str(i) + ' DCN'].values[0] == 0:
                    data_dispatch_path = os.path.join(
                        locator.get_optimization_disconnected_folder_building_result_cooling(i, 'AHU_ARU_SCU'))
                    df_cooling_costs = pd.read_csv(data_dispatch_path)
                    df_cooling_costs = df_cooling_costs[df_cooling_costs["Best configuration"] == 1]
                    for j in range(len(column_names)):
                        name_of_column = str(i) + " " + column_names[j]
                        data_processed.loc[0][name_of_column] = df_cooling_costs[column_names[j]].values

        return data_processed

    def preprocessing_create_thermal_network_layout(self, config, locator, output_name_network, output_type_network, buildings_data):

        buildings_data = buildings_data.loc[buildings_data["Type"]=="CENTRALIZED"]
        buildings_connected = buildings_data.Name.values

        # configure layout script to create the new network adn store in the folder inputs.
        config.network_layout.network_type = output_type_network
        config.network_layout.create_plant = True
        config.network_layout.buildings = buildings_connected
        network_layout(config, locator, output_name_network)

    def preprocessing_import_exports(self, locator, generation, individual, generation_pointer, individual_pointer, config):

        data_imports_exports_electricity_W = electricity_import_and_exports(generation_pointer, int(individual_pointer[-1]), locator, config)
        data_imports_natural_gas_W = natural_gas_imports(generation_pointer, int(individual_pointer[-1]), locator, config)

        return  {"E_hourly_Wh":data_imports_exports_electricity_W, "E_yearly_Wh": data_imports_exports_electricity_W.sum(axis=0),
                 "NG_hourly_Wh": data_imports_natural_gas_W,
                 "NG_yearly_Wh": data_imports_natural_gas_W.sum(axis=0)}

    def preprocessing_energy_mix(self, locator, generation, individual, generation_pointer, individual_pointer, config):

        data_energy_mix_W = energy_mix_based_on_technologies_script(generation_pointer, int(individual_pointer[-1]), locator, config)

        return  {"yearly_Wh": data_energy_mix_W}

    def preprocessing_capacities_installed(self, locator, generation, individual, generation_pointer, individual_pointer, output_type_network, config):

        data_capacities_installed, building_connectivity = supply_system_configuration(generation_pointer, int(individual_pointer[-1]), locator, output_type_network, config)

        return {"capacities": data_capacities_installed, "building_connectivity":building_connectivity}

    def erase_zeros(self, data, fields):
        analysis_fields_no_zero = []
        for field in fields:
            if isinstance(data[field], float):
                sum = data[field]
            else:
                sum = data[field].sum()
            if not np.isclose(sum, 0.0):
                analysis_fields_no_zero += [field]
        return analysis_fields_no_zero

    def individual_heating_dispatch_curve(self, category):
        title = 'Dispatch curve for configuration' + self.individual + " in generation " + str(self.generation)
        output_path = self.locator.get_timeseries_plots_file(
            'gen' + str(self.generation) + '_' + self.individual + '_centralized_heating_dispatch_curve', category)
        anlysis_fields_loads = self.analysis_fields_heating_loads
        data = self.data_processed_individual
        plot = individual_activation_curve(data, anlysis_fields_loads, self.analysis_fields_heating, title, output_path)
        return plot

    def individual_heating_storage_dispatch_curve(self, category):
        title = 'Dispatch curve for configuration ' + self.individual + " in generation " + str(
            self.generation)
        output_path = self.locator.get_timeseries_plots_file(
            'gen' + str(self.generation) + '_' + self.individual + '_centralized_heating_storage_dispatch_curve', category)
        analysis_fields_charging = self.analysis_fields_heating_storage_charging
        analysis_fields_discharging = self.analysis_fields_heating_storage_discharging
        analysis_fields_status = self.analysis_fields_heating_storage_status
        data = self.data_processed_individual.copy()
        plot = thermal_storage_activation_curve(data, analysis_fields_charging, analysis_fields_discharging,
                                                analysis_fields_status, title, output_path)
        return plot

    def individual_electricity_dispatch_curve_heating(self, category):
        title = 'Dispatch curve for configuration ' + self.individual + " in generation " + str(self.generation)
        output_path = self.locator.get_timeseries_plots_file(
            'gen' + str(self.generation) + '_' + self.individual + '_centralized_electricity_dispatch_curve', category)
        anlysis_fields_loads = self.analysis_fields_electricity_loads_heating
        data = self.data_processed_imports_exports["E_hourly_Wh"].copy()
        data.set_index("DATE")
        plot = individual_activation_curve(data, anlysis_fields_loads, self.analysis_fields_electricity_heating, title,
                                           output_path)
        return plot

    def individual_electricity_dispatch_curve_cooling(self, category):
        title = 'Dispatch curve for ' + self.individual + " in generation " + str(self.generation)
        output_path = self.locator.get_timeseries_plots_file(
            'gen' + str(self.generation) + '_' + self.individual + '_centralized_electricity_dispatch_curve', category)
        anlysis_fields_loads = self.analysis_fields_electricity_loads_cooling
        data = self.data_processed_imports_exports["E_hourly_Wh"].copy()
        data_indexed = data.set_index("DATE")
        analysis_fields_clean = self.erase_zeros(data_indexed, self.analysis_fields_electricity_cooling)
        plot = individual_activation_curve(data_indexed, anlysis_fields_loads, analysis_fields_clean, title,
                                           output_path)
        return plot

    def individual_cooling_dispatch_curve(self, category):
        title = 'Dispatch curve for ' + self.individual + " in generation " + str(self.generation)
        output_path = self.locator.get_timeseries_plots_file(
            'gen' + str(self.generation) + '_' + self.individual + '_centralized_cooling_dispatch_curve', category)
        data = self.data_processed_individual.copy()
        anlysis_fields_loads = self.analysis_fields_cooling_loads
        analysis_fields_clean = self.erase_zeros(data, self.analysis_fields_cooling)
        plot = individual_activation_curve(data, anlysis_fields_loads, analysis_fields_clean, title, output_path)
        return plot

    def cost_analysis_cooling_decentralized(self, config, category):
        data = self.data_processed_cost_decentralized
        output_path = self.locator.get_timeseries_plots_file(
            'gen' + str(self.generation) + '_' + self.individual + '_decentralized_costs_per_generation_unit', category)
        plot = cost_analysis_curve_decentralized(data, self.locator, self.generation, self.individual, config, output_path)
        return plot

    def cost_analysis_heating_decentralized(self, config, category):

        data = self.data_processed_cost_decentralized
        output_path = self.locator.get_timeseries_plots_file(
            'gen' + str(self.generation) + '_' + self.individual + '_decentralized_costs_per_generation_unit', category)
        plot = cost_analysis_curve_decentralized(data, self.locator, self.generation, self.individual, config, output_path)
        return plot

    def pie_import_exports(self, category):
        title = 'Imports vs exports in ' + self.individual + " in generation " + str(self.generation)
        output_path = self.locator.get_timeseries_plots_file(
            'gen' + str(self.generation) + '_' + self.individual + '_pie_import_exports', category)
        anlysis_fields = ["E_from_grid_W", ##TODO: get values for imports of gas etc..Low priority
                          "E_CHP_to_grid_W",
                          "E_PV_to_grid_W",
                          "NG_used_CCGT_W"]
        data = self.data_processed_imports_exports["E_yearly_Wh"].copy()
        data = data.append(self.data_processed_imports_exports['NG_yearly_Wh'].copy())
        analysis_fields_clean = self.erase_zeros(data, anlysis_fields)
        plot = pie_chart_imports_exports(data, analysis_fields_clean, title, output_path)

        return plot

    def bar_total_costs(self, category):
        title = 'CAPEX vs OPEX for ' + self.individual + " in generation " + str(self.generation)
        output_path = self.locator.get_timeseries_plots_file(
            'gen' + str(self.generation) + '_' + self.individual + '_bar_costs', category)
        anlysis_fields = ["Opex_Centralized",
                          "Capex_Centralized",
                          "Capex_Decentralized",
                          "Opex_Decentralized"]
        data = self.data_processed_cost_centralized.copy()
        analysis_fields_clean = self.erase_zeros(data, anlysis_fields)
        plot = bar_chart_costs(data.iloc[0], analysis_fields_clean, title, output_path)
        return plot

    def pie_energy_supply_mix(self, category):
        title = 'Energy supply mix of ' + self.individual + " in generation " + str(self.generation)
        output_path = self.locator.get_timeseries_plots_file(
            'gen' + str(self.generation) + '_' + self.individual + '_pie_energy_supply_mix', category)
        anlysis_fields = ["Q_VCC_total_W", "Q_Lake_total_W", "Q_ACH_total_W", "Q_VCC_backup_total_W",
                          "Q_thermal_storage_total_W", "E_ACH_total_W",
                          "E_VCC_total_W", "E_VCC_backup_total_W", "E_hotwater_total_W",
                          "E_building_appliances_total_W", "NG_used_total_W"]
        data = self.data_energy_mix["yearly_Wh"].copy()
        analysis_fields_clean = self.erase_zeros(data, anlysis_fields)
        plot = pie_chart_imports_exports(data.iloc[0], analysis_fields_clean, title, output_path)
        return plot

    def map_location_size_customers_energy_system(self, output_type_network, category):
        title = 'Energy system map for %s in generation %s' % (self.individual, self.generation)
        output_path = self.locator.get_timeseries_plots_file('gen' + str(self.generation) + '_' + self.individual + '_energy_system_map', category)
        output_name_network = "gen%s_%s" % (self.generation, self.individual)
        data_processed_capacities_installed = self.preprocessing_capacities_installed(self.locator,
                                                                                           self.generation,
                                                                                           self.individual,
                                                                                           self.generation_pointer,
                                                                                           self.individual_pointer,
                                                                                           self.output_type_network,
                                                                                           self.config)
        data = data_processed_capacities_installed["capacities"]
        buildings_connected = data_processed_capacities_installed["building_connectivity"]
        analysis_fields = data.columns.values
        analysis_fields_clean = self.erase_zeros(data, analysis_fields)
        self.preprocessing_create_thermal_network_layout(self.config, self.locator, output_name_network, output_type_network,
                                                          buildings_connected)

        plot = map_chart(data, self.locator, analysis_fields_clean, title, output_path,
                         output_name_network, output_type_network,
                         buildings_connected)
        return plot

    def impact_in_the_local_grid (self, category):
        title = 'Likelihood ramp-up/ramp-down hours in ' + self.individual + " in generation " + str(self.generation)
        output_path = self.locator.get_timeseries_plots_file(
            'gen' + str(self.generation) + '_' + self.individual + '_likelihood_ramp-up_ramp_down', category)

        anlysis_fields = ["E_total_to_grid_W_negative",
                          "E_from_grid_W",]
        data = self.data_processed_imports_exports["E_hourly_Wh"].copy()
        analysis_fields_clean = self.erase_zeros(data, anlysis_fields)
        plot = likelihood_chart(data, analysis_fields_clean, title, output_path)

        return plot

def main(config):
    locator = cea.inputlocator.InputLocator(config.scenario)

    print("Running dashboard with scenario = %s" % config.scenario)
    print("Running dashboard with the next generation = %s" % config.plots_supply_system.generation)
    print("Running dashboard with the next individual = %s" % config.plots_supply_system.individual)

    plots_main(locator, config)

if __name__ == '__main__':
    main(cea.config.Configuration())