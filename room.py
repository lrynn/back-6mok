from typing import Final, Dict, List

import board
import game
import account

from player import Player
from utilities import printDebug

DEFAULT_BOARD_SIZE: Final[int] = 13

class UserInRoom(Player):
    def __init__(self, board: board.Board, account_id: int) -> None:
        super().__init__(board)
        self.ACCOUNT_ID: Final[int] = account_id

class Room:
    def __init__(self, room_id: int) -> None:
        self.ROOM_ID: Final[int] = room_id
        self.participants: Dict[str, List[UserInRoom]] = {"black": [], "white": [], "observer": []}
        self.team_size: int = 1
        self.board_size = 13
        self.game = None

    def setBoardSize(self, board_size: int) -> None:
        '''
        오목판 크기를 조정합니다. 범위는 13x13 ~ 25x25 입니다.
        '''
        if 13 <= board_size <= 25:
            self.board_size = board_size
            printDebug(3, f"set board size {self.board_size} at room {self.ROOM_ID}.")
            return
        else:
            printDebug(3, f"Attempt to set board size to {board_size} at room {self.ROOM_ID} failed due to its range.")

    def userInit(self, user: UserInRoom) -> None:
        '''
        사용자를 방으로 들여보냅니다.

        이때 적당한 순서에 따라 흑번과 백번, 관전자로 팀을 정합니다.
        '''
        len_black: int = len(self.participants['black'])
        len_white: int = len(self.participants['white'])
        key: str = ''
        if len_white < self.team_size:
            if len_black == len_white:
                key = 'black'
            else:
                key = 'white'
        elif len(self.participants['observer']) < 11:
            key = 'observer'
        else:
            printDebug(3, f"There is not enough spaces to enter room {self.ROOM_ID} for {user.ACCOUNT_ID}.")
            return
        
        self.participants[key].append(user)
        printDebug(3, f"User {user.ACCOUNT_ID} entered to room {self.ROOM_ID} at {key} {len(self.participants[key])}")

    def moveTeam(self, user: UserInRoom, team: str) -> bool:
        '''
        사용자의 팀을 옮깁니다.

        성공 여부를 반환합니다.
        '''
        if not team in ('black', 'white', 'observer'):
            printDebug(2, f"User {user.ACCOUNT_ID} failed to move team due to wrong team key: {team}.")
            return False
        
        if len(self.participants[team]) == self.team_size:
            printDebug(2, f"User {user.ACCOUNT_ID} failed to move team {team} due to not enough spaces.")
            return False
        
        self.participants[team].append(user)
        user.setTeam(len(self.participants[team]) * (-1 if team=='white' else 1))

        printDebug(3, f"User {user.ACCOUNT_ID} set to team {user.team}.")
        return True

    def isAbleToStartGame(self) -> bool:
        '''
        게임이 시작 가능한 상태인가를 판단합니다.
        '''
        return (
            len(self.participants["black"]) > 0
            and len(self.participants["black"]) == len(self.participants["white"])
        )

    def startGame(self):
        '''
        게임을 시작합니다.
        '''
        if not self.isAbleToStartGame():
            printDebug(2, f"Room {self.ROOM_ID} could not to start game but tried.")
            return
        
        self.game = game.Game(DEFAULT_BOARD_SIZE, len(self.participants["black"]))