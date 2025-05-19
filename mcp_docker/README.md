# Copilot/ChatGPT Plugin Integration Template

Questa cartella contiene i file necessari per esporre i tool MCP come plugin/function calling per LLM (GitHub Copilot Chat, ChatGPT, Claude, ecc.).

## Contenuto
- `.well-known/ai-plugin.json`: Manifest plugin OpenAI/ChatGPT
- `openapi.yaml`: Specifica OpenAPI degli endpoint/tool MCP
- `README.md`: Istruzioni per pubblicazione e utilizzo

## Come usare
1. Pubblica questi file su un endpoint raggiungibile (es: reverse proxy, FastAPI static, nginx, ecc.).
2. Assicurati che il percorso `/copilot_integration_template/.well-known/ai-plugin.json` sia accessibile pubblicamente.
3. Configura la chat/LLM per puntare al tuo endpoint MCP e manifest.

**Nota:** Non è necessario modificare il codice esistente. Questa integrazione è non-invasiva e pensata per demo e sviluppo.
