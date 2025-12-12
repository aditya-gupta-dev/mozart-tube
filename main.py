from src.processors.editor import VideoEditor
from src.processors.downloader import VideoDownloader
from src.config import ConfigLoader
from src.logger import Logger, LoggingLevel
from src.uploader.youtube_uploader import YouTubeUploader
from src.uploader.uploader import Uploader
from src.utils import print_title, is_valid_url
import src.cleaner as cleaner
import src.randomizer as randomizer


def main():
    print_title()

    logger = Logger()

    config_loader = ConfigLoader(logger=logger)

    if cleaner.is_reset_arg_passed():
        exit(cleaner.start_reset(config_loader))

    if cleaner.is_cleaner_arg_passed():
        exit(cleaner.start_cleaner(config_loader))

    if randomizer.is_randomizer_arg_passed():
        (usage_mode, error) = randomizer.parse_randomizer_arg()
        if error != "":
            logger.log_file_with_stdout(error, LoggingLevel.Warn)
        random_uploader = randomizer.Randomizer(usage_mode, logger, config_loader)
        random_uploader.start_editing(
            random_uploader.get_videos_according_to_usage_mode()
        )
        random_uploader.start_uploading_to_youtube()
        exit(0)

    config_loader.check_for_ffmpeg(logger=logger)
    config_loader.check_for_yt_dlp(logger=logger)

    youtube_uploader = YouTubeUploader(logger=logger, config_loader=config_loader)

    youtube_uploader.authenticate()

    video_downloader = VideoDownloader(logger=logger, configLoader=config_loader)

    links = video_downloader.get_links_from_file()

    for index, link in enumerate(links):
        if index == len(links) - 1:
            break

        if not is_valid_url(link):
            logger.log_file_with_stdout(
                f"Not a valid url [ {link} ]. Skipping...", LoggingLevel.Info
            )
            continue

        video_downloader.download_video_using_pkg(link)

        video_editor = VideoEditor(link=link, logger=logger, configLoader=config_loader)

        video_editor.edit()

    uploader = Uploader(
        logger=logger, config_loader=config_loader, youtube_uploader=youtube_uploader
    )

    uploader.start_uploading_to_youtube()


if __name__ == "__main__":
    main()
