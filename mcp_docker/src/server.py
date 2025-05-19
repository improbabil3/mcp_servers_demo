import os
import multiprocessing
import uvicorn
from mcp.server.fastmcp import FastMCP
tasks: list[dict] = [
    {"id": 1, "item": "Buy groceries"}
]

mcp = FastMCP("docker-mcp", stateless_http=True)
app = mcp.streamable_http_app()

# Define a simple function called 'add' to be used with the MCP
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def list_items() -> list[dict]:
    """Get all pending tasks in the TODO list."""
    return tasks

@mcp.tool()
def new_item(title: str) -> dict:
    """Add a new task to the TODO list."""
    item = {"id": len(tasks) + 1, "item": title}
    tasks.append(item)
    return item

@mcp.tool()
def complete_item(id: int) -> dict:
    """Remove a task from the TODO list by its ID."""
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
            return {"status": "success"}
    return {"status": "Error: no such id"}

if __name__ == "__main__":
    if os.getenv("RUNNING_IN_PRODUCTION"):
        # Production mode with multiple workers for better performance
        uvicorn.run(
            "server:app",  # Pass as import string
            host="0.0.0.0",
            port=8080,
            workers=(multiprocessing.cpu_count() * 2) + 1,
            timeout_keep_alive=300  # Increased for SSE connections
        )
    else:
        # Development mode with a single worker for easier debugging
        uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)