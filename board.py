from typing import Final, Union
from pydantic import BaseModel

from utilities import printDebug, printLine


# Stone 클래스의 Pydantic 모델
class StoneModel(BaseModel):
    team: int
    order: int

class Stone:
    def __init__(self, team=0, order=0) -> None:
        self.team: int = team
        self.order: int = order

    def toModel(self) -> StoneModel:
        return StoneModel(team=self.team, order=self.order)


class Board:
    def __init__(self, size: int = 19, stones_need_to_end: int = 6) -> None:
        self.SIZE: Final[int] = size
        self.grid: list[list[Stone]] = [[Stone()]*size for _ in range(size)]
        self.stones_need_to_end: int = stones_need_to_end
        self.order: int = 0

    def __getitem__(self, index):
        row, col = index
        return self.grid[row][col]

    def isStonePlacedIn(self, x: int, y: int) -> bool:
        printDebug(4, f"somewhere noticed if stone has placed at ({x}, {y}).")
        return bool(self.grid[x][y].team)

    def placeStone(self, player_number: int, x: int, y: int) -> bool:
        '''
        returns if stone placed successfully.
        '''
        printDebug(3, f"someone tried to place stone at ({x}, {y}).")
        if self.isStonePlacedIn(x, y):
            return False
        
        self.grid[x][y] = Stone(player_number, self.order)
        self.order += 1

        printDebug(2, f"A stone that number {player_number} has placed at ({x}, {y}).")
        return True
    

class BoardStatusProvider:
    def __init__(self, board: Board) -> None:
        self.board = board
        self.BOARD_SIZE: Final[int] = board.SIZE

    def getStatus(self) -> list[list[Stone]]:
        printDebug(4, "Somewhere tried to get the game status.")
        return self.board.grid
    
    
    def printStatus(self) -> None:
        output: str = ''
        output += "┌─" + "───"*(self.BOARD_SIZE+2) + "──┐" + '\n'
        output += "│    " + ''.join(f" {x:2}" for x in range(1, self.BOARD_SIZE + 1)) + "     │" + '\n'

        for y in range(self.BOARD_SIZE):
            output += "│ " + f"{str(y+1):2} "

            for x in range(self.BOARD_SIZE):
                output += "  "

                target_point: int = self.board[x, y].team
                if target_point > 0:
                    output += "○"
                elif target_point < 0:
                    output += "●"
                else:
                    output += "*" if (
                        all(i in (3, self.BOARD_SIZE-4) for i in (x, y))
                        or self.BOARD_SIZE%2 and all(i in (self.BOARD_SIZE//2, 3, self.BOARD_SIZE-4) for i in (x, y))
                        ) else "·"

            output += f"  {str(y+1):2}" + " │" + '\n'
        output += "│    " + ''.join(f" {x:2}" for x in range(1, self.BOARD_SIZE + 1)) + "     │" + '\n'
        output += "└─" + "───"*(self.BOARD_SIZE+2) + "──┘" + '\n'
        print(output)
    
    def checkWinByLine(self, x: int, y: int,
                            dx: int, dy: int) -> int:
        
        count: int = 0
        nx, ny = x, y

        while 0 <= nx < self.BOARD_SIZE and 0 <= ny < self.BOARD_SIZE:
            target_stone = self.board.grid[nx][ny].team

            # 아무것도 안놔져있을 경우
            if not self.board.isStonePlacedIn(nx, ny):
                count = 0
            # 뭔가 놔져있을 경우
            elif count==0:
                count = target_stone // abs(target_stone)

            # 같은 팀 돌이 연속될 경우
            if target_stone * count > 0:
                count += 1 if count>0 else -1
            # 다른 팀 돌이 나올 경우
            elif target_stone * count < 0:
                count = 2 if target_stone > 0 else -2
        
            if count:
                printDebug(4, f"count {count} at ({nx}, {ny}), diff: ({dx}, {dy}).")
            if abs(count) > self.board.stones_need_to_end:
                return count // self.board.stones_need_to_end
                
            nx += dx
            ny += dy

        return 0
    
    def checkWin(self) -> int:
        printDebug(3, "Someone tried to check winner.")

        for y in range(self.BOARD_SIZE):
            for dx, dy in ((1, 0), (1, 1), (1, -1)):
                if self.checkWinByLine(0, y, dx, dy):
                    return self.checkWinByLine(0, y, dx, dy)
        
        for x in range(self.BOARD_SIZE):
            for dx, dy in ((0, 1), (1, 1)):
                if self.checkWinByLine(x, 0, dx, dy):
                    return self.checkWinByLine(x, 0, dx, dy)
                
        for x in range(self.BOARD_SIZE):
            if self.checkWinByLine(x, self.BOARD_SIZE-1, 1, -1):
                return self.checkWinByLine(x, self.BOARD_SIZE-1, 1, -1)

        # → 방향 검사
        # dx, dy = 1, 0
        # for y in range(self.BOARD_SIZE):
        #     if self.checkWinByLine(0, y, dx, dy):
        #         return self.checkWinByLine(0, y, dx, dy)
            
        # # ↓ 방향 검사
        # dx, dy = 0, 1
        # for x in range(self.BOARD_SIZE):
        #     if self.checkWinByLine(x, 0, dx, dy):
        #         return self.checkWinByLine(x, 0, dx, dy)
            
        # # ↘ 방향 검사
        # dx, dy = 1, 1
        # for y in range(self.BOARD_SIZE):
        #     if self.checkWinByLine(0, y, dx, dy):
        #         return self.checkWinByLine(0, y, dx, dy)
        # for x in range(self.BOARD_SIZE):
        #     if self.checkWinByLine(x, 0, dx, dy):
        #         return self.checkWinByLine(x, 0, dx, dy)
            
        # # ↗ 방향 검사
        # dx, dy = 1, -1
        # for y in range(self.BOARD_SIZE):
        #     if self.checkWinByLine(0, y, dx, dy):
        #         return self.checkWinByLine(0, y, dx, dy)
        # for x in range(self.BOARD_SIZE):
        #     if self.checkWinByLine(x, self.BOARD_SIZE-1, dx, dy):
        #         return self.checkWinByLine(x, 0, dx, dy)
            
        return False
    
class BoardStatusProviderForApi(BoardStatusProvider):
    def getStatus(self) -> list[list[StoneModel]]: # type: ignore
        models = [[self.board[row, col].toModel() for col in range(self.BOARD_SIZE)] for row in range(self.BOARD_SIZE)]
        return models