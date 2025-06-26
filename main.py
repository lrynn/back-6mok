from typing import Dict

from fastapi import FastAPI, Request, WebSocket, BackgroundTasks
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

# @app.websocket("/chat")
# async def chatMain(websocket: WebSocket):
#     print(f"client connected : {websocket.client}")
#     await websocket.accept() # client의 websocket접속 허용
    
#     await websocket.send_text(f"Welcome client : {websocket.client}")
#     try:
#         while True:
#             data = await websocket.receive_text() # Client 메시지 수신대기
#             print(f"Received: {data} from {websocket.client}")
#             await websocket.send_text(f"Echo: {data}") # Client에 메시지 전달
#     except WebSocketDisconnect:
#         print("Client disconnected")



# --------------------------------
#
#   /rooms
#   대기방과 관련한 api를 정의합니다.
#
# --------------------------------



#   /rooms/newRoom
#   새 방을 개설합니다.

@app.post("/rooms/newRoom")
async def makeNewRoom(item: RequestBody_Account) -> str:
    room_id: str = hex(time.time_ns())
    rooms[room_id] = room.Room(room_id)

    target_room = rooms[room_id]
    target_room.userInit(room.UserInRoom(target_room.game.board, item.account_id))

    return room_id



# --------------------------------
#
#   /games
#   게임과 관련한 api를 정의합니다.
#
# --------------------------------



#   /games/{room_id}/set
#   돌을 둡니다.

# 임시 변수
player_number = 1
order = 0
# player_number, order은 Game 클래스에서 알아서 핸들하게 하기
@app.post("/games/{room_id}/set")
async def placeStone(room_id: str, item: RequestBody_PlaceStone, background: BackgroundTasks):
    if rooms[room_id].game.board.placeStone(player_number, item.x, item.y):
        background.add_task(
            broadcast,
            room_id,
            {
                "type": "set",
                "stone": {
                    "team": player_number,
                    "order": order
                },
                "axis": [item.x, item.y]
            }
        )
        return {200: "OK"}
    else:
        return {400: "ERROR"}
    


#   /games/{room_id}/get-all
#   보드의 모든 정보를 제공합니다.

@app.get("/games/{room_id}/get-all")
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



@app.websocket("/games/{room_id}/chat")
async def chatGame(websocket: WebSocket):
    pass


# # 개발/디버깅용으로 사용할 앱 구동 함수
# def run():
#     import uvicorn
#     uvicorn.run(app, reload=True)
    
# # python main.py로 실행할경우 수행되는 구문
# # uvicorn main:app 으로 실행할 경우 아래 구문은 수행되지 않는다.
# if __name__ == "__main__":
#     run()