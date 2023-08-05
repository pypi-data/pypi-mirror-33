from importlib import import_module


def my_import(name):
    splitted = name.rsplit('.', 1)

    mod = import_module(splitted[0])

    if len(splitted) > 1:
        mod = getattr(mod, splitted[1])
    return mod
