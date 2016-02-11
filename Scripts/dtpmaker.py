import os
import json
import inlet_velocity_profile

class DtpMaker(object):
    """The class for manipulating dtpmaker
    """

    def __init__(self, config, cwd_lock=None):

        #self.__read_config(config)

        if cwd_lock is not None:
            self.__cwd_lock = cwd_lock
        else:
            self.__cwd_lock = None

        self.__config = config

        #create the parameter file data
        self.__create_parameter_file_data()

        #create the temperary files directory
	local_path = os.path.dirname(os.path.realpath(__file__))
        self.dtpmaker_tmp_dir_path = local_path + self.__config.get("dtpmaker", "tmp_file_directory")

        if not os.path.exists(self.dtpmaker_tmp_dir_path):
            os.makedirs(self.dtpmaker_tmp_dir_path)

        #create the parameter file path
	self.dtpmaker_parameter_file_path = self.dtpmaker_tmp_dir_path + "/dtpmaker_parameter_file.txt"
        #create the parameter file
        self.__create_paramter_file()

        if cwd_lock is not None:
            cwd_lock.acquire()

        #change working directory to tmp file path        
        current_cwd = os.getcwd()
        os.chdir(self.dtpmaker_tmp_dir_path)

        #launch dtpmaker
        self.__launch_dtpmaker()

        #Inits inlet_velocity_profile object
	self.inlet_velocity_profile = inlet_velocity_profile.InletVelocityProfile()

        #get velocity profiles
        self.__get_velocity_profile()

        #recover the working directory
        os.chdir(current_cwd)

        if cwd_lock is not None:
            cwd_lock.release()

        
    def __launch_dtpmaker(self):
        self.call_dtpmaker = self.__config.get("dtpmaker", "call")
        command_string = self.call_dtpmaker + " " + self.dtpmaker_parameter_file_path  + " &> "\
            + self.dtpmaker_tmp_dir_path + "/dtpmaker.log" #/dev/null  
        os.system(command_string)

    def __get_velocity_profile(self):
        #obtain the path of the velocity profile files
        current_working_directory = os.getcwd()
        va_path = current_working_directory + "/va_cfdOpt.dat"
        vt_path = current_working_directory + "/vt_cfdOpt.dat"
        vr_path = current_working_directory + "/vr_cfdOpt.dat"

        #read va file and radius
        with open (va_path, 'r') as va_file:
            va_data = va_file.readlines()
            for data in va_data:
                data = data.split(" ")
                for word in data:
                    if word[-1] == '\n':
                        self.inlet_velocity_profile.Va.append(float(word[:-1]))
                    else:
                        self.inlet_velocity_profile.radius.append(float(word))
         #read vt file
        with open (vt_path, 'r') as vt_file:
            vt_data = vt_file.readlines()
            for data in vt_data:
                data = data.split(" ")
                for word in data:
                    if word[-1] == '\n':
                        self.inlet_velocity_profile.Vt.append(float(word[:-1]))

         #read vr file
        with open (vr_path, 'r') as vr_file:
            vr_data = vr_file.readlines()
            for data in vr_data:
                data = data.split(" ")
                for word in data:
                    if word[-1] == '\n':
                        self.inlet_velocity_profile.Vr.append(float(word[:-1]))


    def __create_parameter_file_data(self):

        self.num_control_points = self.__config.getint("dtpmaker", "num_of_control_points")
        self.radius_min = self.__config.getfloat("InletPatch", "radius_of_hub")
        self.radius_max = self.__config.getfloat("InletPatch", "radius_of_cone")
        self.va_control_points = json.loads(str(self.__config.get("dtpmaker", "Va")))
        self.vt_control_points = json.loads(str(self.__config.get("dtpmaker", "Vt")))

	#create the ratio list
	delta_ratio = 1.0 / (self.num_control_points - 1.0)

        ratio = []

	for i in range(self.num_control_points):
	    ratio_tmp = i * delta_ratio
	    ratio.append(ratio_tmp)

        self.dtpmaker_parameter_file_data = ""
        self.dtpmaker_parameter_file_data += "#Part 1: Velocity Profiles #\n"
        self.dtpmaker_parameter_file_data += "#r     Vtan\n"

        for i in range(self.num_control_points):
            self.dtpmaker_parameter_file_data += str(ratio[i]) + "       " + str(self.vt_control_points[i]) + "\n"

        self.dtpmaker_parameter_file_data += "\n"
        self.dtpmaker_parameter_file_data += "#r     Vax\n"

        for i in range(self.num_control_points):
            self.dtpmaker_parameter_file_data += str(ratio[i]) + "      " + str(self.va_control_points[i]) + "\n"

        self.dtpmaker_parameter_file_data += "\n"
        self.dtpmaker_parameter_file_data += "#Part 2: Principal arguments\n"
        self.dtpmaker_parameter_file_data += "va_ave=3.0\n"
        self.dtpmaker_parameter_file_data += "rmin=" + str(self.radius_min) + "\n"
        self.dtpmaker_parameter_file_data += "rmax=" + str(self.radius_max) + "\n"
        self.dtpmaker_parameter_file_data += \
            "bl_in_vt=0.0\n" + \
            "bl_out_vt=5.0\n" + \
            "bl_in_va=0.0\n" + \
	    "bl_out_va=5.0\n" + \
	    "bl_in_vr=0.0\n" + \
	    "bl_out_vr=5.0\n" + \
	    "points=100\n" + \
	    "blpointsin=25\n" + \
	    "blpointsout=25\n" + \
	    "alphahub=-5\n" + \
	    "alphashroud=12\n" + \
	    "vrint=False\n" + \
	    "plot=False\n" + \
	    "print=True\n" + \
	    "output_suffix='cfdOpt'\n" + \
            "\n" + \
            "#Part 3: Secondary arguments\n" + \
	    "r_ns=0.5\n" + \
	    "gamma=0.0\n" + \
	    "rad0=0.0\n" + \
	    "rpm=500\n" + \
	    "vanomfrac=-0.2\n" + \
	    "tanh_midfactor_va=0.5\n" + \
	    "bcoeff_va=94.248\n" + \
	    "tanh_midfactor_vr=0.3\n" + \
	    "bcoeff_vr=188.50\n" + \
	    "powerlaw=7\n" + \
	    "# base=testData_f1330.txt\n"

    def __create_paramter_file(self):
        #create the parameter file to launch dtpmaker
        if not os.path.exists(os.path.dirname(self.dtpmaker_parameter_file_path)):
            os.makedirs(os.path.dirname(self.dtpmaker_parameter_file_path))

        with open(self.dtpmaker_parameter_file_path, 'w+') as dtpmaker_parameter_file:
	    dtpmaker_parameter_file.write(self.dtpmaker_parameter_file_data)
	


