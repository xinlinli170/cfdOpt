
class KEpsilon(object):
    """The class to calculate the Turbulence Kinetic Energy and Turbulence Eddy Dissipation boundary conditions
    """
    def __init__(self, config, inlet_velocity_profile):
        #read k-epsilon model parameters from config object
        self.turbulence_intensity = config.getfloat("InletPatch", "turbulence_intensity")
        self.turbulence_length_scale = config.getfloat("InletPatch", "turbulence_length_scale")

        self.k = []
        self.epsilon = []

        
        for Va in inlet_velocity_profile.Va:
            k_tmp = 1.5 * ( (float(Va) * self.turbulence_intensity) ** 2)
            epsilon_tmp = pow(k_tmp, 1.5) / self.turbulence_length_scale

            self.k.append(k_tmp)
            self.epsilon.append(epsilon_tmp)
