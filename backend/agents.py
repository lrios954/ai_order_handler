from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import openai
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load menu from JSON file
with open(os.path.join(os.path.dirname(__file__), "menu.json"), "r") as f:
    MENU = json.load(f)

# Get allowed item IDs from menu
allowed_item_ids = [item["id"] for item in MENU]
allowed_names = [item["name"] for item in MENU]

# Temporary in-memory order
order = {"items": []}

async def classify_user_intent(data):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that classifies user intents."},
            {"role": "user", "content": data}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "intent_classification",
                "schema": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "enum": ["greeting", "order_food", "ask_menu", "goodbye", "other"]
                        }
                    },
                    "required": ["intent"]
                }
            }
        }
    )
    parsed = json.loads(response.choices[0].message.content)
    return parsed["intent"]

async def look_for_menu_items(data):
        system_prompt = (
            "You are an order assistant for helping users choose food for an order from our menu. "
            "Only allow items from this menu: " + ", ".join(allowed_names) + ". "
            "If the user requests something not on the menu, do not include it in the response. "
            "Respond only with valid menu items."
        )

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "order",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "item_id": {"type": "string", "enum": allowed_item_ids},
                                        "quantity": {"type": "integer"},
                                        "extras": {"type": "array", "items": {"type": "string"}}
                                    },
                                    "required": ["item_id", "quantity"]
                                }
                            }
                        },
                        "required": ["items"]
                    }
                }
            }
        )

        parsed = json.loads(response.choices[0].message.content)

        # Update the global order
        order["items"].extend(parsed["items"])

        print("Current order:", order)
        
        # Group items by item_id and extras
        grouped = {}
        for item in order["items"]:
            key = (item["item_id"], tuple(item.get("extras", [])))
            if key not in grouped:
                grouped[key] = {
                    "item_id": item["item_id"],
                    "quantity": 0,
                    "extras": item.get("extras", [])
                }
            grouped[key]["quantity"] += item["quantity"]

        enriched_items = []
        total = 0
        for group in grouped.values():
            menu_item = next((m for m in MENU if m["id"] == group["item_id"]), None)
            if menu_item is None:
                print("Menu item not found:", group["item_id"])
                continue
            subtotal = menu_item["price"] * group["quantity"]
            total += subtotal
            enriched_items.append({
                **menu_item,
                "quantity": group["quantity"],
                "extras": group["extras"],
                "subtotal": round(subtotal, 2)
            })

        enriched = {
            "items": enriched_items,
            "total": round(total, 2)
        }
        return enriched