from typing import Final

from utilities import printDebug
from board import Board

class Player:
    def __init__(self, board: Board) -> None:
        self.stones = 0
        self.board = board
        self.team = 0

    def setTeam(self, team: int) -> None:
        self.team = team
        printDebug(1, f"Player {self.team} set.")
        return
    
    def getStone(self, amount: int) -> int:
        self.stones += amount
        printDebug(3, f"Player {self.team} got {amount} stone(s). Remaining stones: {self.stones}")
        return self.stones

    def placeStone(self, x: int, y: int) -> bool:
        '''
        돌을 둡니다.
        성공 여부를 반환합니다.
        '''
        if self.stones:
            if self.board.placeStone(self.team, x, y):
                printDebug(2, f"Player {self.team} placed a stone at ({x}, {y}).")
                self.getStone(-1)
                return True
            else:
                printDebug(2, f"Player {self.team} tried to place stone but there was a stone already.")
        else:
            printDebug(2, f"Player {self.team} tried to place stone but he has not enough.")
        return False