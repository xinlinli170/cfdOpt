
class Pressure(object):
    """The class to calculate the pressure boundary conditions
    """
    def __init__(self, config, inlet_velocity_profile):
        self.p = []
        
        for r in inlet_velocity_profile.radius:
            p_tmp = 0.0

            self.p.append(p_tmp)
