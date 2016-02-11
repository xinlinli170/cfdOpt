class SwirlNumberEvaluation(object):
    """The class for evaluating the swirl number of the inlet velocity profile
    """

    def __init__(self, inlet_velocity_profile):
        self.inlet_velocity_profile = inlet_velocity_profile

    def get_swirl_number(self):
    
        maxradius = self.inlet_velocity_profile.radius[-1]
    
        swirl = 0.0
        tanMomentum = 0.0
        axialMomentum = 0.0

        radius = self.inlet_velocity_profile.radius
        Va = self.inlet_velocity_profile.Va
        Vt = self.inlet_velocity_profile.Vt

        for index in range(len(radius) - 1):
            dr = radius[index + 1] - radius[index]
            radius_dr = (radius[index] + radius[index + 1]) / 2.0
            Va_dr = (Va[index] + Va[index + 1]) / 2.0
            Vt_dr = (Vt[index] + Vt[index + 1]) / 2.0
            #swirl += ( (Va_dr * Vt_dr * radius_dr * radius_dr) / (maxradius * (Va_dr * Va_dr * radius_dr)))
            tanMomentum += Va_dr * Vt_dr * radius_dr * radius_dr * dr
            axialMomentum += Va_dr * Va_dr * radius_dr * dr
    
        swirl = tanMomentum / (axialMomentum * maxradius)

        return swirl
