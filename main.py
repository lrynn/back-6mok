from typing import Iterable

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

import room, board

# uvicorn main:app --reload


# POST method로 받을 Request Body

class RequestBody_PlaceStone(BaseModel):
    x: int
    y: int


rooms: list[room.Room] = [room.Room(0)]


app = FastAPI()

# CORS 설정 (Next.js 클라이언트와 통신 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],  # Next.js 주소
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.websocket("/chat")
async def chatMain(websocket: WebSocket):
    print(f"client connected : {websocket.client}")
    await websocket.accept() # client의 websocket접속 허용
    
    await websocket.send_text(f"Welcome client : {websocket.client}")
    try:
        while True:
            data = await websocket.receive_text() # Client 메시지 수신대기
            print(f"Received: {data} from {websocket.client}")
            await websocket.send_text(f"Echo: {data}") # Client에 메시지 전달
    except WebSocketDisconnect:
        print("Client disconnected")


@app.get("/games/{roomNumber}/get/all")
async def getAllStatus(roomNumber: int):
    status_provider = board.BoardStatusProviderForApi(rooms[roomNumber].game.board)
    board_models = status_provider.getStatus()
    return jsonable_encoder(board_models)

player_number = 1 #임시 변수
@app.post("/games/{roomNumber}/set")
async def placeStone(roomNumber: int, item: RequestBody_PlaceStone):
    if rooms[roomNumber].game.board.placeStone(player_number, item.x, item.y):
        return 200
    else:
        return 400

@app.websocket("/games/{roomNumber}/chat")
async def chatGame(websocket: WebSocket):
    pass


# 개발/디버깅용으로 사용할 앱 구동 함수
def run():
    import uvicorn
    uvicorn.run(app, reload=True)
    
# python main.py로 실행할경우 수행되는 구문
# uvicorn main:app 으로 실행할 경우 아래 구문은 수행되지 않는다.
if __name__ == "__main__":
    run()