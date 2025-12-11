import sys 
from enum import Enum 

randomizer = "--randomize"

class RandomizerUsageMode(Enum): 
    ALL = 1 
    RANDOMLY_ONE = 2 
    RANDOMLY_SELECT_FEW = 3 

def is_randomizer_arg_passed() -> bool:
    if len(sys.argv) < 2:
        return False

    return sys.argv[1] == randomizer 

def upload_existing_videos(): 
    'looks for '
    pass 