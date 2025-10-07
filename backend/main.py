from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from agents import classify_user_intent, look_for_menu_items

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()

        # User classification for re routing requests to proper agentic soluction
        classified_intent = await classify_user_intent(data)
        print("Classified intent:", classified_intent)

        if classified_intent == "greeting":
            # Just a simple response for a demo
            await websocket.send_text(json.dumps({"message": f"Well hello there!"}))
            continue

        if classified_intent != "order_food" and classified_intent != "greeting":
            # Handle other intents, such as checking the menu or confirming an order for processing
            await websocket.send_text(json.dumps({"message": f"Intent '{classified_intent}' not handled in this demo."}))
            continue

        # getting here requires order_food intent
        order = await look_for_menu_items(data)

        # Broadcast updated order back to client
        await websocket.send_text(json.dumps(order))
