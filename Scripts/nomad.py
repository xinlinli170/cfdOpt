import os
import sys
import ConfigParser

class NOMAD(object):
    """The class of NOMAD
    """

    def __init__(self):
        local_path = os.path.dirname(os.path.realpath(__file__))
        self.nomad_parameter_file_path = local_path + "/nomad/nomad_parameters_file.txt"     
        self.nomad_tmp_file_directory = local_path + "/nomad"

        #load config file
        self.__config = ConfigParser.RawConfigParser()
        local_path = os.path.dirname(os.path.realpath(__file__))
        self.__config.read(local_path + "/cfdOpt_config.ini")

        self.__number_of_threads = self.__config.getint("NOMAD", "num_of_threads")
        self.nomad_path = local_path + self.__config.get("NOMAD", "path")
        self.nomad_MPI_path = local_path + self.__config.get("NOMAD", "path_parallel")

        self.nomad_mpirun = self.__config.get("NOMAD", "mpirun")

    def launch_optimization(self, parameter_files_path=None):
        if parameter_files_path is not None:
            self.nomad_parameter_file_path = parameter_files_path

        if self.__number_of_threads == 1:
            command = self.nomad_path + " " + self.nomad_parameter_file_path +\
                " > " + self.nomad_tmp_file_directory + "/NOMAD.log" +\
                " 2> " + self.nomad_tmp_file_directory + "/NOMAD.error.log"
        else:
            command = self.nomad_mpirun + " -np " + str(self.__number_of_threads + 1) + " " +\
                self.nomad_MPI_path + " " + self.nomad_parameter_file_path +\
                " > " + self.nomad_tmp_file_directory + "/NOMAD.log" +\
                " 2> " + self.nomad_tmp_file_directory + "/NOMAD.error.log"

        os.system(command)

import init_counter
optimization = NOMAD()

if len(sys.argv) == 2:
    optimization.launch_optimization(sys.argv[1])
else:
    optimization.launch_optimization()
