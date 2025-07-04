from typing import Dict, Union

from fastapi import FastAPI, Request, WebSocket, BackgroundTasks, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from json import JSONEncoder
import asyncio, time

import room, board, player

# uvicorn main:app --reload


PING_INTERVAL = 25


# POST method로 받을 Request Body

class RequestBody_PlaceStone(BaseModel):
    x: int
    y: int

class RequestBody_Account(BaseModel):
    account_id: str



class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, account_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][account_id] = websocket

    def disconnect(self, room_id: str, account_id: str):
        if room_id in self.active_connections and account_id in self.active_connections[room_id]:
            del self.active_connections[room_id][account_id]

    async def broadcast(self, message: str, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id].values():
                await connection.send_text(message)

manager = ConnectionManager()


rooms: Dict[str, room.Room] = {"0": room.Room("0")}

# {game_id: set[asyncio.Queue]}
SUBSCRIBERS: dict[str, set[asyncio.Queue]] = {}

app = FastAPI()

# CORS 설정 (Next.js 클라이언트와 통신 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],  # Next.js 주소
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


# --------------------------------
#
#   /rooms
#   대기방과 관련한 api를 정의합니다.
#
# --------------------------------



#   /rooms/newRoom
#   새 방을 개설합니다.

def findDuplicatedRoomId() -> str:
    while True:
        room_id = hex(time.time_ns())[2:]
        if room_id not in rooms:
            return room_id

@app.post("/rooms/newRoom")
async def openNewRoom(item: RequestBody_Account):
    room_id: str = findDuplicatedRoomId()
    rooms[room_id] = room.Room(room_id)

    print("Room", room_id, "opened. Num of rooms:", len(rooms))

    return {"room_id": room_id}



#   /rooms/all
#   방 리스트를 제공합니다.

@app.get("/rooms/all")
async def getAllRoomsId():
    all_rooms_info = [
        {"id": room_id, "is_started": room_obj.isStarted}
        for room_id, room_obj in rooms.items()
    ]
    return jsonable_encoder(all_rooms_info)



#   /rooms/{room_id}/info
#   해당 방의 정보를 제공합니다.

@app.get("/rooms/{room_id}/info")
async def getRoomInfo(room_id: str):
    target_room = rooms[room_id]

    value = {
        "name": target_room.name,
        "participants": len(target_room.participants["black"]) + len(target_room.participants["white"]),
        "game": {
            "boardSize": target_room.board_size,
            "teamSize": target_room.team_size,
            "isStarted": target_room.isStarted
        }
    }

    return jsonable_encoder(value)



#   /ws/{room_id}/{account_id}
#   

async def popRoom(room_id) -> None:
    if not (len(rooms[room_id].participants["black"])+len(rooms[room_id].participants["white"])+len(rooms[room_id].participants["observer"])):
        rooms.pop(room_id)
        print("Room", room_id, "popped. Num of rooms:", len(rooms))

@app.websocket("/ws/{room_id}/{account_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, account_id: str):
    if room_id not in rooms:
        await websocket.close(code=4000, reason="Room not found")
        return
    
    await manager.connect(websocket, room_id, account_id)
    target_room = rooms[room_id]
    target_room.userInit(room.UserInRoom(target_room.game.board, account_id))
    await manager.broadcast(f"User {account_id} has entered the room.", room_id)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"[{account_id}]: {data}", room_id)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(room_id, account_id)
        for team in ["black", "white", "observer"]:
            for i in range(len(rooms[room_id].participants[team])):
                if rooms[room_id].participants[team][i] == account_id:
                    rooms[room_id].participants[team].pop(i)
                break
        await popRoom(room_id)
        await manager.broadcast(f"User {account_id} has left the room.", room_id)



# --------------------------------
#
#   /games
#   게임과 관련한 api를 정의합니다.
#
# --------------------------------



#   /games/{room_id}/board/status-all
#   보드의 모든 정보를 제공합니다.

@app.get("/games/{room_id}/status-all")
async def getAllStatus(room_id: str):
    status_provider = board.BoardStatusProviderForApi(rooms[room_id].game.board)
    board_models = status_provider.getStatus()
    return jsonable_encoder(board_models)



#   /games/{room_id}/sse
#   Server Side Event 핸들러입니다.

async def broadcast(room_number: str, payload: dict):
    for q in list(SUBSCRIBERS.get(room_number, [])):
        # 큐가 가득 차 있으면 skip(느린 클라 보호)
        if q.full():
            continue
        await q.put(JSONEncoder().encode(payload))
    
@app.get("/games/{room_id}/sse")
async def sse(room_id: str, request: Request):
    queue = asyncio.Queue()
    SUBSCRIBERS.setdefault(room_id, set()).add(queue)

    async def event_stream():
        last_sent = time.time()
        try:
            while True:
                # ① 새 이벤트 대기 (없으면 timeout)
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=PING_INTERVAL)
                    yield f"data: {jsonable_encoder(data)}\n\n"
                    last_sent = time.time()
                except asyncio.TimeoutError:
                    # ② idle ping (": comment") 으로 연결 유지
                    yield ": ping\n\n"

                # ③ 클라이언트가 끊겼으면 정리
                if await request.is_disconnected():
                    break
        finally:
            SUBSCRIBERS[room_id].discard(queue)

    headers = {"Cache-Control": "no-cache"}
    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)



#   /games/{room_id}/set
#   돌을 둡니다.

# 임시 변수
player_number = 1
order = 0
# player_number, order은 Game 클래스에서 알아서 핸들하게 하기
@app.post("/games/{room_id}/set")
async def placeStone(room_id: str, item: RequestBody_PlaceStone):
    global order
    target_room: room.Room = rooms[room_id]
    
    if (item.x >= target_room.board_size or item.y >= target_room.board_size or
        item.x < 0 or item.y < 0):
        return {501: "Axis out of range"}
    
    if target_room.game.board.placeStone(player_number, item.x, item.y):
        order += 1
        await manager.broadcast(
            JSONEncoder().encode({
                "type": "set",
                "payload": {
                    "stone": {
                        "team": player_number,
                        "order": order
                    },
                    "axis": [item.x, item.y]
                }
            }),
            room_id
        )
        return {200: "OK"}
    else:
        return {400: "ERROR"}


# # 개발/디버깅용으로 사용할 앱 구동 함수
# def run():
#     import uvicorn
#     uvicorn.run(app, reload=True)
    
# # python main.py로 실행할경우 수행되는 구문
# # uvicorn main:app 으로 실행할 경우 아래 구문은 수행되지 않는다.
# if __name__ == "__main__":
#     run()