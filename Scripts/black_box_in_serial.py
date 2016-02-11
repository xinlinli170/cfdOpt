import ConfigParser
import os
import sys
import re
import shutil
import time
import inlet_pressure
import inlet_k_epsilon
import analytical_model
import dtpmaker
import profile_1D_fixed_value
import profile_1D_CFX
import openfoam
import cfx
import swirl_number_evaluation

class BlackBoxInSerial(object):
    """The class of the simulation blackbox
    """
    def __init__(self, argv, config=None, seed=-1, cwd_lock=None):


        #load input arguments
        if self.__is_nomad_input_file(argv):
            self.__argv = self.__read_nomad_input_file(argv)  #local copy of arguments
        else:
            self.__argv = argv
            del self.__argv[0]

        local_path = os.path.dirname(os.path.realpath(__file__))
        self.__config_file_name = "cfdOpt_config.ini"

        #if no config object provided, load the config template
        if config is None:
            self.__config = ConfigParser.RawConfigParser()  #Inits blackbox config
            self.__config.read(local_path + "/" + self.__config_file_name)  #Load config template
        else:
            self.__config = config  #use config from external function 

        if cwd_lock is None:
            self.__cwd_lock = None
        else:
            self.__cwd_lock = cwd_lock

        #read swirl constraint
        self.swirl_upper_bound = self.__config.getfloat("Optimization", "swirl_upper_bound")
        self.swirl_lower_bound = self.__config.getfloat("Optimization", "swirl_lower_bound")  

        #read residual constraint
        self.openfoam_residual_upper_bound = self.__config.getfloat("OpenFOAM", "p_final_residual_bound")
        self.cfx_residual_upper_bound = self.__config.getfloat("CFX", "p_final_residual_bound")
        self.simulation_solver = self.__config.get("Simulation", "solver").lower()

        self.residual_upper_bound = None

        if self.simulation_solver == "OpenFOAM".lower():
            self.residual_upper_bound = self.openfoam_residual_upper_bound
        elif self.simulation_solver == "CFX".lower():
            self.residual_upper_bound = self.cfx_residual_upper_bound
        
        #self.residual_upper_bound = 1e-4

        #set up for counter
        self.__counter_file_name = "cfdOpt_counter.ini"

        #set up for debug        
        self.__current_time = time.strftime('%j%H%M%S',time.localtime(time.time()))
        self.__debug_file_directory = local_path + "/debug/" +\
            self.__current_time + "-" + str(seed)  #dir for debug file

        #path for store flow solutions
        self.__flow_solutions_directory = self.__config.get("cfdOpt", "scratch_path") +\
            self.__config.get("Simulation", "flow_solutions_directory") + "/" +\
            self.__current_time + "-" + str(seed)


    def launch(self):
        self.set_up_inlet_velocity_profile()

        if self.__is_swirl_satisfy_constraint(): 
            self.launch_simulation()
            self.save_debug_file()

            if not self.__is_residual_satisfy_constraint():
                self.__result = 1e20
            else: 
                self.__result = self.get_result()
                if self.__cwd_lock is not None:
                    self.__cwd_lock.acquire()
                    self.update_optimization_counter()
                    self.__cwd_lock.release()
                else:
                    self.update_optimization_counter()
                self.save_flow_solution()
                #self.update_initial_conditions() #no longer needed because use potentialFoam to initialize simulation
        else:
            self.__result = 1e20  

    def set_up_inlet_velocity_profile(self):
        if self.simulation_solver == "OpenFOAM".lower():
            self.set_up_inlet_velocity_profile_for_openfoam()
        elif self.simulation_solver == "CFX".lower():
            self.set_up_inlet_velocity_profile_for_cfx()

    def __is_swirl_satisfy_constraint(self, swirl=None):
        if swirl is None:
            swirl = self.__get_swirl_number()
        return True if swirl > self.swirl_lower_bound and swirl < self.swirl_upper_bound else False

    def __is_residual_satisfy_constraint(self, residual=None):
        if residual is None:
            residual = self.residual
        return True if residual < self.residual_upper_bound else False

    def __is_nomad_input_file(self, argv):
        return True if len(argv) == 2 and "nomad" in argv[1] else False

    def is_nomad_input_file(self, argv):
        return True if len(argv) == 2 and "nomad" in argv[1] else False

    def __read_nomad_input_file(self, argv):
        with open(argv[1], 'r') as nomad_input:
            nomad_input_data = nomad_input.read().splitlines()[0].split(" ")
        return nomad_input_data

    def set_up_inlet_velocity_profile_for_openfoam(self):

        self.__inlet_profile_model = self.__config.get("Optimization", "inlet_velocity_profile_model").lower()

        if self.__inlet_profile_model == "analyticalModel".lower():
            self.__arguments_for_analytical_model()
            model = analytical_model.AnalyticalModel(self.__config)
        elif self.__inlet_profile_model == "dtpmaker".lower():
            self.__arguments_for_dtpmaker()
            model = dtpmaker.DtpMaker(self.__config, self.__cwd_lock)
        else:
            print "Invalid inlet velocity inlet_profile model!"
            exit(1)
        
        self.inlet_velocity_profile = model.inlet_velocity_profile
        self.inlet_pressure = inlet_pressure.Pressure(self.__config, self.inlet_velocity_profile)
        self.inlet_k_epsilon = inlet_k_epsilon.KEpsilon(self.__config, self.inlet_velocity_profile)

        openfoam_profile = profile_1D_fixed_value.OF1DVelocityProfile(self.__config, self.inlet_velocity_profile,
            self.inlet_k_epsilon, self.inlet_pressure)                
        openfoam_profile.set_profile()

    def set_up_inlet_velocity_profile_for_cfx(self):

        self.__inlet_profile_model = self.__config.get("Optimization", "inlet_velocity_profile_model").lower()

        if self.__inlet_profile_model == "analyticalModel".lower():
            self.__arguments_for_analytical_model()
            model = analytical_model.AnalyticalModel(self.__config)
        elif self.__inlet_profile_model == "dtpmaker".lower():
            self.__arguments_for_dtpmaker()
            model = dtpmaker.DtpMaker(self.__config, self.__cwd_lock)
        else:
            print "Invalid inlet velocity inlet_profile model!"
            exit(1)

        self.inlet_velocity_profile = model.inlet_velocity_profile
        self.inlet_pressure = inlet_pressure.Pressure(self.__config, self.inlet_velocity_profile)
        self.inlet_k_epsilon = inlet_k_epsilon.KEpsilon(self.__config, self.inlet_velocity_profile)

        cfx_profile = profile_1D_CFX.CFX1DVelocityProfile(self.__config, self.inlet_velocity_profile,
            self.inlet_k_epsilon, self.inlet_pressure)

        cfx_profile.set_profile()


    def launch_simulation(self):
        if self.simulation_solver == "OpenFOAM".lower():
            self.__simulation = openfoam.OpenFOAM(self.__config)
        elif self.simulation_solver == "CFX".lower():
            self.__simulation = cfx.CFX(self.__config)

        self.__simulation.launch_simulation() 
        self.__result = self.__simulation.evaluate_objective_function()#float(objective_function.ObjectiveFunction(self.__config).get_objective_function())

    def save_debug_file(self):

        debug_file_data = ""
        debug_file_name = "/debug.txt"
        swirl = self.__get_swirl_number()

        if self.__inlet_profile_model == "analyticalModel".lower():
            debug_file_data = self.__debug_info_for_analytical_model(debug_file_data)
        
        if self.__inlet_profile_model == "dtpmaker".lower():
            debug_file_data = self.__debug_info_for_dtpmaker(debug_file_data)

        debug_file_data += "Swirl = " + str(swirl) + "\n"
        debug_file_data += "Obj = " + str(self.__result) + "\n"

        #write debug.txt
        if not os.path.exists(os.path.dirname(self.__debug_file_directory + debug_file_name)):
            os.makedirs(os.path.dirname(self.__debug_file_directory + debug_file_name))

        with open(self.__debug_file_directory + debug_file_name, 'w+') as debug_file:
            debug_file.write(debug_file_data)

        #save log file
        self.__simulation.save_debug_file(self.__debug_file_directory)

        #cwd lock for plot residuals
        if self.__cwd_lock is not None:
            self.__cwd_lock.acquire()
        
        #plot and save residuals
        plot_residuals_path = self.__simulation.plot_residuals(self.__debug_file_directory)

        #shutil.move(plot_residuals_path, self.__debug_file_directory)

        self.residual = self.__simulation.get_p_residuals()

        if self.__cwd_lock is not None:
            self.__cwd_lock.release()

               
        #write config.ini file
        with open(self.__debug_file_directory + "/config.ini", 'w+') as debug_config_file:
            self.__config.write(debug_config_file)

    def __debug_info_for_dtpmaker(self, debug_file_data):
        debug_file_data += "Va = " + str(self.Va) + "\n"
        debug_file_data += "Vt = " + str(self.Vt) + "\n" 
        return debug_file_data

    def __debug_info_for_analytical_model(self, debug_file_data):

        #Scripts, self.Omega0, self.Omega1, self.Omega2, self.U0, self.U1, self.U2, self.R1, self.R2 = self.__argv

        debug_file_data += "Omega0 = " + str(self.Omega0) + "\n"
        debug_file_data += "Omega1 = " + str(self.Omega1) + "\n"
        debug_file_data += "Omega2 = " + str(self.Omega2) + "\n"
        debug_file_data += "U0 = " + str(self.U0) + "\n"
        debug_file_data += "U1 = " + str(self.U1) + "\n"
        debug_file_data += "U2 = " + str(self.U2) + "\n"
        debug_file_data += "R1 = " + str(self.R1) + "\n"
        debug_file_data += "R2 = " + str(self.R2) + "\n"

        return debug_file_data

    def __get_swirl_number(self):
        swirl = swirl_number_evaluation.SwirlNumberEvaluation(
            self.inlet_velocity_profile).get_swirl_number()
        return swirl

    def output_result(self):
        print self.__result if not self.__is_hit_extreme_barrier() else 1e20

    def get_result(self):
        return self.__result if not self.__is_hit_extreme_barrier() else 1e20

    def __arguments_for_analytical_model(self):

        if len(self.__argv) != 8:
            print "Wrong input arguments"
            exit(1) 

        self.Omega0, self.Omega1, self.Omega2, self.U0, self.U1, self.U2, self.R1, self.R2 = self.__argv
        
        self.__config.set("AnalyticalModel", "Omega0", self.Omega0)
        self.__config.set("AnalyticalModel", "Omega1", self.Omega1)
        self.__config.set("AnalyticalModel", "Omega2", self.Omega2)

        self.__config.set("AnalyticalModel", "U0", self.U0)
        self.__config.set("AnalyticalModel", "U1", self.U1)
        self.__config.set("AnalyticalModel", "U2", self.U2)

        self.__config.set("AnalyticalModel", "R1", self.R1)
        self.__config.set("AnalyticalModel", "R2", self.R2)


    def __arguments_for_dtpmaker(self):

        num_control_points = self.__config.getint("dtpmaker", "num_of_control_points")

        if len(self.__argv) != (2 * num_control_points):
            print "Wrong input arguments"
            exit(1)

        self.Va = []
        self.Vt = []

        for i in range(0, num_control_points):
            self.Va.append(float(self.__argv[i]))

        for i in range(num_control_points, len(self.__argv)):
            self.Vt.append(float(self.__argv[i]))

        self.__config.set("dtpmaker", "Va", self.Va)
        self.__config.set("dtpmaker", "Vt", self.Vt)

    def update_initial_conditions(self):
        self.__simulation.update_initial_conditions(0, 2000)

    def update_optimization_counter(self):
        #read counter file info
        optimization_counter = ConfigParser.RawConfigParser()
        local_path = os.path.dirname(os.path.realpath(__file__))
        optimization_counter.read(local_path + "/" + self.__counter_file_name)
        self.__current_best_objective_function = optimization_counter.getfloat(
            "Counter", "current_best_objective_function")
        num_of_simulations = optimization_counter.getint(
            "Counter", "num_of_simulations")
        num_of_successful_simulations = optimization_counter.getint(
            "Counter", "num_of_successful_simulations")

        #update counter info
        num_of_simulations += 1

        if self.__is_successful_simulation():
            num_of_successful_simulations += 1

        if self.__is_found_better_result():
            self.__current_best_objective_function = self.__result
      
        optimization_counter.set("Counter", "current_best_objective_function",
            self.__current_best_objective_function)

        optimization_counter.set("Counter", "num_of_simulations",
            num_of_simulations)
        optimization_counter.set("Counter", "num_of_successful_simulations",
            num_of_successful_simulations)

        #write counter file
        with open(local_path + "/" + self.__counter_file_name, "w+") as counter_file:
            optimization_counter.write(counter_file)

        #update config file (for debug)
        self.__config.set("Optimization", "current_best_objective_function", 
            self.__current_best_objective_function)
        self.__config.set("Optimization", "num_of_simulations", 
            num_of_simulations)
        self.__config.set("Optimization", "num_of_successful_simulations", 
            num_of_successful_simulations)

    def save_flow_solution(self):
        if self.__is_hit_extreme_barrier():
            self.__simulation.save_flow_solution(self.__flow_solutions_directory\
                + "-Fail")
        if self.__is_found_better_result():
            self.__simulation.save_flow_solution(self.__flow_solutions_directory\
                + "-Success")

    def __is_hit_extreme_barrier(self):
        return True if ((not self.__is_swirl_satisfy_constraint()) or self.__result < 0) else False

    def __is_found_better_result(self):
        return True if self.__result <= self.__current_best_objective_function else False

    def __is_successful_simulation(self):
        return True if not self.__is_hit_extreme_barrier() else False

