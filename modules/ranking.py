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
            df = pd.read_csv(file,)
            params_path = os.getcwd() + f'/{file.split("_")[0]}_params.txt'
            df = df.T
            keys = df.iloc[0]
            values = df.iloc[1]
            df = pd.DataFrame({key: [value] for key, value in zip(keys, values) }, index = [params_path])            

            df_list.append(df)
        
        return df_list
    
    os.chdir(path)
    df_list = explore_tree([])
    results_df = pd.concat(df_list)
    os.chdir(init_path)

    results_df.to_csv('all_results.csv')
    return results_df

def parse_expr(s, expr):
    i = 0
    nbquotes = 0 
    prev_add = f'{s}["'
    post_add = '"].astype(float)'
    while True:
        if i >= len(expr):
            break
        if expr[i] == "!":
            if nbquotes%2 == 0:
                expr = expr[:i] + prev_add + expr[i+1:]
                i += len(prev_add)
            if nbquotes%2 == 1:
                expr = expr[:i] + post_add + expr[i+1:]
                i+= len(post_add)
            nbquotes+=1
        i+=1

    return expr

def rank( results_df, sort_expr, conds, max_results = None):
    for cond_expr in conds:
        cond = parse_expr('results_df', cond_expr)
        results_df['cond'] = eval(cond)
        results_df = results_df[np.array(results_df['cond'])]

    if not sort_expr:
        sort_expr = '!End Value!'

    sort_fun = parse_expr('results_df', sort_expr)
    results_df['sort'] = eval(sort_fun)
    results_df = results_df.sort_values(by = 'sort', ascending = False)
    
    results_df.to_csv('conditionned.csv')