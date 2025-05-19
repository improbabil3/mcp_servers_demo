# MCP Servers Demo

Questo repository contiene una demo di server MCP (Model Context Protocol) con implementazioni di base e orchestrazione.

## Struttura del progetto

- `mcp_base/`: Moduli Python di base per la gestione delle richieste MCP e l'integrazione con LLM.
- `mcp_docker/`: Esempio di server MCP containerizzato, con file di configurazione Docker e OpenAPI.

## Requisiti

- Python 3.10+
- Docker (opzionale, per lanciare il server containerizzato)

## Avvio rapido

### 1. Clona il repository
```powershell
git clone https://github.com/improbabil3/mcp_servers_demo.git ; cd mcp_servers_demo
```

### 2. Installa le dipendenze Python (per sviluppo locale)
```powershell
pip install -r mcp_docker/requirements.txt
```

### 3. Avvia il server MCP (modalità locale)
```powershell
python mcp_docker/main.py
```

### 4. Avvio tramite Docker (opzionale)
Assicurati di avere Docker installato, poi esegui:
```powershell
docker compose -f mcp_docker/docker-compose.yml up --build
```

## Note
- Ricorda di configurare le variabili d'ambiente (vedi `.env` in `mcp_base/`, non incluso nel repo).
- Per dettagli sulle API, consulta `mcp_docker/openapi.yaml`.

---

Per domande o contributi, apri una issue o una pull request su GitHub.
