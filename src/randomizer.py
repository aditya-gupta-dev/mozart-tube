from logger import Logger
import sys
from enum import Enum

randomizer = "--randomize"


class RandomizerUsageMode(Enum):
    ALL = 1
    RANDOMLY_ONE = 2
    RANDOMLY_SELECT_FEW = 3


def is_randomizer_arg_passed() -> bool:
    if len(sys.argv) < 2:
        return False

    return sys.argv[1] == randomizer


def parse_randomizer_arg() -> tuple[RandomizerUsageMode, str]:
    items: list[str] = sys.argv[1].split("=")
    if len(items) == 1 or len(items) > 2:
        return (
            RandomizerUsageMode.RANDOMLY_ONE,
            f"args not passed properly: <{items}>",
        )

    usage_mode = RandomizerUsageMode.RANDOMLY_ONE

    try:
        usage_mode = int(items[1].strip())
        if usage_mode == RandomizerUsageMode.ALL:
            return (RandomizerUsageMode.ALL, "")
        if usage_mode == RandomizerUsageMode.RANDOMLY_ONE:
            return (RandomizerUsageMode.RANDOMLY_ONE, "")
        if usage_mode == RandomizerUsageMode.RANDOMLY_SELECT_FEW:
            return (RandomizerUsageMode.RANDOMLY_SELECT_FEW, "")
        else:
            return (
                RandomizerUsageMode.RANDOMLY_ONE,
                f"out of range so using  default:{usage_mode}",
            )

    except ValueError as e:
        return (RandomizerUsageMode.RANDOMLY_ONE, f"{e} : {items[1]}")
    except Exception as e:
        return (RandomizerUsageMode.RANDOMLY_ONE, f"{e}")


def upload_existing_videos(usage_mode: RandomizerUsageMode, logger: Logger) -> int:
    return 0
