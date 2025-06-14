from src.processors.editor import VideoEditor
from src.processors.downloader import VideoDownloader
from src.config import ConfigLoader
from src.logger import Logger
from src.uploader.youtube_uploader import YouTubeUploader
from src.uploader.uploader import Uploader
from src.utils import print_title

def main():

    print_title()

    logger = Logger()
    
    config_loader = ConfigLoader(logger=logger)
    config_loader.check_for_ffmpeg(logger=logger)
    config_loader.check_for_yt_dlp(logger=logger)

    youtube_uploader = YouTubeUploader(
        logger=logger,
        config_loader=config_loader
    )

    youtube_uploader.authenticate()

    video_downloader = VideoDownloader(
        logger=logger,
        configLoader=config_loader
    )
    
    links = video_downloader.get_links_from_file()

    for index, link in enumerate(links):
        if index == len(links) - 1:
            break

        video_downloader.download_video(link)

        video_editor = VideoEditor(
            link=link, 
            logger=logger,
            configLoader=config_loader
        )

        video_editor.edit()

    uploader = Uploader(
        logger=logger,
        config_loader=config_loader,
        youtube_uploader=youtube_uploader
    )

    uploader.start_uploading_to_youtube()
    
    

if __name__ == '__main__':
    main()