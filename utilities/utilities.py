import importlib
import pkgutil
import os

from pathlib import Path
from collections.abc import Iterable
from importlib.util import spec_from_file_location, module_from_spec


def iterable(obj):
    return isinstance(obj, Iterable)


def import_submodules(package, prefix, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :param recursive: look for submodules recursively
    """
    if isinstance(package, str):
        package = importlib.import_module(package)

    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, prefix=prefix):

        full_name = name

        if not full_name.startswith(prefix):
            full_name = prefix + "." + full_name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name, full_name + ".", True))
    return results


def import_project_from_absolute_path(project_root_path, project_module_name):
    return import_submodules_from_absolute_path(project_root_path, project_module_name)


def import_submodules_from_absolute_path(root_path, root_module_name):

    os.chdir(root_path)
    submodules = import_submodules(root_module_name, root_module_name+".")
    return submodules


def get_class_from_parent_module(class_name, package, recursive=True):
    modules = import_submodules(package, "", recursive)
    for module in modules.values():
        try:
            type = getattr(module, class_name)
            return type
        except AttributeError:
            continue

    raise ImportError("Class %s is not part of %s module." % (class_name, package))


def get_project_root():
    """Returns project root folder."""
    return Path(__file__).parent.parent


def get_file_path_for_format(type_name, formats, project_root):

    if project_root is None:
        root = get_project_root()
    else:
        root = project_root

    paths = {}
    for _format in formats:
        if _format not in paths:
            paths[_format] = os.path.join(root, "files", type_name + "." + _format)

    return paths


def class_name_to_underscore_format(class_name):
    underscore_format_name = class_name[0].lower()
    for character in class_name[1:]:
        if character.isupper():
            underscore_format_name += "_"
            character = character.lower()

        underscore_format_name += character

    return underscore_format_name


def class_object_to_underscore_format(type_):
    class_name = type_.__name__
    return class_name_to_underscore_format(class_name)
