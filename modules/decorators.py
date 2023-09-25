#This file defines decorators for the vbt_projects folder
import functools
import traceback
import os
import copy
import itertools, time, datetime
import utils
import telegram
import dotenv
import inspect

import warnings

warnings.filterwarnings("ignore")


def retry_on_error(func):
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        count = 0
        while count < 3:
            try : 
                return func(*args, **kwargs)
            except Exception as e:
                count += 1
                print(f'On try number {count}, exception \n{e}\nwas caught. \nRetrying ... ({3-count} tries left).')
    return wrapper


def product_args(func):

    @functools.wraps(func)
    def wrapper(*args):
        res = []
        for arg in args :
            if isinstance(arg, list):
                res.append(arg)
            else:
                res.append([arg])

        cart_prod = list(itertools.product(*res))

        return [func(*sublist) for sublist in cart_prod]

    return wrapper       

def map_args(func):

    @functools.wraps(func)
    def wrapper(*args):
        args = list(args)
        for elem in args: 
            if isinstance(elem, list):
                length = len(elem)
                break
        try :
            length
        except:
            return func(*args)

        for i, elem in enumerate(args):
            if isinstance(elem, list):
                if len(elem) != length:
                    raise Exception("All arguments need to be of same length if it's a list")
            
            else : 
                args[i] = length * [elem]

        def get_args_i(args, i):
            return [elem[i] for elem in args]
        
        res = []
        for i in range(length):
            res.append(func(*get_args_i(args, i)))
        return res 
    
    return wrapper


def timeit(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ts = time.time()
        result = func(*args, **kwargs)
        te = time.time()

        print (f'func:{func.__name__} took: {te - ts} sec') 
        return result
    return wrapper


def telegram_update_backtest(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = f'Starting execution of function {func.__name__} at {datetime.datetime.now()}\n'
        
        try :
            desc = f"Currency:\t{args[1]['download_params']['symbols']}\n"
        except :
            desc = ''

        try :
            desc += f"Interval:\t{args[1]['download_params']['interval']}\n"
        except :
            pass

        try :
            desc += f"Strategy:\t{args[1]['strategy_name']}\n"
        except:
            pass

        msg = start + desc
        dotenv.load_dotenv()
        token = os.getenv('TOKEN')
        channelId = os.getenv('CHANNEL_ID')
        bot = telegram.Bot(token = token)
        bot.send_message(chat_id = channelId, text = msg)
        

        res = func(*args, **kwargs)

        end = f'Finished execution of function {func.__name__} at {datetime.datetime.now()}'
        #bot.send_message(chat_id = channelId, text = end)

        return res
    
    return wrapper

def error_message_handling(func):
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        try: 
            return func(*args, **kwargs)
        
        except Exception as e:
            name_args = inspect.getfullargspec(func)
            msg = f'An error occured on function {func.__name__} with parameters:\n'
            for name_arg, arg in  zip(name_args[1:], *args[1:]):
                msg += f'{name_arg}: {arg}\n\n'

            msg += f'Got exception:\n{e}\n\nProceeding'
            dotenv.load_dotenv()
            token = os.getenv('TOKEN')
            channelId = os.getenv('CHANNEL_ID')
            bot = telegram.Bot(token = token)
            bot.send_message(chat_id = channelId, text = msg)
    
    return wrapper
