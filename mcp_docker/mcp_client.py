"""
Client di test per il server MCP dockerizzato (copilot_integration_template)
Permette di invocare i tool MCP exposed dal server su http://localhost:8080/mcp
"""

import requests
import json

MCP_URL = "http://localhost:8080/mcp"

TOOLS = [
    {
        "name": "list_items",
        "description": "Restituisce l'elenco di tutti i prodotti attualmente presenti nella lista TODO.",
        "parameters": {}
    },
    {
        "name": "new_item",
        "description": "Aggiunge un nuovo prodotto alla lista TODO. Richiede il titolo del prodotto.",
        "parameters": {"title": "string"}
    },
    {
        "name": "complete_item",
        "description": "Rimuove un prodotto dalla lista TODO dato il suo ID.",
        "parameters": {"id": "integer"}
    },
    {
        "name": "add",
        "description": "Somma due numeri interi.",
        "parameters": {"a": "integer", "b": "integer"}
    }
]

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

def call_mcp_tool(tool_name, args=None):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": args or {}
        }
    }
    resp = requests.post(MCP_URL, headers=HEADERS, data=json.dumps(payload), timeout=10)
    resp.raise_for_status()
    # Gestione risposta event-stream
    for line in resp.iter_lines():
        if line.startswith(b'data: '):
            data = json.loads(line[6:])
            if "result" in data:
                return data["result"]
            elif "error" in data:
                return data["error"]
    return None

def test_all():
    print("Test: list_items")
    print(call_mcp_tool("list_items"))
    print("Test: new_item")
    print(call_mcp_tool("new_item", {"title": "Pane"}))
    print("Test: list_items dopo aggiunta")
    print(call_mcp_tool("list_items"))
    print("Test: complete_item (id=1)")
    print(call_mcp_tool("complete_item", {"id": 1}))
    print("Test: list_items dopo rimozione")
    print(call_mcp_tool("list_items"))
    print("Test: add (2+3)")
    print(call_mcp_tool("add", {"a": 2, "b": 3}))

if __name__ == "__main__":
    test_all()
