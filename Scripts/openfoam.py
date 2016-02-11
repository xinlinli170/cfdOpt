import os
import numpy
import time
import inlet_pressure
import inlet_k_epsilon
import objective_function_openfoam
import profile_1D_fixed_value
import shutil

class OpenFOAM(object):
    """The class
    """

    def __init__(self, config):
        self.__config = config

        local_path = os.path.dirname(os.path.realpath(__file__))        
        self.openfoam_tmp_file_directory = local_path + self.__config.get("OpenFOAM", "tmp_file_directory")

        if not os.path.exists(self.openfoam_tmp_file_directory):
            os.makedirs(self.openfoam_tmp_file_directory)

        solver = self.__config.get("OpenFOAM", "solver")
        
        self.openfoam_foam_log = solver + ".log"
        self.openfoam_error_log = solver + "_error.log"

        self.openfoam_case_path = self.__config.get("OpenFOAM", "case_path")

        self.openfoam_mpirun = self.__config.get("OpenFOAM", "mpirun")

    def load_openfoam_module(self):
        command = self.__config.get("OpenFOAM", "load_OpenFoam_module")
        os.system(command)

    def launch_simulation(self):
        number_of_threads = self.__config.getint("OpenFOAM", "num_of_threads")
        solver = self.__config.get("OpenFOAM", "solver")

        PBS_Script_file_path = self.openfoam_tmp_file_directory + "/PBS_Script.sh"
        done_file_path = self.openfoam_tmp_file_directory + "/done"

        #command w/o potentialFoam
        """
        if number_of_threads != 1:
            command = self.openfoam_mpirun + " -np " + str(number_of_threads) + " " + \
                solver + " -parallel -case " + self.openfoam_case_path + \
                " > " + self.openfoam_tmp_file_directory + "/" + self.openfoam_foam_log +\
                " 2> " + self.openfoam_tmp_file_directory + "/" + self.openfoam_error_log
        else:
            command = solver + " -case " + self.openfoam_case_path + \
                " > " + self.openfoam_tmp_file_directory + "/" + self.openfoam_foam_log +\
                " 2> " + self.openfoam_tmp_file_directory + "/" + self.openfoam_error_log
        """

        if number_of_threads != 1:
            command = self.openfoam_mpirun + " -np " + str(number_of_threads) + " " + \
                "potentialFoam" + " -parallel -case " + self.openfoam_case_path + \
                " > " + self.openfoam_tmp_file_directory + "/" + "potentialFoam.log" +\
                " 2> " + self.openfoam_tmp_file_directory + "/" + "potentialFoam_error.log" +\
                "\n\n"

            command += self.openfoam_mpirun + " -np " + str(number_of_threads) + " " + \
                solver + " -parallel -case " + self.openfoam_case_path + \
                " > " + self.openfoam_tmp_file_directory + "/" + self.openfoam_foam_log +\
                " 2> " + self.openfoam_tmp_file_directory + "/" + self.openfoam_error_log
        else:

            command = "potentialFoam" + " -case " + self.openfoam_case_path + \
                " > " + self.openfoam_tmp_file_directory + "/" + self.openfoam_foam_log +\
                " 2> " + self.openfoam_tmp_file_directory + "/" + self.openfoam_error_log +\
                "\n\n"

            command += solver + " -case " + self.openfoam_case_path + \
                " > " + self.openfoam_tmp_file_directory + "/" + self.openfoam_foam_log +\
                " 2> " + self.openfoam_tmp_file_directory + "/" + self.openfoam_error_log


        #create the PBS script for OpenFOAM simulation
        PBS_Script = ""

        walltime = self.__config.get("OpenFOAM", "walltime")

        PBS_Script += "#!/bin/bash\n"
        PBS_Script += "#PBS -l walltime=" + walltime + "\n"
        PBS_Script += "#PBS -l nodes=1:ppn=" + str(number_of_threads) + "\n"
        #PBS_Script += "#PBS -l mem=4gb\n"
        PBS_Script += "#PBS -r n\n\n"

        #load OpenFOAM module
        #PBS_Script += "module load OpenFOAM/2.3.0\n"
        #PBS_Script += "source /home/apps/Logiciels/OpenFOAM/OpenFOAM-2.3.0/etc/bashrc\n\n"

        #load OpenFOAM module for foam-extend 3.2
        PBS_Script += "module load OpenFOAM/3.2-EXT\n"
        PBS_Script += "source /home/apps/Logiciels/OpenFOAM/OpenFOAM-3.2-ext/foam-extend-3.2/etc/bashrc\n\n"

        PBS_Script += command
        PBS_Script += "\n\n"

        PBS_Script += "echo 1 > " + done_file_path + "\n"

        if not os.path.exists(os.path.dirname(PBS_Script_file_path)):
            os.makedirs(os.path.dirname(PBS_Script_file_path))

        with open(PBS_Script_file_path, 'w') as PBS_Script_file:
            PBS_Script_file.write(PBS_Script)

        command = "qsub " + PBS_Script_file_path + " &> " + self.openfoam_tmp_file_directory + "/job_id"


        os.system(command)
        local_path = os.path.dirname(os.path.realpath(__file__))

        while True:
            time.sleep(10)
            if os.path.isfile(done_file_path):
                os.system("rm " + done_file_path)
                os.system("rm " + local_path + "/*.sh.*")
                break

    def launch_simulation_direct(self):
        number_of_threads = self.__config.getint("OpenFOAM", "num_of_threads")
        solver = self.__config.get("OpenFOAM", "solver")

        if number_of_threads != 1:
            command = self.openfoam_mpirun + " -np " + str(number_of_threads) + " " + \
                solver + " -parallel -case " + self.openfoam_case_path + \
                " > " + self.openfoam_tmp_file_directory + "/" + self.openfoam_foam_log +\
                " 2> " + self.openfoam_tmp_file_directory + "/" + self.openfoam_error_log
        else:
            command = solver + " -case " + self.openfoam_case_path + \
                " > " + self.openfoam_tmp_file_directory + "/" + self.openfoam_foam_log +\
                " 2> " + self.openfoam_tmp_file_directory + "/" + self.openfoam_error_log

        #Run openfoam solver
        os.system(command)

    def update_initial_conditions(self, first_time_step, last_time_step):
        number_of_threads = self.__config.getint("OpenFOAM", "num_of_threads")

        first_time_step = str(first_time_step)
        last_time_step = str(last_time_step)

        if number_of_threads == 1:
            last_time_step_path = self.openfoam_case_path + "/" + last_time_step
            first_time_step_path = self.openfoam_case_path + "/" + first_time_step
            self.__copy_time_step_files(last_time_step_path, first_time_step_path)
        else:
            for i in range(0, number_of_threads):
                last_time_step_path = self.openfoam_case_path + "/processor" + \
                    str(i) + "/" + last_time_step
                first_time_step_path = self.openfoam_case_path + "/processor" +\
                    str(i) + "/" + first_time_step
                self.__copy_time_step_files(last_time_step_path, first_time_step_path)

    def __copy_time_step_files(self, source_time_step_path, destiney_time_step_path):
        #copy all file from src to dest.
        command = "cp -r " + source_time_step_path + "/* " + destiney_time_step_path
        os.system(command)

        #remove extra files
        command = "rm -r " + destiney_time_step_path + "/uniform"
        os.system(command)
        command = "rm -r " + destiney_time_step_path + "/swak4Foam"
        os.system(command)           

    def plot_residuals_with_foamLog(self):
        current_cwd = os.getcwd()
        os.chdir(self.openfoam_tmp_file_directory)
        #foamLog
        command = "foamLog " + self.openfoam_tmp_file_directory + "/" + self.openfoam_foam_log +\
            " &> " + self.openfoam_tmp_file_directory + "/foamLog.log" 
        os.system(command)
 
        #gnuplot
        command = "gnuplot " + self.openfoam_tmp_file_directory + "/plotResiduals.gplt &> plotResiduals.log"
        os.system(command)

        import shutil
        #remove /logs
        shutil.rmtree(self.openfoam_tmp_file_directory + "/logs")
         
        os.chdir(current_cwd)

        return self.openfoam_tmp_file_directory + "/residuals.png"

    def plot_residuals(self, dest_path):
        current_cwd = os.getcwd()
        os.chdir(self.openfoam_tmp_file_directory)

        #gnuplot
        command = "gnuplot " + self.openfoam_tmp_file_directory + "/plotResiduals.gplt &> plotResiduals.log"
        os.system(command)

        shutil.move(self.openfoam_tmp_file_directory + "/residuals.png", dest_path)

        os.chdir(current_cwd)

        return dest_path + "/residuals.png"

    def get_p_residuals(self):

        current_cwd = os.getcwd()
        os.chdir(self.openfoam_tmp_file_directory)

        command = "cat simpleFoam.log | grep 'Solving for p' | cut -d' ' -f9 | tr -d ',' > res_p.log"
        os.system(command)

        lines = [float(line.rstrip('\n')) for line in open('res_p.log')]

        time_steps = -1 * self.__config.getint("OpenFOAM", "time_steps_for_average_final_residuals")

        residuals = numpy.mean(lines[time_steps:])

        os.chdir(current_cwd)

        return residuals

    def evaluate_objective_function(self):
        return float(objective_function_openfoam.ObjectiveFunction(self.__config).get_objective_function())

    def save_flow_solution(self, dest_path):
        number_of_threads = self.__config.getint("OpenFOAM", "num_of_threads")

        
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        #save flow solutions
        if number_of_threads == 1:
            command = "cp -r " + self.openfoam_case_path + "/[0-9]* " + dest_path
            os.system(command)
        else:
            command = "cp -r " + self.openfoam_case_path + "/processor* " + dest_path
            os.system(command)

        #save postProcessing data
        command = "cp -r " + self.openfoam_case_path + "/postProcessing " + dest_path
        os.system(command)

        #save profile csv data
        csv_path = self.__config.get("Profile1DFixedValue", "profile_csv_path")
        command = "cp " + self.openfoam_case_path + csv_path + " " + dest_path
        os.system(command)

    def save_debug_file(self, dest_path):

        #save log file
        shutil.copy(self.openfoam_tmp_file_directory + "/" + \
            self.openfoam_foam_log, dest_path)

        shutil.copy(self.openfoam_tmp_file_directory + "/" + \
            "potentialFoam.log", dest_path)

