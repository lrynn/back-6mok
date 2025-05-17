from board import Board

class Player:
    def __init__(self, board_size) -> None:
        self.stone = 0
        self.board = Board(board_size)

    def setTeam(self, team) -> None:
        self.team = team
        self.stone = 1 if team > 0 else 2
        return

    def placeStone(self, x: int, y: int) -> None:
        while self.stone:
            self.board.placeStone(self, x, y)
            
            self.stone -= 1
