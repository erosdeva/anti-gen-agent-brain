# Adversarial Identification Project

**An Agentic AI memory agent built with [Google ADK](https://google.github.io/adk-docs/)**

No vector database. No embeddings. Just an LLM that reads, thinks, and writes structured memory that has been pre-selected to ensure consistent results regarding AI Ethics as well as identification of Generative AI Content.

## How it is structured

### Project Overview

The agent is fed information from its development roots pertainning to its topics. 

The goal of its ingested data and the purpose of the overall project can be found here: [Adv. Provenance](https://docs.google.com/document/d/1bioOjigse8OnqxMKr0OySSDd0KXDaTQfKCZcodX2GXM/edit?tab=t.0)

### 2. Query

Ask any question. The **QueryAgent** reads all pre-selected memories and consolidation insights, then synthesizes an answer with source citations:

```
Q: "What should I focus on?"

A: "Based on your memories, prioritize:
   1. AI Ethics [Memory 2]
   2. Watermarking of synthetic media [memory 4]
```

## Running Locally

### 1. Set your API key

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

Get your API key from [Vertex AI Studio](https://vertexai.google.com/) or [Google AI Studio](https://aistudio.google.com/).

### 2. Start the agent

```bash
python3 main.py
```

The agent should now be running:
- Watching `./inbox/` for new files (text, images, audio, video, PDFs)
- Consolidating every 30 minutes
- Serving queries at `http://localhost:8501`


## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/status` | GET | Memory statistics (counts) |
| `/memories` | GET | List all stored memories |
| `/ingest` | POST | Ingest new text (`{"text": "...", "source": "..."}`) |
| `/query?q=...` | GET | Query memory with a question |
| `/consolidate` | POST | Trigger manual consolidation |
| `/delete` | POST | Delete a memory (`{"memory_id": 1}`) |
| `/clear` | POST | Delete all memories (full reset) |

## CLI Options

```bash
python agent.py [options]

  --watch DIR              Folder to watch (default: ./inbox)
  --port PORT              HTTP API port (default: 8888)
  --consolidate-every MIN  Consolidation interval (default: 30)
```

## Project Structure

```
always-on-memory-agent/
├── agent.py          # Always-on ADK agent (the real thing)
├── dashboard.py      # Streamlit UI (connects to agent API)
├── requirements.txt  # Dependencies
├── inbox/            # Drop any file here for auto-ingestion
├── docs/             # Image assets
└── memory.db         # SQLite database (created automatically)
```

## Why Gemini 3.1 Flash-Lite?

This agent runs continuously. Cost and speed matter more than raw intelligence for background processing:

- **Fast**: Low-latency ingestion and retrieval, designed for continuous background operation
- **Cheap**: Negligible cost per session, making 24/7 operation practical
- **Smart enough**: Extracts structure, finds connections, synthesizes answers

## Built With

- [Google ADK](https://google.github.io/adk-docs/) (Agent Development Kit) for agent orchestration
- [Gemini 3.1 Flash-Lite](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-1-flash-lite) for all LLM operations
- SQLite for persistent memory storage
- aiohttp for the HTTP API
- Streamlit for the dashboard

## License

MIT