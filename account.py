from typing import Final, Dict, List

from utilities import printDebug

class Account:
    def __init__(self, id: str) -> None:
        self.ID: Final[str] = id

class Guest(Account):
    def __init__(self) -> None:
        super().__init__('guest')