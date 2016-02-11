import inlet_velocity_profile
from math import exp, tan

class AnalyticalModel(object):
    """The class to calculate the inlet velocity profile with the analytical model"""

    def __init__(self, config):
        #read the analytical model parameters from config object
        self.__config = config    #local copy of config object

        self.radial_velocity_evaluation = self.__config.getboolean("AnalyticalModel",
            "radial_velocity_profile_evaluation_flag")
        self.radius_min = self.__config.getfloat("InletPatch", "radius_of_hub")
        self.radius_max = self.__config.getfloat("InletPatch", "radius_of_cone")

        ratio_max = 1.0
        ratio_min = self.radius_min / (self.radius_max - self.radius_min)

        self.ratio_boundary_layer = \
            ratio_max - self.__config.getfloat("InletPatch", "boundary_layer_thickness_percentage")

        self.num_interpolation_points = self.__config.getfloat("InletPatch", "num_of_interpolation_points")

        #self.delta_radius = (self.radius_max - self.radius_min) / (self.num_interpolation_points - 1)

        #inits the inlet_velocity_profile object
	self.inlet_velocity_profile = inlet_velocity_profile.InletVelocityProfile()

        delta_ratio = (ratio_max - ratio_min) / (self.num_interpolation_points - 1)

        ratio = [x for x in self.drange(ratio_min, ratio_max, delta_ratio)]
        ratio[-1] = ratio_max

        #Calculate the velocity profile far from the wall
        far_from_wall = (r for r in ratio if r <= self.ratio_boundary_layer)
        for r in far_from_wall:
            #Calculate the radius w.r.t ratio
            #radius_tmp = self.radius_min + (self.radius_max - self.radius_min) * r
            radius_tmp = self.__get_radius_from_ratio(r)
            self.inlet_velocity_profile.radius.append(radius_tmp)
            #Calculate the axial, tangential, radial velocities w.r.t ratio 
	    self.inlet_velocity_profile.Va.append(self.__calcul_axial_velocity(radius_tmp))
            self.inlet_velocity_profile.Vt.append(self.__calcul_tangential_velocity(radius_tmp))
            self.inlet_velocity_profile.Vr.append(\
	        self.__calcul_radial_velocity(self.inlet_velocity_profile.Va[-1]))

        #Calculate the velocity profile between boundary layer and internal flow
        radius_boundary_layer = self.__get_radius_from_ratio(self.ratio_boundary_layer)
	Va_boundary_layer = self.__calcul_axial_velocity(radius_boundary_layer)
	Vt_boundary_layer = self.__calcul_tangential_velocity(radius_boundary_layer)
        Vr_boundary_layer = self.__calcul_radial_velocity(Va_boundary_layer)

        #Calculate the velocity profile near the wall
	near_wall = (r for r in ratio if r > self.ratio_boundary_layer)
	for r in near_wall:
	    #calculate the radius w.r.t ratio
	    radius_tmp = self.__get_radius_from_ratio(r)
	    self.inlet_velocity_profile.radius.append(radius_tmp)
	    #Calculate the axial, tangential, radial velocities w.r.t ratio
            self.inlet_velocity_profile.Va.append(self.__calcul_wall_function(Va_boundary_layer, radius_tmp))
            self.inlet_velocity_profile.Vt.append(self.__calcul_wall_function(Vt_boundary_layer, radius_tmp))
            self.inlet_velocity_profile.Vr.append(self.__calcul_wall_function(Vr_boundary_layer, radius_tmp))


    def __get_radius_from_ratio(self, ratio):
        return self.radius_min + (self.radius_max - self.radius_min) * ratio

    def __get_ratio_from_radius(self, radius):
        return (radius - self.radius_min)/(self.radius_max - self.radius_min)


    def __calcul_axial_velocity(self, radius):
        u0 = self.__config.getfloat("AnalyticalModel", "U0")
        u1 = self.__config.getfloat("AnalyticalModel", "U1")
        u2 = self.__config.getfloat("AnalyticalModel", "U2")

        r1 = self.__config.getfloat("AnalyticalModel", "R1")
        r2 = self.__config.getfloat("AnalyticalModel", "R2")

        Va = u0 \
            + u1 * exp(-1.0 * (radius**2.0)/(r1**2.0)) \
            + u2 * exp(-1.0 * (radius**2.0)/(r2**2.0))

        return Va

    def __calcul_tangential_velocity(self, radius):
        omega0 = self.__config.getfloat("AnalyticalModel", "Omega0")
	omega1 = self.__config.getfloat("AnalyticalModel", "Omega1")
	omega2 = self.__config.getfloat("AnalyticalModel", "Omega2")

	r1 = self.__config.getfloat("AnalyticalModel", "R1")
	r2 = self.__config.getfloat("AnalyticalModel", "R2")

        if radius == 0:
            radius = 0.0000001

	Vt = omega0 * radius  \
	+ omega1 * (r1**2.0) / radius  * (1.0 - exp(-1.0 * (radius ** 2.0)/(r1 ** 2.0))) \
	+ omega2 * (r2**2.0) / radius  * (1.0 - exp(-1.0 * (radius ** 2.0)/(r2 ** 2.0)))

	return Vt

    def __calcul_radial_velocity(self, Va):
        if self.radial_velocity_evaluation:
	    theta = self.__config.getfloat("AnalyticalModel", "Theta")
	    Vr = Va * tan(2 * 3.1415926 * theta / 360)
	else:
	    Vr = 0.0
	    
	return Vr

    def __calcul_wall_function(self, velocity_boundary_layer, radius):
        ratio = self.__get_ratio_from_radius(radius)
        
        exp_ratio = 1.0/7.0

	velocity_near_wall = \
            velocity_boundary_layer * (( (1.0 - ratio) / (1.0 - self.ratio_boundary_layer) ) ** (exp_ratio))

        return velocity_near_wall

    def drange(self, start, stop, step):
        r = start
        while r < stop:
            yield r
            r += step
