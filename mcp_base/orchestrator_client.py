"""
Orchestratore generico per function calling LLM + MCP server
Personalizza qui i parametri per riutilizzare il client con qualsiasi server MCP compatibile (wrapper HTTP)
"""

import requests
import os
from dotenv import load_dotenv
load_dotenv()

# === PARAMETRI CONFIGURABILI ===
MCP_URL = "http://127.0.0.1:8000"  # URL del server MCP (wrapper HTTP)
AZURE_OPENAI_URL = "https://YOUR_AZURE_OPENAI_ENDPOINT/openai/deployments/YOUR_DEPLOYMENT/chat/completions?api-version=2024-02-15-preview"
AZURE_OPENAI_KEY = "YOUR_API_KEY"

# Definizione compatta dei tool MCP disponibili
MCP_TOOL_DEFS = [
    {
        "name": "list_items",
        "description": "Restituisce l'elenco di tutti i prodotti attualmente presenti nella lista TODO.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "new_item",
        "description": "Aggiunge un nuovo prodotto alla lista TODO. Richiede il titolo del prodotto.",
        "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}
    },
    {
        "name": "complete_item",
        "description": "Rimuove un prodotto dalla lista TODO dato il suo ID.",
        "parameters": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}
    }
]

# Conversione in formato OpenAI function calling
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"]
        }
    }
    for tool in MCP_TOOL_DEFS
]

HEADERS = {
    "Content-Type": "application/json",
    "api-key": AZURE_OPENAI_KEY
}

SYSTEM_PROMPT = "Se ti viene chiesto di elencare, aggiungere o completare prodotti, usa i tool MCP disponibili."

# === FUNZIONI GENERICHE ===
def call_mcp_tool(tool_name, args=None):
    url = f"{MCP_URL}/tool/{tool_name}"
    resp = requests.post(url, json=args or {})
    resp.raise_for_status()
    return resp.json()

def ask_llm_with_tools(prompt: str, tools=None, system_prompt=None):
    """
    Orchestratore generico: gestisce il ciclo function calling tra LLM e tool MCP.
    """
    if tools is None:
        tools = MCP_TOOLS
    if system_prompt is None:
        system_prompt = SYSTEM_PROMPT
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    data = {
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto"
    }
    all_raw = []
    response = requests.post(AZURE_OPENAI_URL, headers=HEADERS, json=data)
    response.raise_for_status()
    resp_json = response.json()
    all_raw.append(resp_json)
    while resp_json["choices"][0]["message"].get("tool_calls"):
        tool_call = resp_json["choices"][0]["message"]["tool_calls"][0]
        tool_name = tool_call["function"]["name"]
        import json as _json
        tool_args = _json.loads(tool_call["function"]["arguments"])
        tool_result = call_mcp_tool(tool_name, tool_args)
        messages.append({
            "role": "assistant",
            "tool_calls": [tool_call]
        })
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "name": tool_name,
            "content": str(tool_result)
        })
        data2 = {
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto"
        }
        response2 = requests.post(AZURE_OPENAI_URL, headers=HEADERS, json=data2)
        response2.raise_for_status()
        resp_json = response2.json()
        all_raw.append(resp_json)
        content = resp_json["choices"][0]["message"].get("content")
        if content:
            return content.strip(), all_raw
    content = resp_json["choices"][0]["message"].get("content")
    return content.strip() if content else "[Nessuna risposta testuale dal modello]", all_raw

if __name__ == "__main__":
    # Esempio di utilizzo generico
    print("Risposta LLM a: 'Dammi l'elenco di tutti i prodotti'")
    risposta, raw = ask_llm_with_tools("Dammi l'elenco di tutti i prodotti")
    print(risposta)
    show = input("Vuoi vedere il dettaglio raw? (s/n): ").strip().lower()
    if show == "s":
        import pprint
        pprint.pprint(raw)
