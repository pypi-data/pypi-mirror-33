"""
Evolutionary algorithm main

"""
from __future__ import division

import time
import json
from cea.optimization.constants import PROBA, SIGMAP, GHP_HMAX_SIZE, N_HR, N_HEAT, N_PV, N_PVT
import cea.optimization.master.crossover as cx
import cea.optimization.master.evaluation as evaluation
import random
from deap import base
from deap import creator
from deap import tools
import cea.optimization.master.generation as generation
import mutations as mut
import selection as sel
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cmx
import os
import numpy as np
import pandas as pd
import cea.optimization.supportFn as sFn



__author__ =  "Sreepathi Bhargava Krishna"
__copyright__ = "Copyright 2015, Architecture and Building Systems - ETH Zurich"
__credits__ = [ "Sreepathi Bhargava Krishna", "Thuy-An Nguyen", "Tim Vollrath", "Jimeno A. Fonseca"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "thomas@arch.ethz.ch"
__status__ = "Production"


def evolutionary_algo_main(locator, building_names, extra_costs, extra_CO2, extra_primary_energy, solar_features,
                           network_features, gv, config, prices, lca,  genCP=00):

    """
    Evolutionary algorithm to optimize the district energy system's design.
    This algorithm optimizes the size and operation of technologies for a district heating network.
    electrical network are not considered but their burdens in terms electricity costs, efficiency and emissions
    is added on top of the optimization.
    The equipment for cooling networks is not optimized as it is assumed that all customers with cooling needs will be
    connected to a lake. in case there is not enough capacity from the lake, a chiller and cooling tower is used to
    cover the extra needs.

    genCP is defaulted to '0' when the entire optimization is run. For running from the intermediate generations, key in
    the generation from which the optimization should continue.

    :param locator: locator class
    :param building_names: vector with building names
    :param extra_costs: costs calculated before optimization of specific energy services
     (process heat and electricity)
    :param extra_CO2: green house gas emissions calculated before optimization of specific energy services
     (process heat and electricity)
    :param extra_primary_energy: primary energy calculated before optimization of specific energy services
     (process heat and electricity)
    :param solar_features: object class with vectors and values of interest for the integration of solar potentials
    :param network_features: object class with linear coefficients of the network obtained after its optimization
    :param gv: global variables class
    :param genCP: 0
    :type locator: class
    :type building_names: array
    :type extra_costs: float
    :type extra_CO2: float
    :type extra_primary_energy: float
    :type solar_features: class
    :type network_features: class
    :type gv: class
    :type genCP: int
    :return: for every generation 'g': it stores the results of every generation of the genetic algorithm in the
     subfolders locator.get_optimization_master_results_folder() as a python pickle file.
    :rtype: pickled file
    """
    t0 = time.clock()
    genCP = config.optimization.recoverycheckpoint

    # initiating hall of fame size and the function evaluations
    halloffame_size = config.optimization.halloffame
    function_evals = 0
    euclidean_distance = 0
    spread = 0
    random.seed(config.optimization.random_seed)
    np.random.seed(config.optimization.random_seed)

    # get number of buildings
    nBuildings = len(building_names)

    # DEFINE OBJECTIVE FUNCTION
    def objective_function(individual_number, individual, generation):
        """
        Objective function is used to calculate the costs, CO2, primary energy and the variables corresponding to the
        individual
        :param individual: Input individual
        :type individual: list
        :return: returns costs, CO2, primary energy and the master_to_slave_vars
        """
        print ( 'cea optimization progress: individual ' + str(individual_number) + ' and generation '+ str(generation) + '/' + str(config.optimization.ngen))
        costs, CO2, prim, master_to_slave_vars, valid_individual = evaluation.evaluation_main(individual, building_names, locator, extra_costs, extra_CO2, extra_primary_energy, solar_features,
                                                                                              network_features, gv, config, prices, lca, individual_number, generation)
        return costs, CO2, prim, master_to_slave_vars, valid_individual

    # SET-UP EVOLUTIONARY ALGORITHM
    # Contains 3 minimization objectives : Costs, CO2 emissions, Primary Energy Needs
    # this part of the script sets up the optimization algorithm in the same syntax of DEAP toolbox
    creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0, -1.0)) # weights of -1 for minimization, +1 for maximization
    creator.create("Individual", list, fitness=creator.Fitness)
    toolbox = base.Toolbox()
    toolbox.register("generate", generation.generate_main, nBuildings, config)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.generate)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", objective_function)

    # Initialization of variables
    DHN_network_list = ["1"*nBuildings]
    DCN_network_list = ["1"*nBuildings]
    epsInd = []
    invalid_ind = []
    halloffame = []
    halloffame_fitness = []
    costs_list = []
    co2_list = []
    prim_list = []
    valid_pop = []
    slavedata_list = []
    fitnesses = []
    capacities = []
    disconnected_capacities = []
    Furnace_wet = 0
    Furnace_wet_capacity_W = 0
    Furnace_dry = 0
    Furnace_dry_capacity_W = 0
    CHP_NG = 0
    CHP_NG_capacity_W = 0
    CHP_BG = 0
    CHP_BG_capacity_W = 0
    Base_boiler_BG = 0
    Base_boiler_BG_capacity_W = 0
    Base_boiler_NG = 0
    Base_boiler_NG_capacity_W = 0
    Peak_boiler_BG = 0
    Peak_boiler_BG_capacity_W = 0
    Peak_boiler_NG = 0
    Peak_boiler_NG_capacity_W = 0
    cooling_all_units = 'AHU_ARU_SCU'
    heating_all_units = 'AHU_ARU_SHU'

    columns_of_saved_files = ['generation', 'individual', 'CHP/Furnace', 'CHP/Furnace Share', 'Base Boiler', 'Base Boiler Share', 'Peak Boiler', 'Peak Boiler Share',
               'Heating Lake', 'Heating Lake Share', 'Heating Sewage', 'Heating Sewage Share', 'GHP', 'GHP Share',
               'Data Centre', 'Compressed Air', 'PV', 'PV Area Share', 'PVT', 'PVT Area Share', 'SC_ET', 'SC_ET Area Share',
               'SC_FP', 'SC_FP Area Share', 'DHN Temperature', 'DHN unit configuration', 'Lake Cooling', 'Lake Cooling Share', 'VCC Cooling', 'VCC Cooling Share',
               'Absorption Chiller', 'Absorption Chiller Share', 'Storage', 'Storage Share', 'DCN Temperature', 'DCN unit configuration']
    for i in building_names: #DHN
        columns_of_saved_files.append(str(i) + ' DHN')

    for i in building_names: #DCN
        columns_of_saved_files.append(str(i) + ' DCN')

    columns_of_saved_files.append('TAC')
    columns_of_saved_files.append('CO2 emissions')
    columns_of_saved_files.append('Primary Energy')

    # Evolutionary strategy
    if genCP is 0:

        # create population based on the number of individuals in the config file
        pop = toolbox.population(n=config.optimization.initialind)

        # Check the network and update ntwList. ntwList size keeps changing as the following loop runs
        for ind in pop:
            evaluation.checkNtw(ind, DHN_network_list, DCN_network_list, locator, gv, config, building_names)

        # Evaluate the initial population
        print "Evaluate initial population"
        DHN_network_list = DHN_network_list[1:]  # done this to remove the first individual in the ntwList as it is an initial value
        DCN_network_list = DCN_network_list[1:]  # done this to remove the first individual in the ntwList as it is an initial value
        # costs_list updates the costs involved in every individual
        # co2_list updates the GHG emissions in terms of CO2
        # prim_list updates the primary energy  corresponding to every individual
        # slavedata_list updates the master_to_slave variables corresponding to every individual. This is used in
        # calculating the capacities of both the centralized and the decentralized system
        for i, ind in enumerate(pop):
            
            a = objective_function(i, ind, genCP)
            costs_list.append(a[0])
            co2_list.append(a[1])
            prim_list.append(a[2])
            slavedata_list.append(a[3])
            valid_pop.append(a[4])
            function_evals = function_evals + 1  # keeping track of number of function evaluations


        zero_data = np.zeros(shape = (len(pop), len(columns_of_saved_files)))
        saved_dataframe_for_each_generation = pd.DataFrame(zero_data, columns = columns_of_saved_files)
        pop[:] = valid_pop

        for i, ind in enumerate(pop):
            saved_dataframe_for_each_generation['individual'][i] = i
            saved_dataframe_for_each_generation['generation'][i] = genCP
            for j in range(len(columns_of_saved_files) - 5):
                saved_dataframe_for_each_generation[columns_of_saved_files[j+2]][i] = ind[j]
            saved_dataframe_for_each_generation['TAC'][i] = costs_list[i]
            saved_dataframe_for_each_generation['CO2 emissions'][i] = co2_list[i]
            saved_dataframe_for_each_generation['Primary Energy'][i] = prim_list[i]

        saved_dataframe_for_each_generation.to_csv(locator.get_optimization_individuals_in_generation(genCP))
        # fitnesses appends the costs, co2 and primary energy corresponding to each individual
        # the main reason of doing the following is to follow the syntax provided by DEAP toolbox as it works on the
        # fitness class in every individual
        for i in range(len(costs_list)):
            fitnesses.append([costs_list[i], co2_list[i], prim_list[i]])

        # linking every individual with the corresponding fitness, this also keeps a track of the number of function
        # evaluations. This can further be used as a stopping criteria in future
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        # halloffame is the best individuals that are observed in all generations
        # the size of the halloffame is linked to the number of initial individuals
        if len(halloffame) <= halloffame_size:
            halloffame.extend(pop)

        # halloffame_fitness appends the fitness values corresponding to the individuals in the halloffame
        for ind in halloffame:
            halloffame_fitness.append(ind.fitness.values)

        # disconnected building capacity is calculated from the networklist of every individual
        # disconnected building have four energy technologies namely Bio-gas Boiler, Natural-gas Boiler, Fuel Cell
        # and Geothermal heat pumps
        # These values are already calculated in 'decentralized_main.py'. This piece of script gets these values from
        # the already created csv files
        if config.optimization.isheating:
            network_list = DHN_network_list
        elif config.optimization.iscooling:
            network_list = DCN_network_list

        for (index, network) in enumerate(network_list):
            intermediate_capacities = []
            for i in range(len(network)):
                # if a building is connected, which corresponds to '1' then the disconnected shares are linked to the
                # number of units the DHN/DCN is supplying. A building can be supplied AHU demand from the centralized
                # plant whereas the remaining load corresponding to ARU and SHU/SCU be supplied by the decentralized option
                # if a building is disconnected, which corresponds to '0' then disconnected shares are imported from csv files
                Disconnected_Boiler_BG_share_heating = 0
                Disconnected_Boiler_BG_capacity_heating_W = 0
                Disconnected_Boiler_NG_share_heating = 0
                Disconnected_Boiler_NG_capacity_heating_W = 0
                Disconnected_FC_share_heating = 0
                Disconnected_FC_capacity_heating_W = 0
                Disconnected_GHP_share_heating = 0
                Disconnected_GHP_capacity_heating_W = 0

                Disconnected_VCC_to_AHU_share_cooling = 0
                Disconnected_VCC_to_AHU_capacity_cooling_W = 0
                Disconnected_VCC_to_ARU_share_cooling = 0
                Disconnected_VCC_to_ARU_capacity_cooling_W = 0
                Disconnected_VCC_to_SCU_share_cooling = 0
                Disconnected_VCC_to_SCU_capacity_cooling_W = 0
                Disconnected_VCC_to_AHU_ARU_share_cooling = 0
                Disconnected_VCC_to_AHU_ARU_capacity_cooling_W = 0
                Disconnected_VCC_to_AHU_SCU_share_cooling = 0
                Disconnected_VCC_to_AHU_SCU_capacity_cooling_W = 0
                Disconnected_VCC_to_ARU_SCU_share_cooling = 0
                Disconnected_VCC_to_ARU_SCU_capacity_cooling_W = 0
                Disconnected_VCC_to_AHU_ARU_SCU_share_cooling = 0
                Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W = 0

                Disconnected_single_effect_ACH_to_AHU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_ARU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_ARU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_SCU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_SCU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W = 0

                Disconnected_direct_expansion_to_AHU_share_cooling = 0
                Disconnected_direct_expansion_to_AHU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_ARU_share_cooling = 0
                Disconnected_direct_expansion_to_ARU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_SCU_share_cooling = 0
                Disconnected_direct_expansion_to_SCU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_AHU_SCU_share_cooling = 0
                Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_AHU_ARU_share_cooling = 0
                Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_ARU_SCU_share_cooling = 0
                Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling = 0
                Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W = 0

                if network[i] == "0":
                    if config.optimization.isheating:
                        df = pd.read_csv(locator.get_optimization_disconnected_folder_building_result_heating(building_names[i]))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_Boiler_BG_share_heating = dfBest["BoilerBG Share"].iloc[0]
                        Disconnected_Boiler_NG_share_heating = dfBest["BoilerNG Share"].iloc[0]
                        Disconnected_FC_share_heating = dfBest["FC Share"].iloc[0]
                        Disconnected_GHP_share_heating = dfBest["GHP Share"].iloc[0]

                        if Disconnected_Boiler_BG_share_heating == 1:
                            Disconnected_Boiler_BG_capacity_heating_W = dfBest["Nominal Power"].iloc[0]

                        if Disconnected_Boiler_NG_share_heating == 1:
                            Disconnected_Boiler_NG_capacity_heating_W = dfBest["Nominal Power"].iloc[0]

                        if Disconnected_FC_share_heating == 1:
                            Disconnected_FC_capacity_heating_W = dfBest["Nominal Power"].iloc[0]

                        if Disconnected_GHP_share_heating == 1:
                            Disconnected_GHP_capacity_heating_W = dfBest["Nominal Power"].iloc[0]

                        if (Disconnected_FC_share_heating == 0 and Disconnected_Boiler_BG_share_heating == 0 and Disconnected_GHP_share_heating != 0 and Disconnected_Boiler_NG_share_heating != 0):
                            Disconnected_Boiler_NG_capacity_heating_W = dfBest["Nominal Power"].iloc[0] / Disconnected_Boiler_NG_share_heating
                            Disconnected_GHP_capacity_heating_W = dfBest["Nominal Power"].iloc[0] / Disconnected_GHP_share_heating

                        disconnected_capacity = dict(building_name=building_names[i],
                                                     Disconnected_Boiler_BG_share=Disconnected_Boiler_BG_share_heating,
                                                     Disconnected_Boiler_BG_capacity_W=Disconnected_Boiler_BG_capacity_heating_W,
                                                     Disconnected_Boiler_NG_share=Disconnected_Boiler_NG_share_heating,
                                                     Disconnected_Boiler_NG_capacity_W=Disconnected_Boiler_NG_capacity_heating_W,
                                                     Disconnected_FC_share=Disconnected_FC_share_heating,
                                                     Disconnected_FC_capacity_W=Disconnected_FC_capacity_heating_W,
                                                     Disconnected_GHP_share=Disconnected_GHP_share_heating,
                                                     Disconnected_GHP_capacity_W=Disconnected_GHP_capacity_heating_W,
                                                     Disconnected_VCC_to_AHU_share_cooling=Disconnected_VCC_to_AHU_share_cooling,
                                                     Disconnected_VCC_to_AHU_capacity_cooling_W=Disconnected_VCC_to_AHU_capacity_cooling_W,
                                                     Disconnected_VCC_to_ARU_share_cooling=Disconnected_VCC_to_ARU_share_cooling,
                                                     Disconnected_VCC_to_ARU_capacity_cooling_W=Disconnected_VCC_to_ARU_capacity_cooling_W,
                                                     Disconnected_VCC_to_SCU_share_cooling=Disconnected_VCC_to_SCU_share_cooling,
                                                     Disconnected_VCC_to_SCU_capacity_cooling_W=Disconnected_VCC_to_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_ARU_share_cooling=Disconnected_VCC_to_AHU_ARU_share_cooling,
                                                     Disconnected_VCC_to_AHU_ARU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_SCU_share_cooling=Disconnected_VCC_to_AHU_SCU_share_cooling,
                                                     Disconnected_VCC_to_AHU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_ARU_SCU_share_cooling=Disconnected_VCC_to_ARU_SCU_share_cooling,
                                                     Disconnected_VCC_to_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_ARU_SCU_share_cooling=Disconnected_VCC_to_AHU_ARU_SCU_share_cooling,
                                                     Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_share_cooling=Disconnected_direct_expansion_to_AHU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_ARU_share_cooling=Disconnected_direct_expansion_to_ARU_share_cooling,
                                                     Disconnected_direct_expansion_to_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_SCU_share_cooling=Disconnected_direct_expansion_to_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_ARU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_ARU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W)

                    elif config.optimization.iscooling:

                        df = pd.read_csv(locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i], cooling_all_units))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling = dfBest["single effect ACH to AHU_ARU_SCU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_SCU_share_FP_cooling = dfBest["single effect ACH to SCU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling = dfBest["single effect ACH to AHU_ARU_SCU Share (ET)"].iloc[0]
                        Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling = dfBest["DX to AHU_ARU_SCU Share"].iloc[0]
                        Disconnected_VCC_to_AHU_ARU_share_cooling = dfBest["VCC to AHU_ARU Share"].iloc[0]
                        Disconnected_VCC_to_AHU_ARU_SCU_share_cooling = dfBest["VCC to AHU_ARU_SCU Share"].iloc[0]
                        Disconnected_VCC_to_SCU_share_cooling = dfBest["VCC to SCU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W = dfBest["Nominal Power single effect ACH to AHU_ARU_SCU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_SCU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W = dfBest["Nominal Power single effect ACH to SCU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W = dfBest["Nominal Power single effect ACH to AHU_ARU_SCU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling == 1:
                            Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W = dfBest["Nominal Power DX to AHU_ARU_SCU [W]"].iloc[0]

                        if Disconnected_VCC_to_AHU_ARU_share_cooling == 1:
                            Disconnected_VCC_to_AHU_ARU_capacity_cooling_W = dfBest["Nominal Power VCC to AHU_ARU [W]"].iloc[0]

                        if Disconnected_VCC_to_AHU_ARU_SCU_share_cooling == 1:
                            Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W = dfBest["Nominal Power VCC to AHU_ARU_SCU [W]"].iloc[0]

                        if Disconnected_VCC_to_SCU_share_cooling == 1:
                            Disconnected_VCC_to_SCU_capacity_cooling_W = dfBest["Nominal Power VCC to SCU [W]"].iloc[0]

                        disconnected_capacity = dict(building_name=building_names[i],
                                                     Disconnected_Boiler_BG_share=Disconnected_Boiler_BG_share_heating,
                                                     Disconnected_Boiler_BG_capacity_W=Disconnected_Boiler_BG_capacity_heating_W,
                                                     Disconnected_Boiler_NG_share=Disconnected_Boiler_NG_share_heating,
                                                     Disconnected_Boiler_NG_capacity_W=Disconnected_Boiler_NG_capacity_heating_W,
                                                     Disconnected_FC_share=Disconnected_FC_share_heating,
                                                     Disconnected_FC_capacity_W=Disconnected_FC_capacity_heating_W,
                                                     Disconnected_GHP_share=Disconnected_GHP_share_heating,
                                                     Disconnected_GHP_capacity_W=Disconnected_GHP_capacity_heating_W,
                                                     Disconnected_VCC_to_AHU_share_cooling=Disconnected_VCC_to_AHU_share_cooling,
                                                     Disconnected_VCC_to_AHU_capacity_cooling_W=Disconnected_VCC_to_AHU_capacity_cooling_W,
                                                     Disconnected_VCC_to_ARU_share_cooling=Disconnected_VCC_to_ARU_share_cooling,
                                                     Disconnected_VCC_to_ARU_capacity_cooling_W=Disconnected_VCC_to_ARU_capacity_cooling_W,
                                                     Disconnected_VCC_to_SCU_share_cooling=Disconnected_VCC_to_SCU_share_cooling,
                                                     Disconnected_VCC_to_SCU_capacity_cooling_W=Disconnected_VCC_to_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_ARU_share_cooling=Disconnected_VCC_to_AHU_ARU_share_cooling,
                                                     Disconnected_VCC_to_AHU_ARU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_SCU_share_cooling=Disconnected_VCC_to_AHU_SCU_share_cooling,
                                                     Disconnected_VCC_to_AHU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_ARU_SCU_share_cooling=Disconnected_VCC_to_ARU_SCU_share_cooling,
                                                     Disconnected_VCC_to_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_ARU_SCU_share_cooling=Disconnected_VCC_to_AHU_ARU_SCU_share_cooling,
                                                     Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_share_cooling=Disconnected_direct_expansion_to_AHU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_ARU_share_cooling=Disconnected_direct_expansion_to_ARU_share_cooling,
                                                     Disconnected_direct_expansion_to_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_SCU_share_cooling=Disconnected_direct_expansion_to_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_ARU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_ARU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W)

                    else:
                        raise ValueError("the region is not specified correctly")
                else:
                    DCN_unit_configuration = saved_dataframe_for_each_generation['DCN unit configuration'][index]

                    if DCN_unit_configuration == 1: # corresponds to AHU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'ARU_SCU'
                        df = pd.read_csv(
                            locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i],
                            decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_ARU_SCU_share_cooling = dfBest["DX to ARU_SCU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling = dfBest["single effect ACH to ARU_SCU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling = dfBest["single effect ACH to ARU_SCU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_ARU_SCU_share_cooling = dfBest["VCC to ARU_SCU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W = dfBest["Nominal Power single effect ACH to ARU_SCU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W = dfBest["Nominal Power single effect ACH to ARU_SCU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_ARU_SCU_share_cooling == 1:
                            Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W = dfBest["Nominal Power DX to ARU_SCU [W]"].iloc[0]

                        if Disconnected_VCC_to_ARU_SCU_share_cooling == 1:
                            Disconnected_VCC_to_ARU_SCU_capacity_cooling_W = dfBest["Nominal Power VCC to ARU_SCU [W]"].iloc[0]

                    if DCN_unit_configuration == 2: # corresponds to ARU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'AHU_SCU'
                        df = pd.read_csv(
                            locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i],
                            decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_AHU_SCU_share_cooling = dfBest["DX to AHU_SCU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling = dfBest["single effect ACH to AHU_SCU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling = dfBest["single effect ACH to AHU_SCU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_ARU_SCU_share_cooling = dfBest["VCC to AHU_SCU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W = dfBest["Nominal Power single effect ACH to AHU_SCU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W = dfBest["Nominal Power single effect ACH to AHU_SCU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_AHU_SCU_share_cooling == 1:
                            Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W = dfBest["Nominal Power DX to AHU_SCU [W]"].iloc[0]

                        if Disconnected_VCC_to_AHU_SCU_share_cooling == 1:
                            Disconnected_VCC_to_AHU_SCU_capacity_cooling_W = dfBest["Nominal Power VCC to AHU_SCU [W]"].iloc[0]

                    if DCN_unit_configuration == 3: # corresponds to SCU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'AHU_ARU'

                        df = pd.read_csv(locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i], decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_AHU_ARU_share_cooling = dfBest["DX to AHU_ARU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling = \
                        dfBest["single effect ACH to AHU_ARU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling = \
                        dfBest["single effect ACH to AHU_ARU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_AHU_ARU_share_cooling = dfBest["VCC to AHU_ARU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W = \
                            dfBest["Nominal Power single effect ACH to AHU_ARU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W = \
                            dfBest["Nominal Power single effect ACH to AHU_ARU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_AHU_ARU_share_cooling == 1:
                            Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W = \
                            dfBest["Nominal Power DX to AHU_ARU [W]"].iloc[0]

                        if Disconnected_VCC_to_AHU_ARU_share_cooling == 1:
                            Disconnected_VCC_to_AHU_ARU_capacity_cooling_W = \
                            dfBest["Nominal Power VCC to AHU_ARU [W]"].iloc[0]

                    if DCN_unit_configuration == 4:  # corresponds to AHU + ARU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'SCU'

                        df = pd.read_csv(locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i], decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_SCU_share_cooling = dfBest["DX to SCU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_SCU_share_FP_cooling = \
                        dfBest["single effect ACH to SCU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_SCU_share_ET_cooling = \
                        dfBest["single effect ACH to SCU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_SCU_share_cooling = dfBest["VCC to SCU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_SCU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W = \
                            dfBest["Nominal Power single effect ACH to SCU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_SCU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W = \
                            dfBest["Nominal Power single effect ACH to SCU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_SCU_share_cooling == 1:
                            Disconnected_direct_expansion_to_SCU_capacity_cooling_W = \
                            dfBest["Nominal Power DX to SCU [W]"].iloc[0]

                        if Disconnected_VCC_to_SCU_share_cooling == 1:
                            Disconnected_VCC_to_SCU_capacity_cooling_W = \
                            dfBest["Nominal Power VCC to SCU [W]"].iloc[0]

                    if DCN_unit_configuration == 5: # corresponds to AHU + SCU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'ARU'

                        df = pd.read_csv(locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i], decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_ARU_share_cooling = dfBest["DX to ARU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_ARU_share_FP_cooling = \
                        dfBest["single effect ACH to ARU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_ARU_share_ET_cooling = \
                        dfBest["single effect ACH to ARU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_ARU_share_cooling = dfBest["VCC to ARU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_ARU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W = \
                            dfBest["Nominal Power single effect ACH to ARU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_ARU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W = \
                            dfBest["Nominal Power single effect ACH to ARU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_ARU_share_cooling == 1:
                            Disconnected_direct_expansion_to_ARU_capacity_cooling_W = \
                            dfBest["Nominal Power DX to ARU [W]"].iloc[0]

                        if Disconnected_VCC_to_ARU_share_cooling == 1:
                            Disconnected_VCC_to_ARU_capacity_cooling_W = \
                            dfBest["Nominal Power VCC to ARU [W]"].iloc[0]

                    if DCN_unit_configuration == 6:  # corresponds to ARU + SCU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'AHU'

                        df = pd.read_csv(
                            locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i],
                            decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_AHU_share_cooling = dfBest["DX to AHU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_share_FP_cooling = \
                            dfBest["single effect ACH to AHU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_share_ET_cooling = \
                            dfBest["single effect ACH to AHU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_AHU_share_cooling = dfBest["VCC to AHU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W = \
                                dfBest["Nominal Power single effect ACH to AHU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W = \
                                dfBest["Nominal Power single effect ACH to AHU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_AHU_share_cooling == 1:
                            Disconnected_direct_expansion_to_AHU_capacity_cooling_W = \
                                dfBest["Nominal Power DX to AHU [W]"].iloc[0]

                        if Disconnected_VCC_to_AHU_share_cooling == 1:
                            Disconnected_VCC_to_AHU_capacity_cooling_W = \
                                dfBest["Nominal Power VCC to AHU [W]"].iloc[0]

                    disconnected_capacity = dict(building_name=building_names[i],
                                                 Disconnected_Boiler_BG_share=Disconnected_Boiler_BG_share_heating,
                                                 Disconnected_Boiler_BG_capacity_W=Disconnected_Boiler_BG_capacity_heating_W,
                                                 Disconnected_Boiler_NG_share=Disconnected_Boiler_NG_share_heating,
                                                 Disconnected_Boiler_NG_capacity_W=Disconnected_Boiler_NG_capacity_heating_W,
                                                 Disconnected_FC_share=Disconnected_FC_share_heating,
                                                 Disconnected_FC_capacity_W=Disconnected_FC_capacity_heating_W,
                                                 Disconnected_GHP_share=Disconnected_GHP_share_heating,
                                                 Disconnected_GHP_capacity_W=Disconnected_GHP_capacity_heating_W,
                                                 Disconnected_VCC_to_AHU_share_cooling=Disconnected_VCC_to_AHU_share_cooling,
                                                 Disconnected_VCC_to_AHU_capacity_cooling_W=Disconnected_VCC_to_AHU_capacity_cooling_W,
                                                 Disconnected_VCC_to_ARU_share_cooling=Disconnected_VCC_to_ARU_share_cooling,
                                                 Disconnected_VCC_to_ARU_capacity_cooling_W=Disconnected_VCC_to_ARU_capacity_cooling_W,
                                                 Disconnected_VCC_to_SCU_share_cooling=Disconnected_VCC_to_SCU_share_cooling,
                                                 Disconnected_VCC_to_SCU_capacity_cooling_W=Disconnected_VCC_to_SCU_capacity_cooling_W,
                                                 Disconnected_VCC_to_AHU_ARU_share_cooling=Disconnected_VCC_to_AHU_ARU_share_cooling,
                                                 Disconnected_VCC_to_AHU_ARU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_capacity_cooling_W,
                                                 Disconnected_VCC_to_AHU_SCU_share_cooling=Disconnected_VCC_to_AHU_SCU_share_cooling,
                                                 Disconnected_VCC_to_AHU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_SCU_capacity_cooling_W,
                                                 Disconnected_VCC_to_ARU_SCU_share_cooling=Disconnected_VCC_to_ARU_SCU_share_cooling,
                                                 Disconnected_VCC_to_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_ARU_SCU_capacity_cooling_W,
                                                 Disconnected_VCC_to_AHU_ARU_SCU_share_cooling=Disconnected_VCC_to_AHU_ARU_SCU_share_cooling,
                                                 Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_SCU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_SCU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W,
                                                 Disconnected_direct_expansion_to_AHU_share_cooling=Disconnected_direct_expansion_to_AHU_share_cooling,
                                                 Disconnected_direct_expansion_to_AHU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_ARU_share_cooling=Disconnected_direct_expansion_to_ARU_share_cooling,
                                                 Disconnected_direct_expansion_to_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_SCU_share_cooling=Disconnected_direct_expansion_to_SCU_share_cooling,
                                                 Disconnected_direct_expansion_to_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_SCU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_AHU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_SCU_share_cooling,
                                                 Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_AHU_ARU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_share_cooling,
                                                 Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_ARU_SCU_share_cooling,
                                                 Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling,
                                                 Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W)

                intermediate_capacities.append(disconnected_capacity)
            disconnected_capacities.append(dict(network=network, disconnected_capacity=intermediate_capacities))


        # Based on the slave data, capacities corresponding to the centralized network are calculated in the following
        # script. Note that irrespective of the number of technologies used in an individual, the length of the dict
        # is constant
        for i, ind in enumerate(slavedata_list):
            if ind.Furn_Moist_type == "wet":
                Furnace_wet = ind.Furnace_on
                Furnace_wet_capacity_W = ind.Furnace_Q_max
            elif ind.Furn_Moist_type == "dry":
                Furnace_dry = ind.Furnace_on
                Furnace_dry_capacity_W = ind.Furnace_Q_max
            if ind.gt_fuel == "NG":
                CHP_NG = ind.CC_on
                CHP_NG_capacity_W = ind.CC_GT_SIZE
                Base_boiler_NG = ind.Boiler_on
                Base_boiler_NG_capacity_W = ind.Boiler_Q_max
                Peak_boiler_NG = ind.BoilerPeak_on
                Peak_boiler_NG_capacity_W = ind.BoilerPeak_Q_max
            elif ind.gt_fuel == "BG":
                CHP_BG = ind.CC_on
                CHP_BG_capacity_W = ind.CC_GT_SIZE
                Base_boiler_BG = ind.Boiler_on
                Base_boiler_BG_capacity_W = ind.Boiler_Q_max
                Peak_boiler_BG = ind.BoilerPeak_on
                Peak_boiler_BG_capacity_W = ind.BoilerPeak_Q_max

            HP_Lake = ind.HP_Lake_on
            HP_Lake_capacity_W = ind.HPLake_maxSize
            HP_Sewage = ind.HP_Sew_on
            HP_Sewage_capacity_W = ind.HPSew_maxSize
            GHP = ind.GHP_on
            GHP_capacity_W = ind.GHP_number * GHP_HMAX_SIZE
            PV = pop[i][N_HEAT * 2 + N_HR]
            PV_capacity_W = ind.SOLAR_PART_PV * solar_features.A_PV_m2 * N_PV * 1000
            if config.optimization.isheating:
                PVT = pop[i][N_HEAT * 2 + N_HR + 2]
                PVT_capacity_W = ind.SOLAR_PART_PVT * solar_features.A_PVT_m2 * N_PVT * 1000
            else:
                PVT = 0
                PVT_capacity_W = 0

            SC_ET = pop[i][N_HEAT * 2 + N_HR + 4]
            SC_ET_capacity_W = ind.SOLAR_PART_SC_ET * solar_features.A_SC_ET_m2 * 1000
            SC_FP = pop[i][N_HEAT * 2 + N_HR + 6]
            SC_FP_capacity_W = ind.SOLAR_PART_SC_FP * solar_features.A_SC_FP_m2 * 1000

            VCC = ind.VCC_on
            VCC_capacity_W = ind.VCC_cooling_size
            Absorption_Chiller = ind.Absorption_Chiller_on
            Absorption_Chiller_capacity_W = ind.Absorption_chiller_size
            Lake_cooling = ind.Lake_cooling_on
            Lake_cooling_capacity_W = ind.Lake_cooling_size
            storage_cooling = ind.storage_cooling_on
            storage_cooling_capacity_W = ind.Storage_cooling_size

            capacity = dict(ind=i, generation=genCP,
                            Furnace_wet=Furnace_wet, Furnace_wet_capacity_W=Furnace_wet_capacity_W,
                            Furnace_dry=Furnace_dry, Furnace_dry_capacity_W=Furnace_dry_capacity_W,
                            CHP_NG=CHP_NG, CHP_NG_capacity_W=CHP_NG_capacity_W,
                            CHP_BG=CHP_BG, CHP_BG_capacity_W=CHP_BG_capacity_W,
                            Base_boiler_BG=Base_boiler_BG, Base_boiler_BG_capacity_W=Base_boiler_BG_capacity_W,
                            Base_boiler_NG=Base_boiler_NG, Base_boiler_NG_capacity_W=Base_boiler_NG_capacity_W,
                            Peak_boiler_BG=Peak_boiler_BG, Peak_boiler_BG_capacity_W=Peak_boiler_BG_capacity_W,
                            Peak_boiler_NG=Peak_boiler_NG, Peak_boiler_NG_capacity_W=Peak_boiler_NG_capacity_W,
                            HP_Lake=HP_Lake, HP_Lake_capacity_W=HP_Lake_capacity_W,
                            HP_Sewage=HP_Sewage, HP_Sewage_capacity_W=HP_Sewage_capacity_W,
                            GHP=GHP, GHP_capacity_W=GHP_capacity_W,
                            PV=PV, PV_capacity_W=PV_capacity_W,
                            PVT=PVT, PVT_capacity_W=PVT_capacity_W,
                            SC_ET=SC_ET, SC_ET_capacity_W=SC_ET_capacity_W,
                            SC_FP=SC_FP, SC_FP_capacity_W=SC_FP_capacity_W,
                            VCC=VCC, VCC_capacity_W=VCC_capacity_W,
                            Absorption_Chiller=Absorption_Chiller, Absorption_Chiller_capacity_W=Absorption_Chiller_capacity_W,
                            Lake_cooling=Lake_cooling, Lake_cooling_capacity_W=Lake_cooling_capacity_W,
                            storage_cooling=storage_cooling, storage_cooling_capacity_W=storage_cooling_capacity_W)
            capacities.append(capacity)
        # Save initial population
        print "Save Initial population \n"

        with open(locator.get_optimization_checkpoint_initial(),"wb") as fp:
            cp = dict(population=pop, generation=0, networkList=DHN_network_list, epsIndicator=[], testedPop=[],
                      population_fitness=fitnesses, capacities=capacities, disconnected_capacities=disconnected_capacities,
                      halloffame=halloffame, halloffame_fitness=halloffame_fitness)
            json.dump(cp, fp)

    else:
        print "Recover from CP " + str(genCP) + "\n"
        # import the checkpoint based on the genCP
        with open(locator.get_optimization_checkpoint(genCP), "rb") as fp:
            cp = json.load(fp)
            pop = toolbox.population(n=config.optimization.initialind)
            for i in xrange(len(pop)):
                for j in xrange(len(pop[i])):
                    pop[i][j] = cp['population'][i][j]
            DHN_network_list = DHN_network_list
            DCN_network_list = DCN_network_list
            epsInd = cp["epsIndicator"]

            for ind in pop:
                evaluation.checkNtw(ind, DHN_network_list, DCN_network_list, locator, gv, config, building_names)

            for i, ind in enumerate(pop):
                a = objective_function(i, ind, genCP)
                costs_list.append(a[0])
                co2_list.append(a[1])
                prim_list.append(a[2])
                slavedata_list.append(a[3])
                function_evals = function_evals + 1  # keeping track of number of function evaluations

            for i in range(len(costs_list)):
                fitnesses.append([costs_list[i], co2_list[i], prim_list[i]])

            # linking every individual with the corresponding fitness, this also keeps a track of the number of function
            # evaluations. This can further be used as a stopping criteria in future
            for ind, fit in zip(pop, fitnesses):
                ind.fitness.values = fit

    proba, sigmap = PROBA, SIGMAP

    # variables used for generating graphs
    # graphs are being generated for every generation, it is shown in 2D plot with colorscheme for the 3rd objective
    xs = [((objectives[0])) for objectives in fitnesses]  # Costs
    ys = [((objectives[1])) for objectives in fitnesses]  # GHG emissions
    zs = [((objectives[2])) for objectives in fitnesses]  # MJ

    # normalization is used for optimization metrics as the objectives are all present in different scales
    # to have a consistent value for normalization, the values of the objectives of the initial generation are taken
    normalization = [max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)]

    xs = [a / 10**6 for a in xs]
    ys = [a / 10**6 for a in ys]
    zs = [a / 10**6 for a in zs]

    # plot showing the Pareto front of every generation
    # parameters corresponding to Pareto front
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # cm = plt.get_cmap('jet')
    # cNorm = matplotlib.colors.Normalize(vmin=min(zs), vmax=max(zs))
    # scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
    # ax.scatter(xs, ys, c=scalarMap.to_rgba(zs), s=50, alpha=0.8)
    # ax.set_xlabel('TAC [$ Mio/yr]')
    # ax.set_ylabel('GHG emissions [x 10^3 ton CO2-eq]')
    # scalarMap.set_array(zs)
    # fig.colorbar(scalarMap, label='Primary Energy [x 10^3 GJ]')
    # plt.grid(True)
    # plt.rcParams['figure.figsize'] = (20, 10)
    # plt.rcParams.update({'font.size': 12})
    # plt.gcf().subplots_adjust(bottom=0.15)
    # plt.savefig(os.path.join(locator.get_plots_folder(), "pareto_" + str(genCP) + ".png"))
    # plt.clf()

    # Evolution starts !

    g = genCP
    stopCrit = False # Threshold for the Epsilon indicator, Not used

    while g < config.optimization.ngen and not stopCrit and ( time.clock() - t0 ) < config.optimization.maxtime :

        # Initialization of variables
        DHN_network_list = ["1" * nBuildings]
        costs_list = []
        co2_list = []
        prim_list = []
        valid_pop = []
        costs_list_invalid_ind = []
        co2_list_invalid_ind = []
        prim_list_invalid_ind = []
        slavedata_list_invalid_ind = []
        fitnesses_invalid_ind = []
        capacities = []
        disconnected_capacities = []
        Furnace_wet = 0
        Furnace_wet_capacity_W = 0
        Furnace_dry = 0
        Furnace_dry_capacity_W = 0
        CHP_NG = 0
        CHP_NG_capacity_W = 0
        CHP_BG = 0
        CHP_BG_capacity_W = 0
        Base_boiler_BG = 0
        Base_boiler_BG_capacity_W = 0
        Base_boiler_NG = 0
        Base_boiler_NG_capacity_W = 0
        Peak_boiler_BG = 0
        Peak_boiler_BG_capacity_W = 0
        Peak_boiler_NG = 0
        Peak_boiler_NG_capacity_W = 0

        g += 1
        print "Generation", g
        offspring = list(pop)

        # costs_list updates the costs involved in every individual
        # co2_list updates the GHG emissions in terms of CO2
        # prim_list updates the primary energy  corresponding to every individual
        # slavedata_list updates the master_to_slave variables corresponding to every individual. This is used in
        # calculating the capacities of both the centralized and the decentralized system
        for i, ind in enumerate(pop):
            a = ind.fitness.values
            costs_list.append(a[0])
            co2_list.append(a[1])
            prim_list.append(a[2])

        # slavedata_list is initiated at the generation 0 or regenerated when started from a checkpoint
        # this is further used in the first generation from genCP. For the second generation, the slave data of the
        # selected individuals is to be used and this piece of code does this
        if len(slavedata_list) == 0:
            slavedata_list = slavedata_selected

        # Apply crossover and mutation on the pop
        for ind1, ind2 in zip(pop[::2], pop[1::2]):
            child1, child2 = cx.cxUniform(ind1, ind2, proba, nBuildings)
            offspring += [child1, child2]

        for mutant in pop:
            mutant = mut.mutFlip(mutant, proba, nBuildings)
            mutant = mut.mutShuffle(mutant, proba, nBuildings)
            offspring.append(mut.mutGU(mutant, proba))

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        for ind in invalid_ind:
            evaluation.checkNtw(ind, DHN_network_list, DCN_network_list, locator, gv, config, building_names)

        for i, ind in enumerate(invalid_ind):
            a = objective_function(i, ind, g)
            costs_list_invalid_ind.append(a[0])
            co2_list_invalid_ind.append(a[1])
            prim_list_invalid_ind.append(a[2])
            slavedata_list_invalid_ind.append(a[3])
            valid_pop.append(a[4])
            function_evals = function_evals + 1  # keeping track of number of function evaluations


        zero_data = np.zeros(shape = (len(invalid_ind), len(columns_of_saved_files)))
        saved_dataframe_for_each_generation = pd.DataFrame(zero_data, columns = columns_of_saved_files)

        invalid_ind[:] = valid_pop
        for i, ind in enumerate(invalid_ind):
            saved_dataframe_for_each_generation['individual'][i] = i
            saved_dataframe_for_each_generation['generation'][i] = g
            for j in range(len(columns_of_saved_files) - 5):
                saved_dataframe_for_each_generation[columns_of_saved_files[j+2]][i] = ind[j]
            saved_dataframe_for_each_generation['TAC'][i] = costs_list_invalid_ind[i]
            saved_dataframe_for_each_generation['CO2 emissions'][i] = co2_list_invalid_ind[i]
            saved_dataframe_for_each_generation['Primary Energy'][i] = prim_list_invalid_ind[i]

        saved_dataframe_for_each_generation.to_csv(locator.get_optimization_individuals_in_generation(g))

        for i in range(len(invalid_ind)):
            fitnesses_invalid_ind.append([costs_list_invalid_ind[i], co2_list_invalid_ind[i], prim_list_invalid_ind[i]])

        for ind, fit in zip(invalid_ind, fitnesses_invalid_ind):
            ind.fitness.values = fit

        pop_compiled = pop
        for i in range(len(invalid_ind)):
            pop_compiled.append(invalid_ind[i])
        slavedata_compiled = slavedata_list
        for i in range(len(slavedata_list_invalid_ind)):
            slavedata_compiled.append(slavedata_list_invalid_ind[i])
        slavedata_selected = []

        # Select the Pareto Optimal individuals
        selection = sel.selectPareto(pop_compiled, config.optimization.initialind)
        fitnesses = []
        for ind in selection:
            fitnesses.append(ind.fitness.values)
        for ind in selection:
            for i in range(len(pop_compiled)):
                if ind == pop_compiled[i]:
                    slavedata_selected.append(slavedata_compiled[i])

        if len(halloffame) <= halloffame_size:
            halloffame.extend(selection)
        else:
            halloffame.extend(selection)
            halloffame = sel.selectPareto(halloffame, halloffame_size)

        for ind in halloffame:
            halloffame_fitness.append(ind.fitness.values)

        # Compute the epsilon criteria [and check the stopping criteria]
        epsInd.append(evaluation.epsIndicator(pop, selection))
        # compute the optimization metrics for every front apart from generation 0
        euclidean_distance, spread = convergence_metric(pop, selection, normalization)

        # The population is entirely replaced by the best individuals

        pop[:] = selection

        # this is done to ensure the ntwList has the same list as the selected pop instead of tested pop
        DHN_network_list = ["1" * nBuildings]
        DCN_network_list = ["1" * nBuildings]
        for ind in pop:
            DHN_barcode, DCN_barcode, DHN_configuration, DCN_configuration = sFn.individual_to_barcode(ind, building_names)
            DHN_network_list.append(DHN_barcode)
            DCN_network_list.append(DCN_barcode)

        DHN_network_list = DHN_network_list[1:]  # done to remove the first individual, which is used for initiation
        DCN_network_list = DCN_network_list[1:]
        # disconnected building capacity is calculated from the networklist of every individual
        # disconnected building have four energy technologies namely Bio-gas Boiler, Natural-gas Boiler, Fuel Cell
        # and Geothermal heat pumps
        # These values are already calculated in 'decentralized_main.py'. This piece of script gets these values from
        # the already created csv files
        if config.optimization.isheating:
            network_list = DHN_network_list
        elif config.optimization.iscooling:
            network_list = DCN_network_list
        for (index, network) in enumerate(network_list):
            intermediate_capacities = []
            for i in range(len(network)):

                Disconnected_Boiler_BG_share_heating = 0
                Disconnected_Boiler_BG_capacity_heating_W = 0
                Disconnected_Boiler_NG_share_heating = 0
                Disconnected_Boiler_NG_capacity_heating_W = 0
                Disconnected_FC_share_heating = 0
                Disconnected_FC_capacity_heating_W = 0
                Disconnected_GHP_share_heating = 0
                Disconnected_GHP_capacity_heating_W = 0

                Disconnected_VCC_to_AHU_share_cooling = 0
                Disconnected_VCC_to_AHU_capacity_cooling_W = 0
                Disconnected_VCC_to_ARU_share_cooling = 0
                Disconnected_VCC_to_ARU_capacity_cooling_W = 0
                Disconnected_VCC_to_SCU_share_cooling = 0
                Disconnected_VCC_to_SCU_capacity_cooling_W = 0
                Disconnected_VCC_to_AHU_ARU_share_cooling = 0
                Disconnected_VCC_to_AHU_ARU_capacity_cooling_W = 0
                Disconnected_VCC_to_AHU_SCU_share_cooling = 0
                Disconnected_VCC_to_AHU_SCU_capacity_cooling_W = 0
                Disconnected_VCC_to_ARU_SCU_share_cooling = 0
                Disconnected_VCC_to_ARU_SCU_capacity_cooling_W = 0
                Disconnected_VCC_to_AHU_ARU_SCU_share_cooling = 0
                Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W = 0

                Disconnected_single_effect_ACH_to_AHU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_ARU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_ARU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_SCU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_SCU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling = 0
                Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W = 0

                Disconnected_direct_expansion_to_AHU_share_cooling = 0
                Disconnected_direct_expansion_to_AHU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_ARU_share_cooling = 0
                Disconnected_direct_expansion_to_ARU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_SCU_share_cooling = 0
                Disconnected_direct_expansion_to_SCU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_AHU_SCU_share_cooling = 0
                Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_AHU_ARU_share_cooling = 0
                Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_ARU_SCU_share_cooling = 0
                Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W = 0
                Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling = 0
                Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W = 0

                if network[i] == "0":
                    if config.optimization.isheating:
                        df = pd.read_csv(locator.get_optimization_disconnected_folder_building_result_heating(building_names[i]))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_Boiler_BG_share_heating = dfBest["BoilerBG Share"].iloc[0]
                        Disconnected_Boiler_NG_share_heating = dfBest["BoilerNG Share"].iloc[0]
                        Disconnected_FC_share_heating = dfBest["FC Share"].iloc[0]
                        Disconnected_GHP_share_heating = dfBest["GHP Share"].iloc[0]

                        if Disconnected_Boiler_BG_share_heating == 1:
                            Disconnected_Boiler_BG_capacity_heating_W = dfBest["Nominal Power"].iloc[0]

                        if Disconnected_Boiler_NG_share_heating == 1:
                            Disconnected_Boiler_NG_capacity_heating_W = dfBest["Nominal Power"].iloc[0]

                        if Disconnected_FC_share_heating == 1:
                            Disconnected_FC_capacity_heating_W = dfBest["Nominal Power"].iloc[0]

                        if Disconnected_GHP_share_heating == 1:
                            Disconnected_GHP_capacity_heating_W = dfBest["Nominal Power"].iloc[0]

                        if (Disconnected_FC_share_heating == 0 and Disconnected_Boiler_BG_share_heating == 0 and Disconnected_GHP_share_heating != 0 and Disconnected_Boiler_NG_share_heating != 0):
                            Disconnected_Boiler_NG_capacity_heating_W = dfBest["Nominal Power"].iloc[0] / Disconnected_Boiler_NG_share_heating
                            Disconnected_GHP_capacity_heating_W = dfBest["Nominal Power"].iloc[0] / Disconnected_GHP_share_heating

                        disconnected_capacity = dict(building_name=building_names[i],
                                                     Disconnected_Boiler_BG_share=Disconnected_Boiler_BG_share_heating,
                                                     Disconnected_Boiler_BG_capacity_W=Disconnected_Boiler_BG_capacity_heating_W,
                                                     Disconnected_Boiler_NG_share=Disconnected_Boiler_NG_share_heating,
                                                     Disconnected_Boiler_NG_capacity_W=Disconnected_Boiler_NG_capacity_heating_W,
                                                     Disconnected_FC_share=Disconnected_FC_share_heating,
                                                     Disconnected_FC_capacity_W=Disconnected_FC_capacity_heating_W,
                                                     Disconnected_GHP_share=Disconnected_GHP_share_heating,
                                                     Disconnected_GHP_capacity_W=Disconnected_GHP_capacity_heating_W,
                                                     Disconnected_VCC_to_AHU_share_cooling=Disconnected_VCC_to_AHU_share_cooling,
                                                     Disconnected_VCC_to_AHU_capacity_cooling_W=Disconnected_VCC_to_AHU_capacity_cooling_W,
                                                     Disconnected_VCC_to_ARU_share_cooling=Disconnected_VCC_to_ARU_share_cooling,
                                                     Disconnected_VCC_to_ARU_capacity_cooling_W=Disconnected_VCC_to_ARU_capacity_cooling_W,
                                                     Disconnected_VCC_to_SCU_share_cooling=Disconnected_VCC_to_SCU_share_cooling,
                                                     Disconnected_VCC_to_SCU_capacity_cooling_W=Disconnected_VCC_to_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_ARU_share_cooling=Disconnected_VCC_to_AHU_ARU_share_cooling,
                                                     Disconnected_VCC_to_AHU_ARU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_SCU_share_cooling=Disconnected_VCC_to_AHU_SCU_share_cooling,
                                                     Disconnected_VCC_to_AHU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_ARU_SCU_share_cooling=Disconnected_VCC_to_ARU_SCU_share_cooling,
                                                     Disconnected_VCC_to_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_ARU_SCU_share_cooling=Disconnected_VCC_to_AHU_ARU_SCU_share_cooling,
                                                     Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_share_cooling=Disconnected_direct_expansion_to_AHU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_ARU_share_cooling=Disconnected_direct_expansion_to_ARU_share_cooling,
                                                     Disconnected_direct_expansion_to_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_SCU_share_cooling=Disconnected_direct_expansion_to_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_ARU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_ARU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W)

                    elif config.optimization.iscooling:
                        df = pd.read_csv(
                            locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i],
                            cooling_all_units))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling = dfBest["single effect ACH to AHU_ARU_SCU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_SCU_share_FP_cooling = dfBest["single effect ACH to SCU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling = dfBest["single effect ACH to AHU_ARU_SCU Share (ET)"].iloc[0]
                        Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling = dfBest["DX to AHU_ARU_SCU Share"].iloc[0]
                        Disconnected_VCC_to_AHU_ARU_share_cooling = dfBest["VCC to AHU_ARU Share"].iloc[0]
                        Disconnected_VCC_to_AHU_ARU_SCU_share_cooling = dfBest["VCC to AHU_ARU_SCU Share"].iloc[0]
                        Disconnected_VCC_to_SCU_share_cooling = dfBest["VCC to SCU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W = dfBest["Nominal Power single effect ACH to AHU_ARU_SCU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_SCU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W = dfBest["Nominal Power single effect ACH to SCU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W = dfBest["Nominal Power single effect ACH to AHU_ARU_SCU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling == 1:
                            Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W = dfBest["Nominal Power DX to AHU_ARU_SCU [W]"].iloc[0]

                        if Disconnected_VCC_to_AHU_ARU_share_cooling == 1:
                            Disconnected_VCC_to_AHU_ARU_capacity_cooling_W = dfBest["Nominal Power VCC to AHU_ARU [W]"].iloc[0]

                        if Disconnected_VCC_to_AHU_ARU_SCU_share_cooling == 1:
                            Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W = dfBest["Nominal Power VCC to AHU_ARU_SCU [W]"].iloc[0]

                        if Disconnected_VCC_to_SCU_share_cooling == 1:
                            Disconnected_VCC_to_SCU_capacity_cooling_W = dfBest["Nominal Power VCC to SCU [W]"].iloc[0]

                        disconnected_capacity = dict(building_name=building_names[i],
                                                     Disconnected_Boiler_BG_share=Disconnected_Boiler_BG_share_heating,
                                                     Disconnected_Boiler_BG_capacity_W=Disconnected_Boiler_BG_capacity_heating_W,
                                                     Disconnected_Boiler_NG_share=Disconnected_Boiler_NG_share_heating,
                                                     Disconnected_Boiler_NG_capacity_W=Disconnected_Boiler_NG_capacity_heating_W,
                                                     Disconnected_FC_share=Disconnected_FC_share_heating,
                                                     Disconnected_FC_capacity_W=Disconnected_FC_capacity_heating_W,
                                                     Disconnected_GHP_share=Disconnected_GHP_share_heating,
                                                     Disconnected_GHP_capacity_W=Disconnected_GHP_capacity_heating_W,
                                                     Disconnected_VCC_to_AHU_share_cooling=Disconnected_VCC_to_AHU_share_cooling,
                                                     Disconnected_VCC_to_AHU_capacity_cooling_W=Disconnected_VCC_to_AHU_capacity_cooling_W,
                                                     Disconnected_VCC_to_ARU_share_cooling=Disconnected_VCC_to_ARU_share_cooling,
                                                     Disconnected_VCC_to_ARU_capacity_cooling_W=Disconnected_VCC_to_ARU_capacity_cooling_W,
                                                     Disconnected_VCC_to_SCU_share_cooling=Disconnected_VCC_to_SCU_share_cooling,
                                                     Disconnected_VCC_to_SCU_capacity_cooling_W=Disconnected_VCC_to_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_ARU_share_cooling=Disconnected_VCC_to_AHU_ARU_share_cooling,
                                                     Disconnected_VCC_to_AHU_ARU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_SCU_share_cooling=Disconnected_VCC_to_AHU_SCU_share_cooling,
                                                     Disconnected_VCC_to_AHU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_ARU_SCU_share_cooling=Disconnected_VCC_to_ARU_SCU_share_cooling,
                                                     Disconnected_VCC_to_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_VCC_to_AHU_ARU_SCU_share_cooling=Disconnected_VCC_to_AHU_ARU_SCU_share_cooling,
                                                     Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling,
                                                     Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_share_cooling=Disconnected_direct_expansion_to_AHU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_ARU_share_cooling=Disconnected_direct_expansion_to_ARU_share_cooling,
                                                     Disconnected_direct_expansion_to_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_SCU_share_cooling=Disconnected_direct_expansion_to_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_ARU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_ARU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W,
                                                     Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling,
                                                     Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W)


                    else:
                        raise ValueError("no heating or cooling is required from the centralized plant")
                else:
                    DCN_unit_configuration = saved_dataframe_for_each_generation['DCN unit configuration'][index]

                    if DCN_unit_configuration == 1:  # corresponds to AHU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'ARU_SCU'
                        df = pd.read_csv(
                            locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i],
                            decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_ARU_SCU_share_cooling = dfBest["DX to ARU_SCU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling = dfBest["single effect ACH to ARU_SCU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling = dfBest["single effect ACH to ARU_SCU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_ARU_SCU_share_cooling = dfBest["VCC to ARU_SCU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W = dfBest["Nominal Power single effect ACH to ARU_SCU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W = dfBest["Nominal Power single effect ACH to ARU_SCU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_ARU_SCU_share_cooling == 1:
                            Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W = dfBest["Nominal Power DX to ARU_SCU [W]"].iloc[0]

                        if Disconnected_VCC_to_ARU_SCU_share_cooling == 1:
                            Disconnected_VCC_to_ARU_SCU_capacity_cooling_W = dfBest["Nominal Power VCC to ARU_SCU [W]"].iloc[0]

                    if DCN_unit_configuration == 2:  # corresponds to ARU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'AHU_SCU'
                        df = pd.read_csv(
                            locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i],
                            decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_AHU_SCU_share_cooling = dfBest["DX to AHU_SCU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling = dfBest["single effect ACH to AHU_SCU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling = dfBest["single effect ACH to AHU_SCU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_ARU_SCU_share_cooling = dfBest["VCC to AHU_SCU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W = dfBest["Nominal Power single effect ACH to AHU_SCU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W = dfBest["Nominal Power single effect ACH to AHU_SCU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_AHU_SCU_share_cooling == 1:
                            Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W = dfBest["Nominal Power DX to AHU_SCU [W]"].iloc[0]

                        if Disconnected_VCC_to_AHU_SCU_share_cooling == 1:
                            Disconnected_VCC_to_AHU_SCU_capacity_cooling_W = dfBest["Nominal Power VCC to AHU_SCU [W]"].iloc[0]

                    if DCN_unit_configuration == 3:  # corresponds to SCU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'AHU_ARU'

                        df = pd.read_csv(
                            locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i],
                            decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_AHU_ARU_share_cooling = dfBest["DX to AHU_ARU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling = \
                        dfBest["single effect ACH to AHU_ARU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling = \
                        dfBest["single effect ACH to AHU_ARU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_AHU_ARU_share_cooling = dfBest["VCC to AHU_ARU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W = \
                            dfBest["Nominal Power single effect ACH to AHU_ARU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W = \
                            dfBest["Nominal Power single effect ACH to AHU_ARU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_AHU_ARU_share_cooling == 1:
                            Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W = \
                            dfBest["Nominal Power DX to AHU_ARU [W]"].iloc[0]

                        if Disconnected_VCC_to_AHU_ARU_share_cooling == 1:
                            Disconnected_VCC_to_AHU_ARU_capacity_cooling_W = \
                            dfBest["Nominal Power VCC to AHU_ARU [W]"].iloc[0]

                    if DCN_unit_configuration == 4:  # corresponds to AHU + ARU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'SCU'

                        df = pd.read_csv(
                            locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i],
                            decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_SCU_share_cooling = dfBest["DX to SCU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_SCU_share_FP_cooling = \
                        dfBest["single effect ACH to SCU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_SCU_share_ET_cooling = \
                        dfBest["single effect ACH to SCU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_SCU_share_cooling = dfBest["VCC to SCU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_SCU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W = \
                            dfBest["Nominal Power single effect ACH to SCU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_SCU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W = \
                            dfBest["Nominal Power single effect ACH to SCU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_SCU_share_cooling == 1:
                            Disconnected_direct_expansion_to_SCU_capacity_cooling_W = \
                            dfBest["Nominal Power DX to SCU [W]"].iloc[0]

                        if Disconnected_VCC_to_SCU_share_cooling == 1:
                            Disconnected_VCC_to_SCU_capacity_cooling_W = \
                            dfBest["Nominal Power VCC to SCU [W]"].iloc[0]
                    if DCN_unit_configuration == 5:  # corresponds to AHU + SCU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'ARU'

                        df = pd.read_csv(
                            locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i],
                            decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_ARU_share_cooling = dfBest["DX to ARU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_ARU_share_FP_cooling = \
                        dfBest["single effect ACH to ARU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_ARU_share_ET_cooling = \
                        dfBest["single effect ACH to ARU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_ARU_share_cooling = dfBest["VCC to ARU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_ARU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W = \
                            dfBest["Nominal Power single effect ACH to ARU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_ARU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W = \
                            dfBest["Nominal Power single effect ACH to ARU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_ARU_share_cooling == 1:
                            Disconnected_direct_expansion_to_ARU_capacity_cooling_W = \
                            dfBest["Nominal Power DX to ARU [W]"].iloc[0]

                        if Disconnected_VCC_to_ARU_share_cooling == 1:
                            Disconnected_VCC_to_ARU_capacity_cooling_W = \
                            dfBest["Nominal Power VCC to ARU [W]"].iloc[0]

                    if DCN_unit_configuration == 6:  # corresponds to ARU + SCU in the central plant, so remaining load need to be provided by decentralized plant
                        decentralized_configuration = 'AHU'

                        df = pd.read_csv(
                            locator.get_optimization_disconnected_folder_building_result_cooling(building_names[i],
                            decentralized_configuration))
                        dfBest = df[df["Best configuration"] == 1]
                        Disconnected_direct_expansion_to_AHU_share_cooling = dfBest["DX to AHU Share"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_share_FP_cooling = \
                            dfBest["single effect ACH to AHU Share (FP)"].iloc[0]
                        Disconnected_single_effect_ACH_to_AHU_share_ET_cooling = \
                            dfBest["single effect ACH to AHU Share (ET)"].iloc[0]
                        Disconnected_VCC_to_AHU_share_cooling = dfBest["VCC to AHU Share"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_share_FP_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W = \
                                dfBest["Nominal Power single effect ACH to AHU (FP) [W]"].iloc[0]

                        if Disconnected_single_effect_ACH_to_AHU_share_ET_cooling == 1:
                            Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W = \
                                dfBest["Nominal Power single effect ACH to AHU (ET) [W]"].iloc[0]

                        if Disconnected_direct_expansion_to_AHU_share_cooling == 1:
                            Disconnected_direct_expansion_to_AHU_capacity_cooling_W = \
                                dfBest["Nominal Power DX to AHU [W]"].iloc[0]

                        if Disconnected_VCC_to_AHU_share_cooling == 1:
                            Disconnected_VCC_to_AHU_capacity_cooling_W = \
                                dfBest["Nominal Power VCC to AHU [W]"].iloc[0]
                    disconnected_capacity = dict(building_name=building_names[i],
                                                 Disconnected_Boiler_BG_share=Disconnected_Boiler_BG_share_heating,
                                                 Disconnected_Boiler_BG_capacity_W=Disconnected_Boiler_BG_capacity_heating_W,
                                                 Disconnected_Boiler_NG_share=Disconnected_Boiler_NG_share_heating,
                                                 Disconnected_Boiler_NG_capacity_W=Disconnected_Boiler_NG_capacity_heating_W,
                                                 Disconnected_FC_share=Disconnected_FC_share_heating,
                                                 Disconnected_FC_capacity_W=Disconnected_FC_capacity_heating_W,
                                                 Disconnected_GHP_share=Disconnected_GHP_share_heating,
                                                 Disconnected_GHP_capacity_W=Disconnected_GHP_capacity_heating_W,
                                                 Disconnected_VCC_to_AHU_share_cooling=Disconnected_VCC_to_AHU_share_cooling,
                                                 Disconnected_VCC_to_AHU_capacity_cooling_W=Disconnected_VCC_to_AHU_capacity_cooling_W,
                                                 Disconnected_VCC_to_ARU_share_cooling=Disconnected_VCC_to_ARU_share_cooling,
                                                 Disconnected_VCC_to_ARU_capacity_cooling_W=Disconnected_VCC_to_ARU_capacity_cooling_W,
                                                 Disconnected_VCC_to_SCU_share_cooling=Disconnected_VCC_to_SCU_share_cooling,
                                                 Disconnected_VCC_to_SCU_capacity_cooling_W=Disconnected_VCC_to_SCU_capacity_cooling_W,
                                                 Disconnected_VCC_to_AHU_ARU_share_cooling=Disconnected_VCC_to_AHU_ARU_share_cooling,
                                                 Disconnected_VCC_to_AHU_ARU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_capacity_cooling_W,
                                                 Disconnected_VCC_to_AHU_SCU_share_cooling=Disconnected_VCC_to_AHU_SCU_share_cooling,
                                                 Disconnected_VCC_to_AHU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_SCU_capacity_cooling_W,
                                                 Disconnected_VCC_to_ARU_SCU_share_cooling=Disconnected_VCC_to_ARU_SCU_share_cooling,
                                                 Disconnected_VCC_to_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_ARU_SCU_capacity_cooling_W,
                                                 Disconnected_VCC_to_AHU_ARU_SCU_share_cooling=Disconnected_VCC_to_AHU_ARU_SCU_share_cooling,
                                                 Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_VCC_to_AHU_ARU_SCU_capacity_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_SCU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_SCU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_SCU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_SCU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_SCU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_ARU_SCU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_ARU_SCU_capacity_ET_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_FP_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_FP_cooling_W,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_share_ET_cooling,
                                                 Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W=Disconnected_single_effect_ACH_to_AHU_ARU_SCU_capacity_ET_cooling_W,
                                                 Disconnected_direct_expansion_to_AHU_share_cooling=Disconnected_direct_expansion_to_AHU_share_cooling,
                                                 Disconnected_direct_expansion_to_AHU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_ARU_share_cooling=Disconnected_direct_expansion_to_ARU_share_cooling,
                                                 Disconnected_direct_expansion_to_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_SCU_share_cooling=Disconnected_direct_expansion_to_SCU_share_cooling,
                                                 Disconnected_direct_expansion_to_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_SCU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_AHU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_SCU_share_cooling,
                                                 Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_SCU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_AHU_ARU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_share_cooling,
                                                 Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_ARU_SCU_share_cooling,
                                                 Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_ARU_SCU_capacity_cooling_W,
                                                 Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling=Disconnected_direct_expansion_to_AHU_ARU_SCU_share_cooling,
                                                 Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W=Disconnected_direct_expansion_to_AHU_ARU_SCU_capacity_cooling_W)

                intermediate_capacities.append(disconnected_capacity)
            disconnected_capacities.append(dict(network=network, disconnected_capacity=intermediate_capacities))

        # Based on the slave data, capacities corresponding to the centralized network are calculated in the following
        # script. Note that irrespective of the number of technologies used in an individual, the length of the dict
        # is constant
        for i, ind in enumerate(slavedata_selected):
            if ind.Furn_Moist_type == "wet":
                Furnace_wet = ind.Furnace_on
                Furnace_wet_capacity_W = ind.Furnace_Q_max
            elif ind.Furn_Moist_type == "dry":
                Furnace_dry = ind.Furnace_on
                Furnace_dry_capacity_W = ind.Furnace_Q_max
            if ind.gt_fuel == "NG":
                CHP_NG = ind.CC_on
                CHP_NG_capacity_W = ind.CC_GT_SIZE
                Base_boiler_NG = ind.Boiler_on
                Base_boiler_NG_capacity_W = ind.Boiler_Q_max
                Peak_boiler_NG = ind.BoilerPeak_on
                Peak_boiler_NG_capacity_W = ind.BoilerPeak_Q_max
            elif ind.gt_fuel == "BG":
                CHP_BG = ind.CC_on
                CHP_BG_capacity_W = ind.CC_GT_SIZE
                Base_boiler_BG = ind.Boiler_on
                Base_boiler_BG_capacity_W = ind.Boiler_Q_max
                Peak_boiler_BG = ind.BoilerPeak_on
                Peak_boiler_BG_capacity_W = ind.BoilerPeak_Q_max

            HP_Lake = ind.HP_Lake_on
            HP_Lake_capacity_W = ind.HPLake_maxSize
            HP_Sewage = ind.HP_Sew_on
            HP_Sewage_capacity_W = ind.HPSew_maxSize
            GHP = ind.GHP_on
            GHP_capacity_W = ind.GHP_number * GHP_HMAX_SIZE
            PV = invalid_ind[i][N_HEAT * 2 + N_HR]
            PV_capacity_W = ind.SOLAR_PART_PV * solar_features.A_PV_m2 * N_PV * 1000
            if config.optimization.isheating:
                PVT = invalid_ind[i][N_HEAT * 2 + N_HR + 2]
                PVT_capacity_W = ind.SOLAR_PART_PVT * solar_features.A_PVT_m2 * N_PVT * 1000
            else:
                PVT = 0
                PVT_capacity_W = 0
            SC_ET = invalid_ind[i][N_HEAT * 2 + N_HR + 4]
            SC_ET_capacity_W = ind.SOLAR_PART_SC_ET * solar_features.A_SC_ET_m2 * 1000
            SC_FP = invalid_ind[i][N_HEAT * 2 + N_HR + 6]
            SC_FP_capacity_W = ind.SOLAR_PART_SC_FP * solar_features.A_SC_FP_m2 * 1000

            VCC = ind.VCC_on
            VCC_capacity_W = ind.VCC_cooling_size
            Absorption_Chiller = ind.Absorption_Chiller_on
            Absorption_Chiller_capacity_W = ind.Absorption_chiller_size
            Lake_cooling = ind.Lake_cooling_on
            Lake_cooling_capacity_W = ind.Lake_cooling_size
            storage_cooling = ind.storage_cooling_on
            storage_cooling_capacity_W = ind.Storage_cooling_size

            capacity = dict(ind=i, generation=genCP,
                            Furnace_wet=Furnace_wet, Furnace_wet_capacity_W=Furnace_wet_capacity_W,
                            Furnace_dry=Furnace_dry, Furnace_dry_capacity_W=Furnace_dry_capacity_W,
                            CHP_NG=CHP_NG, CHP_NG_capacity_W=CHP_NG_capacity_W,
                            CHP_BG=CHP_BG, CHP_BG_capacity_W=CHP_BG_capacity_W,
                            Base_boiler_BG=Base_boiler_BG, Base_boiler_BG_capacity_W=Base_boiler_BG_capacity_W,
                            Base_boiler_NG=Base_boiler_NG, Base_boiler_NG_capacity_W=Base_boiler_NG_capacity_W,
                            Peak_boiler_BG=Peak_boiler_BG, Peak_boiler_BG_capacity_W=Peak_boiler_BG_capacity_W,
                            Peak_boiler_NG=Peak_boiler_NG, Peak_boiler_NG_capacity_W=Peak_boiler_NG_capacity_W,
                            HP_Lake=HP_Lake, HP_Lake_capacity_W=HP_Lake_capacity_W,
                            HP_Sewage=HP_Sewage, HP_Sewage_capacity_W=HP_Sewage_capacity_W,
                            GHP=GHP, GHP_capacity_W=GHP_capacity_W,
                            PV=PV, PV_capacity_W=PV_capacity_W,
                            PVT=PVT, PVT_capacity_W=PVT_capacity_W,
                            SC_ET=SC_ET, SC_ET_capacity_W=SC_ET_capacity_W,
                            SC_FP=SC_FP, SC_FP_capacity_W=SC_FP_capacity_W,
                            VCC=VCC, VCC_capacity_W=VCC_capacity_W,
                            Absorption_Chiller=Absorption_Chiller,
                            Absorption_Chiller_capacity_W=Absorption_Chiller_capacity_W,
                            Lake_cooling=Lake_cooling, Lake_cooling_capacity_W=Lake_cooling_capacity_W,
                            storage_cooling=storage_cooling, storage_cooling_capacity_W=storage_cooling_capacity_W)
            capacities.append(capacity)

        xs = [((objectives[0]) / 10 ** 6) for objectives in fitnesses]  # Costs
        ys = [((objectives[1]) / 10 ** 6) for objectives in fitnesses]  # GHG emissions
        zs = [((objectives[2]) / 10 ** 6) for objectives in fitnesses]  # MJ

        # plot showing the Pareto front of every generation

        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # cm = plt.get_cmap('jet')
        # cNorm = matplotlib.colors.Normalize(vmin=min(zs), vmax=max(zs))
        # scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
        # ax.scatter(xs, ys, c=scalarMap.to_rgba(zs), s=50, alpha=0.8)
        # ax.set_xlabel('TAC [$ Mio/yr]')
        # ax.set_ylabel('GHG emissions [x 10^3 ton CO2-eq]')
        # scalarMap.set_array(zs)
        # fig.colorbar(scalarMap, label='Primary Energy [x 10^3 GJ]')
        # plt.grid(True)
        # plt.rcParams['figure.figsize'] = (20, 10)
        # plt.rcParams.update({'font.size': 12})
        # plt.gcf().subplots_adjust(bottom=0.15)
        # plt.savefig(os.path.join(locator.get_plots_folder(), "pareto_" + str(g) + ".png"))
        # plt.clf()

        # Create Checkpoint if necessary
        if g % config.optimization.fcheckpoint == 0:
            print "Create CheckPoint", g, "\n"
            with open(locator.get_optimization_checkpoint(g), "wb") as fp:
                cp = dict(population=pop, generation=g, networkList=DHN_network_list, epsIndicator=epsInd, testedPop=invalid_ind,
                          population_fitness=fitnesses, capacities=capacities, disconnected_capacities=disconnected_capacities,
                          halloffame=halloffame, halloffame_fitness=halloffame_fitness,
                          euclidean_distance=euclidean_distance, spread=spread)
                json.dump(cp, fp)
        slavedata_list = [] # reinitializing to avoid really long lists, as this keeps appending

    if g == config.optimization.ngen:
        print "Final Generation reached"
    else:
        print "Stopping criteria reached"

    # Dataframe with all the individuals whose objective functions are calculated, gathering all the results from
    # multiple generations
    df = pd.read_csv(locator.get_optimization_individuals_in_generation(0))
    for i in range(config.optimization.ngen):
        df = df.append(pd.read_csv(locator.get_optimization_individuals_in_generation(i+1)))
    df.to_csv(locator.get_optimization_all_individuals())
    # Saving the final results
    print "Save final results. " + str(len(pop)) + " individuals in final population"
    print "Epsilon indicator", epsInd, "\n"
    with open(locator.get_optimization_checkpoint_final(), "wb") as fp:
        cp = dict(population=pop, generation=g, networkList=DHN_network_list, epsIndicator=epsInd, testedPop=invalid_ind,
                  population_fitness=fitnesses, capacities=capacities, disconnected_capacities=disconnected_capacities,
                  halloffame=halloffame, halloffame_fitness=halloffame_fitness,
                  euclidean_distance=euclidean_distance, spread=spread)
        json.dump(cp, fp)

    print "Master Work Complete \n"
    print ("Number of function evaluations = " + str(function_evals))

    return pop, epsInd

def convergence_metric(old_front, new_front, normalization):
    #  This function calculates the metrics corresponding to a Pareto-front
    #  combined_euclidean_distance calculates the euclidean distance between the current front and the previous one
    #  it is done by locating the choosing a point on current front and the closest point in the previous front and
    #  calculating normalized euclidean distance

    #  Spread discusses on the spread of the Pareto-front, i.e. how evenly the Pareto front is spaced. This is calculated
    #  by identifying the closest neighbour to a point on the Pareto-front. Distance to each closest neighbour is then
    #  subtracted by the mean distance for all the points on the Pareto-front (i.e. closest neighbors for all points).
    #  The ideal value for this is to be 'zero'

    combined_euclidean_distance = 0

    for indNew in new_front:

        (aNew, bNew, cNew) = indNew.fitness.values
        distance = []
        for i, indOld in enumerate(old_front):
            (aOld, bOld, cOld) = indOld.fitness.values
            distance_mix = ((aNew - aOld) / normalization[0])**2 + ((bNew - bOld) / normalization[1])**2 + ((cNew - cOld) / normalization[2])**2
            distance_mix = round(distance_mix, 5)
            distance.append(np.sqrt(distance_mix))

        combined_euclidean_distance = combined_euclidean_distance + min(distance)

    combined_euclidean_distance = (combined_euclidean_distance) / (len(new_front))

    spread = []
    nearest_neighbor = []

    for i, ind_i in enumerate(new_front):
        spread_i = []
        (cost_i, co2_i, eprim_i) = ind_i.fitness.values
        for j, ind_j in enumerate(new_front):
            (cost_j, co2_j, eprim_j) = ind_j.fitness.values
            if i != j:
                spread_mix = ((cost_i - cost_j) / normalization[0])**2 + ((co2_i - co2_j) / normalization[1])**2 + ((eprim_i - eprim_j) / normalization[2])**2
                spread_mix = round(spread_mix, 5)
                spread.append(np.sqrt(spread_mix))
                spread_i.append(np.sqrt(spread_mix))

        nearest_neighbor.append(min(spread_i))
    average_spread = np.mean(spread)

    nearest_neighbor = [abs(x - average_spread) for x in nearest_neighbor]

    spread_final = np.sum(nearest_neighbor)

    print ('combined euclidean distance = ' + str(combined_euclidean_distance))
    print ('spread = ' + str(spread_final))

    return combined_euclidean_distance, spread_final
