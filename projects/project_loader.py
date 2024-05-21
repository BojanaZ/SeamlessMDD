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
            
        self._path = project_path
        self._name = project_name
        self._templates_path = None

        self._metamodel = None
        self._data_manipulation = None
        self._tracer = None
        self._generator_handler = None

        self.init()
    
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, value):
        self._path = value

    @property
    def templates_path(self):
        return self._templates_path

    @templates_path.setter
    def templates_path(self, value):
        self._templates_path = value

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
        
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

    def create_initial_content(self):
        self._data_manipulation = DataManipulation(self._path)
        self._generator_handler = GeneratorHandler(self)
        self._tracer = Tracer(self._path)

        self._data_manipulation.save_to_xmi()
        self._generator_handler.save_to_json()
        self._tracer.save_to_json()

    def init(self):
        modules, main_module = self.load_project()
        self.remove_temp_files()

        if main_module is not None:
            self._metamodel = main_module.make(modules)
            self._data_manipulation = DataManipulation(self._path, self._metamodel)
            self._generator_handler = GeneratorHandler(self)
            self._tracer = Tracer(self._path)

            try:
                self._data_manipulation.load_from_xmi()
                self._generator_handler.load_from_json()
                self._tracer.load_from_json()
            except FileNotFoundError as e:
                print("Project {} from {} could not be loaded.".format(self._name, self._path))

    def load_project(self):
        # project_config_path = os.path.join(path, config_filename)
        # try:
        #     config_file = open(project_config_path)
        # except:
        #     raise ProjectNotFoundException("Current folder is not a SeamlessMDD project.")
        modules = import_project_from_absolute_path(self._path, self._name)

        main_module_name = self._name + "." + self._main_module_name
        main_module = None
        if main_module_name in modules:
            main_module = modules[self._name + "." + self._main_module_name]

        return modules, main_module

    def remove_temp_files(self):
        folder = 'templates/temp_diff'
        if self._path is None:
            project_root_path = os.getcwd()
        else:
            project_root_path = self._path
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
