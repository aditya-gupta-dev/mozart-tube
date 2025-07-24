import sys

clean_flag = '--clean'

def is_cleaner_arg_passed() -> bool:
    if len(sys.argv) < 2:
        return False

    return sys.argv[1] == clean_flag

def start_cleaner() -> int:
    return 0