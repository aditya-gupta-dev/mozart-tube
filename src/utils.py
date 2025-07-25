import re 
import os 
import platform

def generate_output_filename(yt_title: str) -> str:
    sanitized_title = re.sub(r'[^a-zA-Z0-9_]', ' ', yt_title)
    suffix = " 1 Hour looped"
    youtube_title_limit = 100
    required_title_length = youtube_title_limit - len(suffix)
    
    if len(sanitized_title) > required_title_length:
        return f"{sanitized_title[:required_title_length]} {suffix}"
    else:
        return f"{sanitized_title} {suffix}"
    
def is_windows() -> bool:
    return platform.system() == "Windows"


def get_folder_size(directory: str): 
    total_size = 0
    try:
        with os.scandir(directory) as it:
            for entry in it:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += get_folder_size(entry.path)
    except (NotADirectoryError, PermissionError):
        try:
            return os.path.getsize(directory)
        except OSError:
            return 0
            
    return total_size

def format_bytes(size_bytes):
    if size_bytes is None or size_bytes < 0:
        return "0 B"
    
    units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    
    power = 0
    while size_bytes >= 1024 and power < len(units) - 1:
        size_bytes /= 1024
        power += 1
        
    return f"{size_bytes:.2f} {units[power]}"
    
def print_title():
    print("""

'##::::'##::'#######::'########::::'###::::'########::'########:'########:'##::::'##:'########::'########:
 ###::'###:'##.... ##:..... ##::::'## ##::: ##.... ##:... ##..::... ##..:: ##:::: ##: ##.... ##: ##.....::
 ####'####: ##:::: ##::::: ##::::'##:. ##:: ##:::: ##:::: ##::::::: ##:::: ##:::: ##: ##:::: ##: ##:::::::
 ## ### ##: ##:::: ##:::: ##::::'##:::. ##: ########::::: ##::::::: ##:::: ##:::: ##: ########:: ######:::
 ##. #: ##: ##:::: ##::: ##::::: #########: ##.. ##:::::: ##::::::: ##:::: ##:::: ##: ##.... ##: ##...::::
 ##:.:: ##: ##:::: ##:: ##:::::: ##.... ##: ##::. ##::::: ##::::::: ##:::: ##:::: ##: ##:::: ##: ##:::::::
 ##:::: ##:. #######:: ########: ##:::: ##: ##:::. ##:::: ##::::::: ##::::. #######:: ########:: ########:
..:::::..:::.......:::........::..:::::..::..:::::..:::::..::::::::..::::::.......:::........:::........::
""")