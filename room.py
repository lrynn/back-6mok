from typing import Final, Dict, List
from random import choice

import board
import game
import account

from player import Player
from utilities import printDebug

DEFAULT_BOARD_SIZE: Final[int] = 19

DEFAULT_ROOM_NAMES: Final[tuple[str, ...]] = (
    "어서 들어오세요!",
    "즐겁게 한 판 두실 분😊",
    "저랑 뜨시죠",
    "매너게임 하실 분",
    "신의 한 수 보여드리겠습니다",
    "IQ 130 이상만이 이 문제를 풀 수 있습니다!",
    "고수는 묵묵히 돌만 두는 법"
)

class UserInRoom(Player):
    def __init__(self, board: board.Board, account_id: str) -> None:
        super().__init__(board)
        self.ACCOUNT_ID: Final[str] = account_id

    def __eq__(self, value: object) -> bool:
        if isinstance(value, UserInRoom):
            return self.ACCOUNT_ID == value.ACCOUNT_ID
        elif isinstance(value, str):
            return self.ACCOUNT_ID == value
        return False


class Room:
    def __init__(self, room_id: str) -> None:
        self.ROOM_ID: Final[str] = room_id
        self.name: str = choice(DEFAULT_ROOM_NAMES)
        self.participants: Dict[str, List[UserInRoom]] = {"black": [], "white": [], "observer": []}
        self.team_size: int = 1
        self.board_size: int = DEFAULT_BOARD_SIZE
        self.game: game.Game = game.Game(DEFAULT_BOARD_SIZE, 1)
        self.isStarted: bool = False

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
        
        self.game = game.Game(self.board_size, len(self.participants["black"]))
        self.isStarted = True