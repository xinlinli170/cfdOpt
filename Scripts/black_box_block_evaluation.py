from black_box_in_parallel import BlackBoxInParallel
import threading
import subprocess
import os
import io
import ConfigParser
import time

class BlackBoxBlockEvaluation(object):
    """
    """

    def __init__(self, argv, config):
        self.__config = config
        self.__argv = argv        

        #create a lock to prevent the cwd conflicts between different threads
        self.__cwd_lock = threading.Lock()        

    def __unpack_argv(self):
        #load input arguments
        if self.__is_nomad_input_file(self.__argv):
            block_evaluation_input_data = self.__read_nomad_input_file(self.__argv)  #local copy of arguments
        else:
            print "wrong input arguments!"
            exit(1)

        return block_evaluation_input_data

    def launch(self):
        block_evaluation_input_data = self.__unpack_argv() 

        threads_popen = [None] * self.__bb_block_size
        results = [None] * self.__bb_block_size
        with open ('tmp_cfg', 'w') as config_string:
            self.__config.write(config_string)

        for index in range(0, self.__bb_block_size):
            #init seperate arguments
            argv_for_one = block_evaluation_input_data[index].split(" ")
            argv_for_one.insert(0, 'block_evaluation')

            #make a deep copy of config parser
            config_for_one = ConfigParser.RawConfigParser()
            config_for_one.read('tmp_cfg')

            threads_popen[index] = threading.Thread(target=self.launch_one_black_box, args=(argv_for_one, config_for_one, index, results))
            threads_popen[index].start()
            #time.sleep(10)

        self.__result = ""

        for index in range(0, self.__bb_block_size):
            threads_popen[index].join() 

        for index in range(0, self.__bb_block_size):
            if results[index] is not None:
                self.__result += (str(results[index]) + "\n")
            else:
                self.__result += "FAIL\n"

    def launch_one_black_box(self, argv_for_one, config_for_one, index, results):
        #print "thread" + str(index) + " Begin"
        #if self.__cwd_lock.acquire():
        #    print "lock"
        #    time.sleep(10)
        #    self.__cwd_lock.release()
        black_box = BlackBoxInParallel(argv_for_one, config_for_one, index, self.__cwd_lock)
        black_box.launch()
        
        results[index] = black_box.get_result()

        #print "thread" + str(index) + " End, result = " + str(results[index])

    def get_result(self):
        return self.__result 


    def __is_nomad_input_file(self, argv):
        return True if len(argv) == 2 and "nomad" in argv[1] else False

    def __read_nomad_input_file(self, argv):
        with open(argv[1], 'r') as nomad_input:
            nomad_input_data = nomad_input.read().splitlines()

        self.__bb_block_size = len(nomad_input_data)

        return nomad_input_data



    

