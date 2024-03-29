import os
import inspect


def import_project_from_absolute_path(project_root_path, project_module_name):
    return import_submodules_from_absolute_path(project_root_path, project_module_name)


def get_generators(project_path, project_name):
    modules = import_submodules_from_absolute_path(project_path, project_name+".transformation.generators")

    generator_classes = {}
    for module in modules.values():
        for value in module.__dict__.values():
            if inspect.isclass(value)\
                    and issubclass(value, BaseDiffGenerator)\
                    and not inspect.isabstract(value):
                generator_classes[value.__name__] = value
    return generator_classes


def get_tasks(project_path, project_name):
    modules = import_submodules_from_absolute_path(project_path, project_name+".transformation.tasks")

    task_classes = {}
    for module in modules.values():
        for value in module.__dict__.values():
            if inspect.isclass(value)\
                    and issubclass(value, TemplateFileTask)\
                    and not inspect.isabstract(value):
                task_classes[value.__name__] = value
    return task_classes
