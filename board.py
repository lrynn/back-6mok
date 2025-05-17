from player import Player

class Board:
    def __init__(self, size: int) -> None:
        self.size = size
        self.grid: list = [[0]*size for _ in range(size)]

    def isStonePlacedIn(self, x: int, y: int) -> bool:
        return bool(self.grid[x][y])

    def placeStone(self, player: Player, x: int, y: int) -> None:
        if self.isStonePlacedIn(x, y):
            return
        
        self.grid[x][y] = player.team
        return
    
    def checkWinByLine(self, x, y, dx, dy) -> int:
        count = self.grid[x][y]
        nx, ny = x + dx, y + dy

        while 0 <= nx < self.size and 0 <= ny < self.size:
            if abs(count) == 6:
                return count // 6
            
            # 아무것도 안놔져있을 경우
            if not self.isStonePlacedIn(x, y):
                count = 0

            # 같은 팀 돌이 연속될 경우
            elif self.grid[nx][ny] * count > 0:
                count += 1
            # 다른 팀 돌이 나올 경우
            elif self.grid[nx][ny] * count < 0:
                count = self.grid[nx][ny]
                
            nx += dx
            ny += dy

        return 0
    
    def checkWin(self) -> int:
        # → 방향 검사
        dx, dy = 1, 0
        for y in range(self.size):
            if self.checkWinByLine(0, y, dx, dy):
                return self.checkWinByLine(0, y, dx, dy)
            
        # ↓ 방향 검사
        dx, dy = 0, 1
        for x in range(self.size):
            if self.checkWinByLine(x, 0, dx, dy):
                return self.checkWinByLine(x, 0, dx, dy)
            
        # ↘ 방향 검사
        dx, dy = 1, 1
        for y in range(self.size-6):
            if self.checkWinByLine(0, y, dx, dy):
                return self.checkWinByLine(0, y, dx, dy)
        for x in range(self.size-6):
            if self.checkWinByLine(x, 0, dx, dy):
                return self.checkWinByLine(x, 0, dx, dy)
            
        # ↗ 방향 검사
        dx, dy = 1, -1
        for y in range(self.size-6):
            if self.checkWinByLine(0, y, dx, dy):
                return self.checkWinByLine(0, y, dx, dy)
        for x in range(self.size-6):
            if self.checkWinByLine(x, self.size-1, dx, dy):
                return self.checkWinByLine(x, 0, dx, dy)
            
        return 0