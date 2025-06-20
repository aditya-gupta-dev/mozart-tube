from src.logger import Logger, LoggingLevel
from src.config import ConfigLoader
import re 
import os 
import subprocess

class VideoDownloader:
    def __init__(self, logger: Logger, configLoader: ConfigLoader):
        self.links_file_path = configLoader.get_links_file_path()
        self.logger = logger
        self.config_loader = configLoader
        self.temp_directory = "files"

        try:
            output_dir = self.config_loader.get_output_directory()
            logger.log_file_only(f'Expected output directory {output_dir}', LoggingLevel.Info)
            logger.log_file_with_stdout(f'Checking for output directory.', LoggingLevel.Info)

            if not os.path.exists(output_dir):
                logger.log_file_with_stdout(f'Creating output directory.', LoggingLevel.Info)
                os.mkdir(output_dir)
        except Exception as e:
            logger.log_file_with_stdout(f'Error Occured {e}', LoggingLevel.Fatal)
            exit()

        
        try:
            logger.log_file_only(f'Expected temp directory {self.temp_directory}', LoggingLevel.Info)
            logger.log_file_with_stdout(f'Checking for temp directory.', LoggingLevel.Info)

            if not os.path.exists(self.temp_directory):
                logger.log_file_with_stdout(f'Creating temporary directory.', LoggingLevel.Info)
                os.mkdir(self.temp_directory)
        except Exception as e:
            logger.log_file_with_stdout(f'Error Occured {e}', LoggingLevel.Fatal)
            exit()

    def get_video_id(self, url: str) -> None | str:
        self.logger.log_file_only(f'parsing link {url}', LoggingLevel.Info)
        regex = r"(?:youtu\.be\/|youtube\.com\/(?:.*v=|.*\/|.*embed\/|v\/|shorts\/))([\w-]{11})"
        match = re.search(regex, url)
        self.logger.log_file_only(f'parsed link {url} -> Result {match}', LoggingLevel.Info)
        return match.group(1) if match else None 

    def get_links_from_file(self):
        links: list[str] = []
        self.logger.log_file_only(f'Parsing data from file {self.links_file_path}', LoggingLevel.Info)
        with open(self.links_file_path, 'r') as file:
            links = file.read().split('\n')
        self.logger.log_file_only(f'Parsed Data : {links}', LoggingLevel.Info)
        return links
    
    def download_video(self, link: str):
        yt_dlp_path = self.config_loader.get_yt_dlp_path()
        try:
            print() # just a line break
            self.logger.log_file_with_stdout(f'Started Downloading {link}', LoggingLevel.Info)
            self.logger.log_file_only(f'Expected saving path {self.temp_directory}/%(id)s/input.%(ext)s', LoggingLevel.Info)
            process = subprocess.run(
                [yt_dlp_path, link, '--output', f'{self.temp_directory}/%(id)s/input.%(ext)s'],
                capture_output=True,
                shell=True,
                check=True   
            )
            
            self.logger.log_file_only(f'yt-dlp returncode {process.returncode}', LoggingLevel.Info)
            self.logger.log_file_only(f'yt-dlp args {process.args}', LoggingLevel.Info)
    
            if process.stdout:
                self.logger.log_file_only(f'yt-dlp stdout: {process.stdout}', LoggingLevel.Info)
                self.logger.log_file_with_stdout(f'Completed Downloading {link}', LoggingLevel.Info)
            if process.stderr:
                self.logger.log_file_only(f'yt-dlp stderr: {process.stderr}', LoggingLevel.Error)
                self.logger.log_file_only(f'Probably Failed Downloading {link}', LoggingLevel.Error)
        except subprocess.CalledProcessError as process_error:
            self.logger.log_file_with_stdout(f'Failed to download the video {link}', LoggingLevel.Error)
            self.logger.log_file_only(f'yt-dlp returned with status code {process_error.returncode}', LoggingLevel.Error)
            self.logger.log_file_only(f'yt-dlp stderr {process_error.stderr}', LoggingLevel.Error)
        except Exception as e:
            self.logger.log_file_with_stdout(f'Fatal error, quitting.', LoggingLevel.Fatal)
            self.logger.log_file_only(f'Error {e}.', LoggingLevel.Fatal)