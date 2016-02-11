import csv

class CFX1DVelocityProfile(object):
    """The class for setting up the 1D velocity profile boundary condition of CFX

    This class store the 1D velocity profiles created by other classes and set up for CFX.
    """  

    def __init__(self, config, inlet_velocity_profile, k_epsilon, p):
        """Inits CFX1DVelocityProfile class

        Args:
            config: RawConfigParser object
            inlet_velocity_profile: velocity profile object
            p: pressure object
            k_epsilon: turbulence model object.
        """

        self.data_map = {
            "radius":inlet_velocity_profile.radius,
            "Va":inlet_velocity_profile.Va,
            "Vt":inlet_velocity_profile.Vt,
            "Vr":inlet_velocity_profile.Vr,
            "Pressure":p.p,
            "KineticEnergy":k_epsilon.k,
            "Dissipation":k_epsilon.epsilon
            }

        self.__config = config    

    def set_profile(self):
        #Read the profile csv file path from config object
        self.cfx_case_path = self.__config.get("CFX", "case_path")
        self.profile_file_path = self.__config.get("CFX", "profile_csv_path")

        #csv table header
        self.table_header = {
            "radius":" R [ m ]",
            "Va":" Velocity Axial [ m s^-1 ]",
            "Vt":" Velocity Circumferential [ m s^-1 ]",
            "Vr":" Velocity Radial [ m s^-1 ]",
            "Pressure":" Pressure [ Pa ]",
            "KineticEnergy":" Turbulence Kinetic Energy [ m^2 s^-2 ]",
            "Dissipation":" Turbulence Eddy Dissipation [ m^2 s^-3 ]"
            }
        
        with open(self.cfx_case_path + self.profile_file_path, 'w+') as self.profile_file:    #csv file object
            self.field_names = [
                self.table_header['radius'],
                self.table_header['Va'],
                self.table_header['Vr'],
                self.table_header['Vt'],
                self.table_header['Pressure'],
                self.table_header['KineticEnergy'],
                self.table_header['Dissipation']
                ]

            self.csv_writer = csv.writer(self.profile_file)    #csv writer object

            #Start writing header for CFX profile
            self.csv_writer.writerow(["[Name]"])
            self.csv_writer.writerow(["OneDimVelocityProfile"])
            self.csv_writer.writerow(["[Spatial Fields]"])
            self.csv_writer.writerow(["R"])
            #End writing header for CFX profile
            self.csv_writer.writerow(["[Data]"])    #write the first row
            self.csv_writer.writerow(self.field_names)    #write the table header

            self.index = 0

            for r in self.data_map['radius']:    #write the table content
                self.csv_writer.writerow([
                     self.data_map['radius'][self.index],
                     self.data_map['Va'][self.index],
                     self.data_map['Vr'][self.index],
                     self.data_map['Vt'][self.index],
                     self.data_map['Pressure'][self.index],
                     self.data_map['KineticEnergy'][self.index],
                     self.data_map['Dissipation'][self.index]
                     ])
            
                self.index += 1



        

