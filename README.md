# Krusty Krab Basic Order Handler 
This application is a web-based food ordering system that uses voice recognition to interact with users. Users speak their requests, and the system uses AI to classify their intent (such as greeting, asking for the menu, or ordering food). When a user orders, the backend ensures only valid menu items are added to the cart, groups identical items, and calculates totals. The cart is updated in real time, providing a seamless, hands-free ordering experience.

## Running the app
Requires `uv` package handler ([Installation](https://docs.astral.sh/uv/getting-started/installation/))

In the main folder, run:
```bash
uv sync
```
Then 

In backend folder run the AI application
```bash
export OPENAI_API_KEY="helloThere"
uv run uvicorn main:app 
```

A basic frontend is included to see the application in action
```bash
uv run python -m http.server 8080
```
