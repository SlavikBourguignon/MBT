import sys 
sys.path.append('modules/')
import warnings

import argparse
from modules import utils 
import bt_runner

parser = argparse.ArgumentParser(description = 'This program backtests trading strategies using the vectorbt library.')

parser.add_argument('-folderList', nargs = '*', default = ['params'])
parser.add_argument('-sendTelegramUpdates', nargs= 1, type= bool, default = True)



args = parser.parse_args()
print(args.folderList)

paramsList = []
for folder in args.folderList:
    paramsList.append(utils.get_all_params_files(folder))

paramsList = utils.flatten(paramsList)

for params in paramsList:
    bt_runner.run(params)


