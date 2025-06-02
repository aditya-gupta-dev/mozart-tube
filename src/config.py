from enum import Enum
import os 
from pathlib import Path
import json
import subprocess

from src.logger import Logger, LoggingLevel

class ConfigLoader:
    def __init__(self, logger: Logger):
        self.pwd=Path().cwd()
        self.default_config_path=f"{self.pwd}/config.json"
        self.config_data = None


        logger.log_file_with_stdout(
            message='Searching config.json',
            level=LoggingLevel.Info
        )

        try:
            with open(self.default_config_path, 'r') as config_file:
                config = json.load(config_file)
                self.config_data = config 
                logger.log_file_with_stdout('Found config.json', LoggingLevel.Info)

                asset_video_path = self.config_data[ConfigParams.ASSET_VIDEO_PATH.value]

                
                if asset_video_path and os.path.exists(asset_video_path):
                    logger.log_file_with_stdout('Asset video file found.', LoggingLevel.Info)
                else:
                    logger.log_file_with_stdout('Asset video file not found.', LoggingLevel.Fatal)
                    exit() # exiting 

                output_dir = self.config_data[ConfigParams.OUTPUT_DIRECTORY.value]
                if output_dir and os.path.exists(output_dir):
                    logger.log_file_with_stdout('Output directory exists', LoggingLevel.Info)
                else:
                    logger.log_file_with_stdout("Output directory doesn't exists, Creating one..", LoggingLevel.Error)
                    os.mkdir(output_dir)
                    logger.log_file_with_stdout('Created Output directory', LoggingLevel.Info)
        
        except FileNotFoundError as e:
            print('Not found config.json')
            logger.log_file_only(f'Not found config.json {e}', LoggingLevel.Fatal)
            exit()
        
        except Exception as ex:
            logger.log_file_with_stdout(f'Unexpected Error Occured {ex}', LoggingLevel.Fatal)
            exit()

    def get_ffmpeg_path(self):
        if self.config_data[ConfigParams.FFMPEG_PATH.value]:
            return self.config_data[ConfigParams.FFMPEG_PATH.value]
        else:
            return 'ffmpeg'
    
    def get_yt_dlp_path(self):
        if self.config_data[ConfigParams.YT_DLP_PATH.value]:
            return self.config_data[ConfigParams.YT_DLP_PATH.value]
        else:
            return 'yt-dlp'
    
    def get_final_video_duration(self) -> int:
        if self.config_data[ConfigParams.FINAL_VIDEO_DURATION.value]:
            try: 
                return int(self.config_data[ConfigParams.FINAL_VIDEO_DURATION.value])
            except Exception:
                print('Enter a valid integer in config.json for final-video-duration')
                exit()

        
    def check_for_ffmpeg(self, logger: Logger):
        ffmpeg_path = self.get_ffmpeg_path()
        search_for = 'ffmpeg'
        try:
            logger.log_file_with_stdout(f'Searching for {search_for} on your device.', LoggingLevel.Info)
            logger.log_file_only(f'Searching at {ffmpeg_path}', LoggingLevel.Info)

            proc = subprocess.run(
                [ffmpeg_path, '-version'],
                capture_output=True,
                shell=True,
                check=True
            )

            if proc.stdout:
                logger.log_file_only(f'Return Code from {search_for} {proc.returncode}', LoggingLevel.Info)
                logger.log_file_only(proc.stdout, LoggingLevel.Info)
                logger.log_file_with_stdout(f'{search_for} is installed', LoggingLevel.Info)

            if proc.stderr:
                logger.log_file_only(f'Return Code from {search_for} {proc.returncode}', LoggingLevel.Info)
                logger.log_file_only(proc.stderr, LoggingLevel.Error)
        
        except subprocess.CalledProcessError as process_error:
            logger.log_file_with_stdout(f'{search_for} returned with status code of {process_error.returncode}', LoggingLevel.Error)

        except FileNotFoundError as e:
            logger.log_file_with_stdout(f"{search_for} does not exists.{e}", LoggingLevel.Error)
            
        except Exception as e:
            logger.log_file_with_stdout(f'Unexpected Error Occured. Please submit the log files. {e}', LoggingLevel.Fatal)

    
    def check_for_yt_dlp(self, logger: Logger):
        ytdlp_path = self.get_yt_dlp_path()
        search_for = 'yt-dlp'
        try:
            logger.log_file_with_stdout(f'Searching for {search_for} on your device.', LoggingLevel.Info)
            logger.log_file_only(f'Searching at {ytdlp_path}', LoggingLevel.Info)

            proc = subprocess.run(
                [ytdlp_path, '--version'],
                capture_output=True,
                shell=True,
                check=True
            )

            if proc.stdout:
                logger.log_file_only(f'Return Code from {search_for} {proc.returncode}', LoggingLevel.Info)
                logger.log_file_only(proc.stdout, LoggingLevel.Info)
                logger.log_file_with_stdout(f'{search_for} is installed', LoggingLevel.Info)

            if proc.stderr:
                logger.log_file_only(f'Return Code from {search_for} {proc.returncode}', LoggingLevel.Info)
                logger.log_file_only(proc.stderr, LoggingLevel.Error)
        
        except subprocess.CalledProcessError as process_error:
            logger.log_file_with_stdout(f'{search_for} returned with status code of {process_error.returncode}', LoggingLevel.Error)

        except FileNotFoundError as e:
            logger.log_file_with_stdout(f"{search_for} does not exists.{e}", LoggingLevel.Error)
            
        except Exception as e:
            logger.log_file_with_stdout(f'Unexpected Error Occured. Please submit the log files. {e}', LoggingLevel.Fatal)
        



class ConfigParams(Enum):
    FFMPEG_PATH="ffmpegPath"
    YT_DLP_PATH="ytdlpPath"
    FINAL_VIDEO_DURATION="final-video-duration"
    YOUTUBE_API_KEY="youtube-api-key"
    ASSET_VIDEO_PATH="asset-video-path"
    OUTPUT_DIRECTORY="output-directory"