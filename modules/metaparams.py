import json
import decorators as dct
import copy
import utils

@dct.product_args
def modify_1_key(params: dict, keyPath: tuple, value: any ) -> dict:
    cp = copy.deepcopy(params)
    if len(keyPath) > 1 :
        
        s = cp[keyPath[0]]
        for key in keyPath[1:-1] :
            s = s[key]
        s[keyPath[-1]] = value
        return cp
    
    else:
        cp[keyPath[0]] = value
        return cp

@dct.map_args    
def modify_2_keys(params: dict, keyPath1: tuple, value1: any, keyPath2: tuple, value2: any)-> dict:
    tmp = modify_1_key(params, keyPath1, value1)
    return modify_1_key(tmp, keyPath2, value2)

def split(params):
    bt = params['backtest']
    lgth, fwd = bt['length'], bt['forward']
    pp = 'params_product'
    params_product = bt[pp] if pp in bt.keys() else False

    if params_product:
        params_list = modify_1_key(params, ('backtest', 'length'), lgth )
        return modify_1_key(params_list, ('backtest', 'forward'), fwd)
        
    else :
        return modify_2_keys(params, ('backtest', 'length'), lgth, ('backtest', 'forward'), fwd)
    
                    