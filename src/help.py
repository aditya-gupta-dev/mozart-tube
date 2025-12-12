
import sys 
from .randomizer import RandomizerUsageMode

help_flag = '--help'

def is_help_arg_passed() -> bool: 
    if len(sys.argv) < 2:
        return False

    return sys.argv[1] == help_flag

def print_help():
    print("\t\tMozart-tube(Help manual)\n")
    print('\t--randomizer Ex:--randomizer=2')
    print('\tuse existing vids on disk and upload them using different strategies')
    print(f'\t\t\t{RandomizerUsageMode.ALL.name}:{RandomizerUsageMode.ALL.value}=uploads all videos')    
    print(f'\t\t\t{RandomizerUsageMode.RANDOMLY_ONE.name}:{RandomizerUsageMode.RANDOMLY_ONE.value}=uploads only one video')    
    print(f'\t\t\t{RandomizerUsageMode.RANDOMLY_SELECT_FEW.name}:{RandomizerUsageMode.RANDOMLY_SELECT_FEW.value}=upload few videos')    
    print('\n')
    print('\t--reset: complete reset, removes asset, auth files\n')
    print('\t--clean: clean output files & assets files')
