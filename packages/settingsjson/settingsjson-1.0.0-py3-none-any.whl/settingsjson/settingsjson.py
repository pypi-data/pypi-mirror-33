import os
import json

# search settings.json
def get(filename=".settings.json", basepath=None):
    if basepath == None :
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
        path = os.path.abspath(os.path.join(path,os.pardir))
        if not os.path.exists(path) or path == before_path :
            raise Exception("not found .setting.json")
