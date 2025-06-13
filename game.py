from typing import Final

from utilities import printDebug
from board import Board, BoardStatusProvider
from player import Player

class Game:
    def __init__(self, board_size: int, player_by_team: int, stones_gain_by_turn: int = 2) -> None:
        self.board = Board(board_size)
        self.boardStatus = BoardStatusProvider(self.board)
        
        self.players = [[Player(self.board) for _ in range(player_by_team)] for _ in range(2)]
        self.player_number_by_team: Final[int] = player_by_team

        self.stones_gain_by_turn = stones_gain_by_turn

        for i in range(player_by_team):
            self.players[0][i].setTeam(i+1)
            self.players[1][i].setTeam(-(i+1))

        for i in range(2):
            for player in self.players[i]:
                player.getStone(i+1)

        self.turn: int = 1

        printDebug(1, "A game has opened.")
        return

    def setTurn(self, target=0) -> None:
        if target:
            self.turn = target
            printDebug(2, f"set game turn to {target}.")
            return

        if self.turn > 0:
            self.turn = -self.turn
        else:
            if abs(self.turn) == self.player_number_by_team:
                self.turn = 1
            else:
                self.turn = -(self.turn+1)
        
        printDebug(3, f"set game turn to {self.turn}")
        return
        
