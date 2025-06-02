from src.config import ConfigLoader
from src.logger import Logger

def main():
    logger = Logger()
    config_loader = ConfigLoader(logger=logger)

    config_loader.check_for_ffmpeg(logger=logger)
    config_loader.check_for_yt_dlp(logger=logger)
    

if __name__ == '__main__':
    main()