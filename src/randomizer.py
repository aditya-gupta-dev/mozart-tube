from .logger import Logger, LoggingLevel
from .config import ConfigLoader
from .uploader.youtube_uploader import YouTubeUploader
from .uploader.uploader import Uploader 
from .processors.editor import VideoEditor 

import sys
from enum import Enum
import random
import os
from pathlib import Path

randomizer_flag = "--randomizer"


class RandomizerUsageMode(Enum):
    ALL = 1
    RANDOMLY_ONE = 2
    RANDOMLY_SELECT_FEW = 3


def is_randomizer_arg_passed() -> bool:
    if len(sys.argv) < 2:
        return False

    return randomizer_flag in sys.argv[1]


def parse_randomizer_arg() -> tuple[RandomizerUsageMode, str]:
    items: list[str] = sys.argv[1].split("=")
    if len(items) == 1 or len(items) > 2:
        return (
            RandomizerUsageMode.RANDOMLY_ONE,
            f"args not passed properly: <{items}> using default",
        )

    try:
        usage_mode = int(items[1].strip())
        if usage_mode == RandomizerUsageMode.ALL.value:
            return (RandomizerUsageMode.ALL, "")
        if usage_mode == RandomizerUsageMode.RANDOMLY_ONE.value:
            return (RandomizerUsageMode.RANDOMLY_ONE, "")
        if usage_mode == RandomizerUsageMode.RANDOMLY_SELECT_FEW.value:
            return (RandomizerUsageMode.RANDOMLY_SELECT_FEW, "")
        else:
            return (
                RandomizerUsageMode.RANDOMLY_ONE,
                f"out of range so using  default:passed usage mode={usage_mode}",
            )

    except ValueError as e:
        return (RandomizerUsageMode.RANDOMLY_ONE, f"{e} : {items[1]} so using default")
    except Exception as e:
        return (RandomizerUsageMode.RANDOMLY_ONE, f"{e} : {items[1]} so using default")


class Randomizer:
    def __init__(
        self,
        usage_mode: RandomizerUsageMode,
        logger: Logger,
        config_loader: ConfigLoader,
    ) -> None:
        self.usage_mode = usage_mode
        self.logger = logger
        self.config_loader = config_loader
        self.temp_directory = "files"

    def get_videos_according_to_usage_mode(self) -> list[str]:
        self.config_loader.check_for_ffmpeg(self.logger)
        self.config_loader.check_for_yt_dlp(self.logger)
        
        videos: list[str] = []
        
        if self.usage_mode == RandomizerUsageMode.ALL:
            self.logger.log_file_with_stdout(f'Selected {self.usage_mode.name} upload mode.', LoggingLevel.Debug)
            videos = self.__get_all_videos()
        if self.usage_mode == RandomizerUsageMode.RANDOMLY_ONE:
            self.logger.log_file_with_stdout(f'Selected {self.usage_mode.name} upload mode.', LoggingLevel.Debug)
            videos = self.__get_one_video()
        if self.usage_mode == RandomizerUsageMode.RANDOMLY_SELECT_FEW:
            self.logger.log_file_with_stdout(f'Selected {self.usage_mode.name} upload mode.', LoggingLevel.Debug)
            videos = self.__get_randomly_few_videos()
        else:
            self.logger.log_file_with_stdout(f'Selected {self.usage_mode.name} upload mode.', LoggingLevel.Debug)
            videos = self.__get_one_video()
        
        self.logger.log_file_with_stdout(f'proceeding with videos: {videos}', LoggingLevel.Debug)
        return videos

    def start_editing(self, videos: list[str]): 
        for vid in videos: 
            editor = VideoEditor(link=vid, logger=self.logger, configLoader=self.config_loader)
            editor.edit()

    def start_uploading_to_youtube(self):
        uploader = Uploader(
            logger=self.logger,
            config_loader=self.config_loader, 
            youtube_uploader=YouTubeUploader(
                logger=self.logger,
                config_loader=self.config_loader, 
            ),
        )
        
        uploader.start_uploading_to_youtube()                
             

    def __get_all_videos(self) -> list[str]:
        videos: list[str] = []
        enteries = os.listdir(self.temp_directory)
        for entry in enteries:
            path = Path(os.path.join(self.temp_directory, entry))
            if path.is_dir(): 
                videos.append(f'https://youtu.be/{entry}')
    
        return videos

    def __get_randomly_few_videos(self) -> list[str]:
        videos: list[str] = self.__get_all_videos()
        few_videos: list[str] = []
        for _ in range(random.randint(1, len(videos)-1)): 
            few_videos.append(videos[random.randint(0, len(videos)-1)])
        return few_videos

    def __get_one_video(self) -> list[str]:
        videos: list[str] = self.__get_all_videos()
        return [videos[random.randint(0, len(videos)-1)]]
        

# def upload_existing_videos(usage_mode: RandomizerUsageMode, logger: Logger, config_loader:ConfigLoader ) -> int:
#     logger.log_file_with_stdout(f'Started Randomizer Upload: with usage mode {usage_mode.name}={usage_mode.value}', LoggingLevel.Info)

#     config_loader.check_for_ffmpeg(logger)
#     config_loader.check_for_yt_dlp(logger)

#     return 0
