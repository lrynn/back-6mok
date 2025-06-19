from typing import Union

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

import room


# uvicorn main:app --reload


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
async def websocket_chat(websocket: WebSocket):
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

@app.get("/game/{roomNumber}/all")
async def getAllStatus():
    pass

@app.post("/game/{roomNumber}")
async def placeStone(axis: tuple[int]):
    pass

# 개발/디버깅용으로 사용할 앱 구동 함수
def run():
    import uvicorn
    uvicorn.run(app)
    
# python main.py로 실행할경우 수행되는 구문
# uvicorn main:app 으로 실행할 경우 아래 구문은 수행되지 않는다.
if __name__ == "__main__":
    run()