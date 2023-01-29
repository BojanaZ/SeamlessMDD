from collections.abc import Iterable
import importlib
import pkgutil
from pathlib import Path
import os


def iterable(obj):
    return isinstance(obj, Iterable)


def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :param recursive: look for submodules recursively
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


def get_class_from_parent_module(class_name, package, recursive=True):
    modules = import_submodules(package, recursive)
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


def get_file_path_for_format(type_name, formats, use_root=True):

    root = ""
    if use_root:
        root = get_project_root()

    paths = {}
    for _format in formats:
        if _format not in paths:
            paths[_format] = os.path.join(root, "files", type_name + "." + _format)

    return paths


def class_name_to_underscore_format(type_):
    class_name = type_.__name__
    underscore_format_name = class_name[0].lower()
    for character in class_name[1:]:
        if character.isupper():
            underscore_format_name += "_"
            character = character.lower()

        underscore_format_name += character

    return underscore_format_name
