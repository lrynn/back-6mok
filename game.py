from typing import Final

from utilities import printDebug
from board import Board, BoardStatusProvider
from player import Player

class Game:
    def __init__(self, board_size: int, player_by_team: int) -> None:
        self.board = Board(board_size)
        self.boardStatus = BoardStatusProvider(self.board)
        
        self.players = [[Player(self.board) for _ in range(player_by_team)] for _ in range(2)]
        self.player_number_by_team: Final[int] = player_by_team

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
        

def consoleSinglePlay(size: int):
    game = Game(size, 1)

    while True:
        this_turn = game.turn
        player_this_turn = game.players[0 if this_turn>0 else 1][0]

        chance_to_place_stone = 3
        while player_this_turn.stone:
            if not chance_to_place_stone:
                break

            game.boardStatus.printStatus()

            winner = game.boardStatus.checkWin()
            if winner:
                print("Game Set!")
                print("The Winner Is...", "○ Black" if winner>0 else "● White", "!")
                return

            print(f"{'○ Black' if game.turn>0 else '● White'}\'s turn!")
            print(f"You have {player_this_turn.stone} stones.")
            print("Please input the coordination where to place stone. If you want to save this turn, just input 0.")

            try:
                input_temp = input()
                if input_temp == '0':
                    break

                x, y = map(int, input_temp.split())
            except:
                print("Wrong input! Please check it and repeat.")
                continue

            if 0 < x <= game.board.SIZE and 0 < y <= game.board.SIZE:
                player_this_turn.placeStone(x-1, y-1)
                chance_to_place_stone -= 1
            else:
                print("Wrong coordination! Please check it and repeat.")
                continue
        
        player_this_turn.getStone(2)
        game.setTurn()

consoleSinglePlay(19)