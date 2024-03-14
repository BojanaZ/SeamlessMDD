import os
import shutil

from utilities.utilities import import_project_from_absolute_path
from tracing.tracer import Tracer
from transformation.data_manipulation import DataManipulation
from transformation.generator_handler import GeneratorHandler


class WorkspaceProject(object):
    
    def __init__(self, project_path, project_name, config_filename=None, main_module_name=None):
        if config_filename is None:
            self._config_filename = ".project"
        
        if main_module_name is None:
            self._main_module_name = "bootstrap"
            
        self._project_path = project_path
        self._project_name = project_name

        self._metamodel = None
        self._data_manipulation = None
        self._tracer = None
        self._generator_handler = None

        self._init()
    
    @property
    def project_path(self):
        return self._project_path
    
    @project_path.setter
    def project_path(self, value):
        self._project_path = value
        
    @property
    def project_name(self):
        return self._project_name
    
    @project_name.setter
    def project_name(self, value):
        self._project_name = value
        
    @property
    def config_filename(self):
        return self._config_filename

    @config_filename.setter
    def config_filename(self, value):
        self._config_filename = value

    @property
    def main_module_name(self):
        return self._main_module_name

    @main_module_name.setter
    def main_module_name(self, value):
        self._main_module_name = value

    @property
    def metamodel(self):
        return self._metamodel

    @metamodel.setter
    def metamodel(self, value):
        self._metamodel = value

    @property
    def data_manipulation(self):
        return self._data_manipulation

    @data_manipulation.setter
    def data_manipulation(self, value):
        self._data_manipulation = value

    @property
    def generator_handler(self):
        return self._generator_handler

    @generator_handler.setter
    def generator_handler(self, value):
        self._generator_handler = value

    @property
    def tracer(self):
        return self._tracer

    @tracer.setter
    def tracer(self, value):
        self._tracer = value

    def _init(self):
        modules, main_module = self.load_project()
        self.remove_temp_files()

        self._metamodel = main_module.make(modules)
        self._data_manipulation = DataManipulation(self._project_path)
        self._generator_handler = GeneratorHandler(self._project_path)
        self._tracer = Tracer(self._project_path)

        try:
            self._data_manipulation.load_from_xmi(metamodel=self._metamodel)
            self._generator_handler.load_from_json()
            self._tracer.load_from_json()
        except FileNotFoundError as e:
            print("Project %s from %s could not be loaded.".format(self._project_name, self._project_path))

    def load_project(self):
        # project_config_path = os.path.join(project_path, config_filename)
        # try:
        #     config_file = open(project_config_path)
        # except:
        #     raise ProjectNotFoundException("Current folder is not a SeamlessMDD project.")
        modules = import_project_from_absolute_path(self._project_path, self._project_name)

        main_module = modules[self._project_name + "." + self._main_module_name]
        return modules, main_module

    def remove_temp_files(self):
        folder = 'templates/temp_diff'
        if self._project_path is None:
            project_root_path = os.getcwd()
        else:
            project_root_path = self._project_path
        folder_path = os.path.join(project_root_path, folder)

        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
