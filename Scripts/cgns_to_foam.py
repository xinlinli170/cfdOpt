import sys
import os

class CGNSToFoam(object):
    """
    """

    def __init__(self, cgns_file_path):
        self.__cgns_file_path = cgns_file_path

        local_path = os.path.dirname(os.path.realpath(__file__))
        self.cgns_to_foam_tmp_dir_path = local_path + "/cgns_to_foam"

        self.template_path = local_path + self.__config.get("OpenFOAM", "case_template")

        if not os.path.exists(self.cgns_to_foam_tmp_dir_path)
            os.makedirs(self.cgns_to_foam_tmp_dir_path)

    def cgns_to_fluent_mesh(self):

        current_cwd = os.getcwd()
        os.chdir(self.cgns_to_foam_tmp_dir_path)

        self.__cgns_to_foam_mesh(self.__cgns_file_path)

        os.chdir(current_cwd)

    def __cgns_to_foam_mesh(self, cgns_file_path):
        #set up openfoam case for cgnsToFoam
        tmp_path = self.cgns_to_foam_tmp_dir_path + "/tmp"
        os.makedirs(tmp_path)
        os.chdir(tmp_path)

        command = "cp -r " + self.template_path + "/* " + tmp_path
        os.system(command)

         

        command = "cgnsToFoam " + cgns_file_path 

    def __foam_mesh_to_fluent_mesh(self, foam_mesh_dir):
        command = "foamMeshToFluent -case " + foam_mesh_dir
