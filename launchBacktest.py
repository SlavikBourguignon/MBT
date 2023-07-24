import argparse
from modules import utils 

parser = argparse.ArgumentParser(description = 'This program backtests trading strategies using the vectorbt library.')
parser.add_argument('folderList', nargs = '*', default = ['params'])

args = parser.parse_args()
print(args.folderList)

paramsList = []
for folder in args.folderList:
    paramsList.append(utils.get_all_params_files(folder))

paramsList = utils.flatten(paramsList)

print(paramsList)



