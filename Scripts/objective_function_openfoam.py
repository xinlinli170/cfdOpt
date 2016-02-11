import read_swak4foam_result

class ObjectiveFunction(object):
    """The class to evaluate different objective functions.

    """

    def __init__(self, config):
       self.__config = config
       self.case_path = self.__config.get("OpenFOAM", "case_path")

    def get_objective_function(self):
        #type_of_objective_function = self.__config.get("Optimization", "objective_function")
        #if type_of_objective_function == "EnergyLossFactor".lower():
        return self.__get_energy_loss_factor()
        #else:
        #    print "incorrect objective function!"
        #    exit(1)

    def __get_energy_loss_factor(self):
       
        self.data_path = self.case_path + self.__config.get("Swak4Foam", "energy_loss_factor")

        energy_loss_factor = read_swak4foam_result.Swak4FoamResult(self.data_path)

        return float(energy_loss_factor.data['sum'])
