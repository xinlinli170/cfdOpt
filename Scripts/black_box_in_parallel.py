from black_box_in_serial import BlackBoxInSerial
import os
import sys
import ConfigParser

class BlackBoxInParallel(BlackBoxInSerial):
    """
    """

    def __init__(self, argv, config=None, seed=None, cwd_lock=None):

        self.__argv = argv

        local_path = os.path.dirname(os.path.realpath(__file__))
        self.__config_file_name = "cfdOpt_config.ini"

        #if no config object provided, load the config template
        if config is None:
            self.__config = ConfigParser.RawConfigParser()  #Inits blackbox config
            self.__config.read(local_path + "/" + self.__config_file_name)  #Load config template
        else:
            self.__config = config  #use config from external function

        #if no seed provided, use the seed in the input file name
        if seed is None:
            self.__black_box_seed = self.__get_the_seed(argv)
        else:
            self.__black_box_seed = seed

        if cwd_lock is None:
            self.__cwd_lock = None
        else:
            self.__cwd_lock = cwd_lock

        BlackBoxInSerial.__init__(self, self.__argv, self.__config, self.__black_box_seed, cwd_lock)

    def launch(self):
        self.set_up_for_parallel()
        BlackBoxInSerial.launch(self)
        
    def __get_the_seed(self, argv):
        if BlackBoxInSerial.is_nomad_input_file(self, argv):
            input_file_name = argv[1]
            seed = input_file_name.split('.')[-3]
        else:
            print "Wrong input arguments!"
            exit(1)

        return seed

    def set_up_for_parallel(self):
        self.__modify_black_box_config()

        simulation_solver = self.__config.get("Simulation", "solver").lower()

        if simulation_solver == "OpenFOAM".lower():
            self.__copy_openfoam_case()
            self.__copy_plot_file()
        elif simulation_solver == "CFX".lower():
            self.__copy_cfx_case()
        else:
            print "Wrong simulation solver!"


    def get_the_black_box_seed(self):
        return self.__black_box_seed

    def __modify_black_box_config(self):
        #set up for openfoam case directory
        self.__openfoam_template_case_path = self.__config.get("OpenFOAM",
            "case_path")
        self.__cfx_template_case_path = self.__config.get("CFX", "case_path")

#        self.__openfoam_case_path = self.__openfoam_template_case_path + "-" +\
#            str(self.__black_box_seed)

        #simulation case path for the cluster
        self.__scratch_folder = self.__config.get("cfdOpt", "scratch_path")
        self.__openfoam_case_path = self.__scratch_folder + "/cfdOpt_simulation_" + \
            str(self.__black_box_seed)
        self.__cfx_case_path = self.__openfoam_case_path

        self.__config.set("OpenFOAM", "case_path", self.__openfoam_case_path)
        self.__config.set("CFX", "case_path", self.__cfx_case_path)

        #set up for openfoam temp directory
        self.__ori_openfoam_tmp_path = self.__config.get("OpenFOAM", "tmp_file_directory")
        self.__openfoam_tmp_path = self.__ori_openfoam_tmp_path + "/" + str(self.__black_box_seed)
        self.__config.set("OpenFOAM", "tmp_file_directory", self.__openfoam_tmp_path)

        #set up for cfx temp directory
        self.__ori_cfx_tmp_path = self.__config.get("CFX", "tmp_file_directory")
        self.__cfx_tmp_path = self.__ori_cfx_tmp_path + "/" + str(self.__black_box_seed)
        self.__config.set("CFX", "tmp_file_directory", self.__cfx_tmp_path)

        #set up for dtpmaker temp directory
        dtpmaker_tmp_path = self.__config.get("dtpmaker", "tmp_file_directory")
        dtpmaker_tmp_path += "/" + str(self.__black_box_seed)
        self.__config.set("dtpmaker", "tmp_file_directory", dtpmaker_tmp_path)

    def __copy_openfoam_case(self):
        command = "cp -r " + self.__openfoam_template_case_path + "/* " +\
            self.__openfoam_case_path

        if not os.path.exists(self.__openfoam_case_path):
            os.makedirs(self.__openfoam_case_path)
            os.system(command)

    def __copy_cfx_case(self):
        command = "cp -r " + self.__cfx_template_case_path + "/* " +\
            self.__cfx_case_path

        if not os.path.exists(self.__cfx_case_path):
            os.makedirs(self.__cfx_case_path)
            os.system(command)


    def __copy_plot_file(self):

        local_path = os.path.dirname(os.path.realpath(__file__))
        if not os.path.exists(local_path + self.__openfoam_tmp_path):
            os.makedirs(local_path + self.__openfoam_tmp_path)

        command = "cp " + local_path + self.__ori_openfoam_tmp_path + "/plotResiduals.gplt " +\
            local_path + self.__openfoam_tmp_path

        os.system(command)

if __name__ == "__main__":
    black_box = BlackBoxInParallel(sys.argv)
    black_box.launch()
    result = black_box.get_result()
    print result
