import os
import json


def get(filename=".settings.json", basepath=None):
    """get and parse .settings.json(or setted filename) from current(or basepath) and parrent directories"""
    if basepath == None:
        path = os.getcwd()
    else:
        path = os.path.abspath(basepath)
    while True:
        filepath = os.path.join(path, filename)
        if os.path.exists(filepath):
            f = open(filepath, 'r')
            d = json.load(f)
            f.close()
            return d
        before_path = path
        path = os.path.abspath(os.path.join(path, os.pardir))
        if not os.path.exists(path) or path == before_path:
            if basepath == None:
                raise Exception("not found {0}".format(filename))
            else:
                raise Exception("not found {0} in {1}".format(filename, basepath))
