from src.config import ConfigLoader
from src.logger import Logger, LoggingLevel
import os

from src.uploader.youtube_uploader import YouTubeUploader 

class Uploader:
    def __init__(self, config_loader: ConfigLoader, logger: Logger, youtube_uploader: YouTubeUploader):
        self.config_loader = config_loader
        self.logger = logger
        self.youtube_uploader = youtube_uploader
        self.video_folders = self.list_elements_in_output_directory()

    def list_elements_in_output_directory(self) -> list[str]:
        try:
            output_directory = self.config_loader.get_output_directory()
            return os.listdir(output_directory)
        except Exception as os_error:
            self.logger.log_file_with_stdout(f'Unexpected Error Occured while reading output directory', LoggingLevel.Fatal)
            self.logger.log_file_only(f'Output directory error :{os_error}', LoggingLevel.Fatal)        
            return []
        
    def get_video_file(self, items: list[str]) -> str | None:
        for item in items:
            if "mp4" in item:
                return item
        return None

    def start_uploading_to_youtube(self):
        try:
            for video_folder in self.video_folders:
                output_dir = self.config_loader.get_output_directory()
                items_dir = os.path.join(output_dir, video_folder)
                items = os.listdir(items_dir)

                video_file = self.get_video_file(items)
                
                if not video_file:
                    self.logger.log_file_with_stdout(f'No video found - Search at: {items_dir} Items: {items}', LoggingLevel.Error)
                    continue

                self.youtube_uploader.upload_video(
                    video_file=f'{items_dir}/{video_file}',
                    title=os.path.splitext(video_file)[0],
                    tags=[''],
                    description='idk',
                    privacy_status='public'                    
                )

        except Exception as e:
            self.logger.log_file_with_stdout("Error occured at the ending", LoggingLevel.Error)
            self.logger.log_file_with_stdout(f"Error {e}", LoggingLevel.Error)
