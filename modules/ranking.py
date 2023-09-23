import os
import decorators as dct
import numpy as np, pandas as pd
import utils



def get_results(path):
    init_path = os.getcwd()

    def explore_tree(df_list):
        list_dir = [fpath for fpath in os.listdir() if os.path.isdir(fpath) ]
        list_file = [fpath for fpath in os.listdir() if (os.path.isfile(fpath) and fpath.endswith('stats.csv') )]
        

        for dir in list_dir:
            os.chdir(dir)
            df_list = explore_tree(df_list)
            os.chdir('..')

        for file in list_file:
            df = pd.read_csv(file)
            params_path = os.getcwd() + f'/{file.split("_")[0]}_stats.txt'
            df['params_path'] = params_path
            df_list.append(df)
        
        return df_list
    
    os.chdir(path)
    df_list = explore_tree([])
    results_df = pd.concat(df_list)
    os.chdir(init_path)

    results_df.to_csv('all_results.csv')
    return results_df

def rank( results_df, expr, conds, max_results = None):
    pass