# Carica le variabili d'ambiente dal file .env (per configurazione sicura e flessibile)
from dotenv import load_dotenv
load_dotenv()

import requests
import os

# Configurazione: URL del server MCP (wrapper FastAPI), endpoint e chiave Azure OpenAI
MCP_URL = os.environ.get("MCP_URL", "http://127.0.0.1:8000")
AZURE_OPENAI_URL = os.environ.get("AZURE_OPENAI_URL", "https://YOUR_AZURE_OPENAI_ENDPOINT/openai/deployments/YOUR_DEPLOYMENT/chat/completions?api-version=2024-02-15-preview")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY", "YOUR_API_KEY")

# Header per autenticazione verso Azure OpenAI
HEADERS = {
    "Content-Type": "application/json",
    "api-key": AZURE_OPENAI_KEY
}

def call_mcp_tool(tool_name, args=None):
    # Esegue la chiamata HTTP al tool MCP (FastAPI wrapper)
    url = f"{MCP_URL}/tool/{tool_name}"
    resp = requests.post(url, json=args or {})
    resp.raise_for_status()
    return resp.json()

def ask_llm_with_tools(prompt: str):
    """
    Gestisce il ciclo function calling tra LLM e tool MCP:
    1. Invia il prompt all'LLM con la definizione dei tool disponibili.
    2. Se il modello risponde con una tool_call, esegue il tool MCP richiesto.
    3. Invia la risposta del tool come nuovo messaggio all'LLM.
    4. Ripete il ciclo finché il modello non restituisce una risposta naturale.
    5. Ritorna sia la risposta naturale che tutte le risposte raw (per debug).
    """
    # Costruzione dei messaggi iniziali
    messages = [
        {"role": "system", "content": "Se ti viene chiesto di elencare, aggiungere o completare prodotti, usa i tool MCP disponibili."},
        {"role": "user", "content": prompt}
    ]
    # Definizione dei tool MCP disponibili (function calling OpenAI)
    data = {
        "messages": messages,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "list_items",
                    "description": "Restituisce l'elenco di tutti i prodotti attualmente presenti nella lista TODO.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "new_item",
                    "description": "Aggiunge un nuovo prodotto alla lista TODO. Richiede il titolo del prodotto.",
                    "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_item",
                    "description": "Rimuove un prodotto dalla lista TODO dato il suo ID.",
                    "parameters": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}
                }
            }
        ],
        "tool_choice": "auto"
    }
    all_raw = []  # Per salvare tutte le risposte raw del ciclo
    # Prima chiamata all'LLM
    response = requests.post(AZURE_OPENAI_URL, headers=HEADERS, json=data)
    response.raise_for_status()
    resp_json = response.json()
    all_raw.append(resp_json)
    # Ciclo: finché il modello chiede tool_call, esegui e reinvia
    while resp_json["choices"][0]["message"].get("tool_calls"):
        tool_call = resp_json["choices"][0]["message"]["tool_calls"][0]
        tool_name = tool_call["function"]["name"]
        import json as _json
        tool_args = _json.loads(tool_call["function"]["arguments"])
        # Esegui il tool MCP richiesto
        tool_result = call_mcp_tool(tool_name, tool_args)
        # Aggiorna la storia dei messaggi secondo il protocollo OpenAI
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
        # Nuova richiesta all'LLM con la storia aggiornata
        data2 = {
            "messages": messages,
            "tools": data["tools"],
            "tool_choice": "auto"
        }
        response2 = requests.post(AZURE_OPENAI_URL, headers=HEADERS, json=data2)
        response2.raise_for_status()
        resp_json = response2.json()
        all_raw.append(resp_json)
        # Se la nuova risposta contiene content, termina
        content = resp_json["choices"][0]["message"].get("content")
        if content:
            return content.strip(), all_raw
    # Se esci dal ciclo senza content
    content = resp_json["choices"][0]["message"].get("content")
    return content.strip() if content else "[Nessuna risposta testuale dal modello]", all_raw

def main():
    import pprint
    print("Risposta LLM a: 'Dammi l'elenco di tutti i prodotti'")
    resp1, raw1 = ask_llm_with_tools("Dammi l'elenco di tutti i prodotti")
    print(resp1)
    show = input("Vuoi vedere il dettaglio raw della risposta 1? (s/n): ").strip().lower()
    if show == "s":
        pprint.pprint(raw1)

    print("\nRisposta LLM a: 'Aggiungi un nuovo prodotto chiamato Pane e mostrami la lista aggiornata'")
    resp2, raw2 = ask_llm_with_tools("Aggiungi un nuovo prodotto chiamato Pane e mostrami la lista aggiornata")
    print(resp2)
    show = input("Vuoi vedere il dettaglio raw della risposta 2? (s/n): ").strip().lower()
    if show == "s":
        pprint.pprint(raw2)

    print("\nRisposta LLM a: 'Rimuovi il prodotto Pane e mostrami la lista aggiornata'")
    prodotti, _ = ask_llm_with_tools("Dammi l'elenco di tutti i prodotti")
    import re
    id_pane = None
    for line in prodotti.splitlines():
        if "Pane" in line:
            match = re.match(r"(\d+)", line.strip())
            if match:
                id_pane = int(match.group(1))
                break
    if id_pane:
        resp3, raw3 = ask_llm_with_tools(f"Rimuovi il prodotto con id {id_pane} e mostrami la lista aggiornata")
        print(resp3)
        show = input("Vuoi vedere il dettaglio raw della risposta 3? (s/n): ").strip().lower()
        if show == "s":
            pprint.pprint(raw3)
    else:
        print("[Impossibile trovare l'id di Pane]")

if __name__ == "__main__":
    main()
