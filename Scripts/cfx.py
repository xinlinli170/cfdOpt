import os
import time

class CFX(object):
    """The class to control the simulation of CFX
    """

    def __init__(self, config):
        self.__config = config

        local_path = os.path.dirname(os.path.realpath(__file__))
        self.cfx_tmp_file_directory = local_path + self.__config.get("CFX", "tmp_file_directory")

        if not os.path.exists(self.cfx_tmp_file_directory):
            os.makedirs(self.cfx_tmp_file_directory)

        self.cfx_case_path = self.__config.get("CFX", "case_path")

        self.def_file_name = self.__config.get("CFX", "def_file_name")
        self.session_file_name = self.__config.get("CFX", "cfx_post_session_file_name")

    def launch_simulation(self):
        number_of_threads = self.__config.getint("CFX", "num_of_threads")
        solver = self.__config.get("CFX", "solver")

        PBS_Script_file_path = self.cfx_tmp_file_directory + "/PBS_Script.sh"
        done_file_path = self.cfx_tmp_file_directory + "/done"

        parallel_method = self.__config.get("CFX", "parallel_method")

        #clean the previous results in the folder
        self.clean_simulation_folder()

        def_file_path = self.cfx_case_path + "/" + self.def_file_name

        if number_of_threads != 1:
            command = solver + " -def " + def_file_path +\
                " -part " + str(number_of_threads) +\
                " -start-method \"" + parallel_method + "\"" +\
                " > " + self.cfx_tmp_file_directory + "/" + "cfx5solve.log" + \
                " 2> " + self.cfx_tmp_file_directory + "/" + "cfx5solve_error.log" + "\n\n"
        else:
            command = solver + " -def " + def_file_path +\
                " > " + self.cfx_tmp_file_directory + "/" + "cfx5solve.log" + \
                " 2> " + self.cfx_tmp_file_directory + "/" + "cfx5solve_error.log" + "\n\n"

        cfx_post = self.__config.get("CFX", "cfx_post")

        session_file_path = self.cfx_case_path + "/" + self.session_file_name
        res_file_path = os.path.splitext(def_file_path)[0] + "_001.res"

        command += cfx_post + " -batch " + session_file_path +\
            " -res " + res_file_path +\
            " > " + self.cfx_tmp_file_directory + "/" + "cfx5post.log" + \
            " 2> " + self.cfx_tmp_file_directory + "/" + "cfx5post_error.log" 

        command += "\n\n"

        #Create the PBS script for CFX simulation
        PBS_Script = ""

        walltime = self.__config.get("CFX", "walltime")

        PBS_Script += "#!/bin/bash\n"
        PBS_Script += "#PBS -A yxu-300-aa\n"
        PBS_Script += "#PBS -l walltime=" + walltime + "\n"
        PBS_Script += "#PBS -l nodes=1:ppn=" + str(number_of_threads) + "\n"
        #PBS_Script += "#PBS -l mem=4gb\n"
        PBS_Script += "#PBS -r n\n\n"
        
        PBS_Script += "cd " + self.cfx_case_path + "\n\n"

        #load CFX module
        PBS_Script += "module load ANSYS_POLY\n\n"

        PBS_Script += command

        PBS_Script += "echo 1 > " + done_file_path + "\n"

        if not os.path.exists(os.path.dirname(PBS_Script_file_path)):
            os.makedirs(os.path.dirname(PBS_Script_file_path))

        with open(PBS_Script_file_path, 'w') as PBS_Script_file:
            PBS_Script_file.write(PBS_Script)

        command = "qsub " + PBS_Script_file_path + " &> " + self.cfx_tmp_file_directory + "/job_id"

        os.system(command)

        local_path = os.path.dirname(os.path.realpath(__file__))

        while True:
            time.sleep(10)
            if os.path.isfile(done_file_path):
                os.system("rm " + done_file_path)
                os.system("rm " + local_path + "/*.sh.*")
                break

    def clean_simulation_folder(self):
        result_file_name = os.path.splitext(self.def_file_name)[0]
        command = "rm -r " + self.cfx_case_path + "/" + result_file_name + "_*"
        os.system(command)
        command = "rm " + self.cfx_case_path + "/" + "output_data.txt"
        os.system(command)

    def save_flow_solution(self, dest_path):

        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        result_file_name = os.path.splitext(self.def_file_name)[0]
        command = "cp -r " + self.cfx_case_path + "/" + result_file_name + "_* " + dest_path
        os.system(command)

        #save profile csv data
        csv_path = self.__config.get("CFX", "profile_csv_path")
        command = "cp " + self.cfx_case_path + csv_path + " " + dest_path
        os.system(command)
 

    def evaluate_objective_function(self):

        result_file_name = self.__config.get("CFX", "cfx_output_file_name")

        result_file_path = self.cfx_case_path + "/" + result_file_name

        with open(result_file_path) as result_file_object:
             result = float(result_file_object.read())

        return result

    def save_debug_file(self, dest_path):

        path = dest_path #place holder
        #save log file
        #shutil.copy(self.openfoam_tmp_file_directory + "/" + \
        #    self.openfoam_foam_log, dest_path)

        #shutil.copy(self.openfoam_tmp_file_directory + "/" + \
        #    "potentialFoam.log", dest_path)

    def plot_residuals(self, dest_path):
        a = 1 #place holder

    def get_p_residuals(self):
        a = 1 #place holder
