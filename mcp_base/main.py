from mcp.server.fastmcp import FastMCP

mcp = FastMCP("basemcp")

tasks: list[dict] = [
    {"id": 1, "item": "Buy groceries"}
]

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
    mcp.run(transport="http")

