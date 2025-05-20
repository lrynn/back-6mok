from typing import Final

from utilities import printDebug
from board import Board

class Player:
    def __init__(self, board: Board) -> None:
        self.stone = 0
        self.board = board
        self.team = 0

    def setTeam(self, team: int) -> None:
        self.team = team
        printDebug(1, f"Player {self.team} set.")
        return
    
    def getStone(self, amount: int) -> int:
        self.stone += amount
        printDebug(3, f"Player {self.team} got {amount} stone(s). Remaining stones: {self.stone}")
        return self.stone

    def placeStone(self, x: int, y: int) -> None:
        if self.stone:
            if self.board.placeStone(self.team, x, y):
                printDebug(2, f"Player {self.team} placed a stone at ({x}, {y}).")
                self.getStone(-1)
            else:
                printDebug(2, f"Player {self.team} tried to place stone but there was a stone already.")
        else:
            printDebug(2, f"Player {self.team} tried to place stone but he has not enough.")