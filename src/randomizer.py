from .logger import Logger, LoggingLevel
from .config import ConfigLoader
import sys
from enum import Enum

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


def upload_existing_videos(usage_mode: RandomizerUsageMode, logger: Logger, config_loader:ConfigLoader ) -> int:
    logger.log_file_with_stdout(f'Started Randomizer Upload: with usage mode {usage_mode.name}={usage_mode.value}', LoggingLevel.Info)
    
    config_loader.check_for_ffmpeg(logger)
    config_loader.check_for_yt_dlp(logger)
    
    return 0
