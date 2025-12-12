import sys
import os
import shutil
import src.utils as utils
import src.config as config

clean_flag = "--clean"
reset_flag = "--reset"


def is_reset_arg_passed() -> bool:
    if len(sys.argv) < 2:
        return False

    return sys.argv[1] == reset_flag


def is_cleaner_arg_passed() -> bool:
    if len(sys.argv) < 2:
        return False

    return sys.argv[1] == clean_flag


def start_reset(config_loader: config.ConfigLoader) -> int:
    print(f"Passed Args: {sys.argv}")
    print("Starting reset")

    asset_video_path = config_loader.get_asset_video_path()
    links_file_path = config_loader.get_links_file_path()

    if os.path.exists(asset_video_path) and os.path.isfile(asset_video_path):
        os.remove(asset_video_path)
        print("Removed asset video path")
    else:
        print(f"asset video was not found: checked at [{asset_video_path}]")

    if os.path.exists(links_file_path) and os.path.isfile(links_file_path):
        with open(links_file_path, "w") as file_handler:
            file_handler.write("")
            print("emptied links file")
    else:
        print(f"links file was not found: checked at [{links_file_path}]")

    return start_cleaner(config_loader)


def start_cleaner(config_loader: config.ConfigLoader) -> int:
    print(f"Passed Args: {sys.argv}")
    print("Starting cleaner")

    files_dir = "files"
    output_dir = config_loader.get_output_directory()

    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        folder_size = utils.format_bytes(utils.get_folder_size(output_dir))
        print(f"Removing output folder [{folder_size}] [{output_dir}]")
        shutil.rmtree(output_dir)
    else:
        print(f"output folder was not found: checked at [{output_dir}]")

    if os.path.exists(files_dir) and os.path.isdir(files_dir):
        folder_size = utils.format_bytes(utils.get_folder_size(files_dir))
        print(f"Removing files folder: [{folder_size}] [{folder_size}]")
        shutil.rmtree(files_dir)
    else:
        print(f"file folder was not found: checked at [{files_dir}]")

    enteries, count = os.listdir("."), 0
    for entry in enteries:
        if entry.endswith(".log"):
            print(f"removing log file: {entry}")
            os.remove(entry)
            count = count + 1

    if count == 0:
        print("no log files were present")
    else:
        print(f"removed a total of {count} log files")

    return 0
