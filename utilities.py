from typing import Final

# An discription for DEBUG_LEVEL
# level 1: Critical to whole game flow.
# level 2: An important process for a turn.
# level 3: Just a process of a turn.
# level 4: It doesn't be needed normally.

DEBUG_LEVEL: Final[int] = 2
def printDebug(level: int, content: str) -> None:
    if DEBUG_LEVEL >= level:
        print(f"[DEBUG lv.{level}] | {content}", end="\n\n" if level==1 else "\n")
    return