
import sys 
from .randomizer import RandomizerUsageMode

help_flag = '--help'

def is_help_arg_passed() -> bool: 
    if len(sys.argv) < 2:
        return False

    return sys.argv[1] == help_flag

def print_help():
    print("\t\tMozart-tube")
    print('\t--randomizer:')
    
