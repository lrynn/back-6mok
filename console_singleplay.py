from typing import Final

from utilities import printDebug
from board import Board, BoardStatusProvider
from player import Player
import game

BOARD_SIZE: Final[int] = 19

game = game.Game(BOARD_SIZE, 1)

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
            quit()

        print(f"{'○ Black' if game.turn>0 else '● White'}\'s turn!")
        print(f"You have {player_this_turn.stone} stones.")
        print("Please input the coordination where to place stone. If you want to save this turn, just input 0.")

        input_temp = input()
        try:
            x, y = map(int, input_temp.split())
        except:
            if input_temp == '0':
                break
            if input_temp == '-1':
                quit()
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