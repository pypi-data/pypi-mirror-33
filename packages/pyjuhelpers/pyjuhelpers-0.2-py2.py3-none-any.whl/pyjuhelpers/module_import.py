import importlib


def import_from_string(name):
    module_name, class_name = name.rsplit(".", 1)

    somemodule = importlib.import_module(module_name)
    return getattr(somemodule, class_name)