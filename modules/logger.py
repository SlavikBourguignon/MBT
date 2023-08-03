import utils
import os
import json


def _getFoldersName(paramsData, paramsBT, paramsRun): 
        pdd = paramsData['download_params']
        resultsFolder = 'results'
        stratFolder = paramsRun['strategy_name']
        symbolFolder = pdd['symbols']
        itvFolder = pdd['interval']
        namedir =  f'{pdd["start"].date()}_' \
                    f'{pdd["end"].date()}_' \
                    f'{str(paramsBT["length"].days).split(" ")[0]}_' \
                    f'{str(paramsBT["forward"].days).split(" ")[0]}'
        
        return resultsFolder, stratFolder, symbolFolder, itvFolder, namedir
        

def verifyTried(paramsTxt, paramsData, paramsBT, paramsRun):
        try : 
            resultsFolder, stratFolder, symbolFolder, itvFolder, namedir = \
                _getFoldersName(paramsData, paramsBT, paramsRun)

            os.chdir(
                f'{resultsFolder}/{stratFolder}/{symbolFolder}'
                f'/{itvFolder}/{namedir}')
            
            return_back = '../../../../..'
        
        except Exception as e:
            utils.debug('Exception: ', e)
            return False, ''

        params_files = [file for file in os.listdir() \
            if (os.path.isfile(file) and file.endswith('_params.txt'))]
        
        for file in params_files:
            with open(file) as f:
                d = json.load(f)
            if d == paramsTxt:
                path = os.getcwd()
                os.chdir(return_back)
                return True, path +'/' + file
            
        os.chdir(return_back)
        return False, ''


def log(paramsTxt, paramsData, paramsRun, paramsBT, paramsPF, pf):
    
    resultsFolder, stratFolder, symbolFolder, itvFolder, namedir = \
        _getFoldersName(paramsData, paramsBT, paramsRun)

    utils.go_or_create(resultsFolder)
    utils.go_or_create(stratFolder)
    utils.go_or_create(symbolFolder)
    utils.go_or_create(itvFolder)
    utils.go_or_create(namedir)

    numfiles = [int(f.split('.')[0].split('_')[0]) for f in os.listdir() \
        if os.path.isfile(f)]
    
    if len(numfiles) == 0:
        id = 1

    else: 
        id = max(numfiles) + 1

    pf.stats().to_csv(f'{id}_stats.csv')
    utils.dict_to_txt(paramsTxt, f'{id}_params')

    os.chdir('../../../../..')