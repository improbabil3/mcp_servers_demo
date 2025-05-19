from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

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

if __name__ == "__main__":
    uvicorn.run("wrapper:app", host="127.0.0.1", port=8000, reload=True)
