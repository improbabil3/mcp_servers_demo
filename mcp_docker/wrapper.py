import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

# Serve la cartella statica per manifest e openapi
static_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/copilot_integration_template", StaticFiles(directory=static_dir), name="static")

tasks = [
    {"id": 1, "item": "Buy groceries"}
]

class NewItemRequest(BaseModel):
    title: str

class CompleteItemRequest(BaseModel):
    id: int

@app.post("/tool/list_items")
def list_items():
    return tasks

@app.post("/tool/new_item")
def new_item(req: NewItemRequest):
    item = {"id": len(tasks) + 1, "item": req.title}
    tasks.append(item)
    return item

@app.post("/tool/complete_item")
def complete_item(req: CompleteItemRequest):
    for task in tasks:
        if task["id"] == req.id:
            tasks.remove(task)
            return {"status": "success"}
    return {"status": "Error: no such id"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("wrapper:app", host="0.0.0.0", port=8000, reload=True)
