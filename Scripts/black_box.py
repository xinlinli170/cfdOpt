from black_box_in_serial import BlackBoxInSerial
from black_box_in_parallel import BlackBoxInParallel
import black_box_block_evaluation
import sys
import os
import ConfigParser

class BlackBox(object):
    """
    """

    def __init__(self, argv):
        self.__argv = argv

        #config
        local_path = os.path.dirname(os.path.realpath(__file__))
        self.__config_file_name = "cfdOpt_config.ini"
        self.__config = ConfigParser.RawConfigParser() #Inits blackbox config
        self.__config.read(local_path + "/" + self.__config_file_name)  #Load config template

    def launch_black_box(self):
        if self.__is_in_parallel():
            black_box = black_box_in_parallel.BlackBoxInParallel(self.__argv, self.__config)
        elif self.__is_block_evaluation():
            black_box = black_box_block_evaluation.BlackBoxBlockEvaluation(self.__argv, self.__config)
        else:
            black_box = black_box_in_serial.BlackBoxInSerial(self__argv, self.__config)

        black_box.launch()
        black_box_result = black_box.get_result()

        return black_box_result

    def __is_block_evaluation(self):
        return True if self.__config.getint("NOMAD", "bb_max_block_size") != 1 else False

    def __is_in_parallel(self):
        return True if self.__config.getint("NOMAD", "num_of_threads") != 1 else False

    def __is_nomad_input_file(self, argv):
        return True if len(argv) == 2 and "nomad" in argv[1] else False

    def __read_nomad_input_file(self, argv):
        with open(argv[1], 'r') as nomad_input:
            nomad_input_data = nomad_input.read().splitlines()[0].split(" ")
        return nomad_input_data

black_box = BlackBox(sys.argv)
result = black_box.launch_black_box()
print result
