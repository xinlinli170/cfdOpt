import ConfigParser
import os

optimization_counter = ConfigParser.RawConfigParser()

local_path = os.path.dirname(os.path.realpath(__file__))
optimization_counter.read(local_path + "/cfdOpt_counter.ini")

optimization_counter.set("Counter", "current_best_objective_function",1000)
optimization_counter.set("Counter", "num_of_simulations",0)
optimization_counter.set("Counter", "num_of_successful_simulations",0)

with open(local_path + "/cfdOpt_counter.ini", "w+") as counter_file:
    optimization_counter.write(counter_file)


