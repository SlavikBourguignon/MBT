import os 
import json
import ast
import collections

def debug(*args, **kwargs):
    print('debug'+95*'=')
    print(*args, **kwargs)
    print(100*'=')
    
def go_or_create(dir):
    if os.path.isdir(dir):
        os.chdir(dir)
    else: 
        os.mkdir(dir)
        os.chdir(dir)

def dict_to_txt(dict, name):
    with open('{}.txt'.format(name), 'w') as file:
        file.write(json.dumps(dict, indent=4))

def flatten(x):
    if isinstance(x, collections.Sequence) and not isinstance(x, (str, bytes)):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

def get_all_params_files(folder):
    os.chdir(folder)
    files = [elem for elem in os.listdir() if os.path.isfile(elem)]
    paramsList = []
    for file in files: 
        with open(file) as f:
            d = ast.literal_eval(f.read())
            paramsList.append(d)
    os.chdir('..')
    return paramsList

def split_meta_params(params):
    if isinstance(params['backtest']['lenghth'], collections.Sequence) \
    and isinstance(params['backtest']['forward'], collections.Sequence) :
        try : 
            params_product = params['backtest']['params_product']
        except:
            params_product = False
    
def regroupParams(paramsData, paramsRun, paramsBT, paramsPF):
    paramsTxt = {}
    paramsTxt['paramsData'] = paramsData
    paramsTxt['paramsRun'] = paramsRun
    paramsTxt['paramsBT'] = paramsBT
    paramsTxt['paramsPF'] = paramsPF
    return paramsTxt
