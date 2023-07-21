#This file defines decorators for the vbt_projects folder
import functools
import traceback
import os

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
