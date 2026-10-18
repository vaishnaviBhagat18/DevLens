# DevLens Full-Stack Demo Setup

## Scope

Prototype: enter a **public GitHub repository URL**, run GitPython repository cloning, repository scanning, technology detection, Tree-sitter parsing, import/dependency extraction, NetworkX module graph construction, context selection, and structured local Ollama explanations. View results through React.

The **login/signup pages are UI-only** (no server-side authentication). **ZIP upload, persistent project history, architecture/flow static inference, and full multi-language semantics** are not yet implemented. The flow and architecture descriptions on the report page are AI interpretations based on available evidence, not full static verification. Generated AI insights can be incomplete or inaccurate.

## Prerequisites

- Python 3.12 and a project-local `.venv`
- Node.js and npm
- Git installed and on PATH
- Ollama for Windows with `qwen2.5-coder:3b` model pulled and its local server running

## Start services from project root

Terminal A:

```bat
.venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Terminal B:

```bat
npm install
npm run dev
```

Open `http://localhost:5173/`. The login page is currently a UI demonstration; enter any valid-looking email and password to navigate to the dashboard, then select **Analyze Repository**. You may also open `http://localhost:5173/upload` directly.

## Run demo

Use `https://github.com/vaishnaviBhagat18/BookMySlot`. Wait for source scanning and local model inference to finish. The report contains project overview, tech stack, file statistics, architecture interpretation, key modules, features, sequence of steps, dependency graph, detected Express API routes, and downloadable raw JSON.

`http://127.0.0.1:8000/docs` provides Swagger testing for `POST /analyze`. Vite forwards frontend requests for `/analyze` to FastAPI on port 8000 in development.

## API contract

```
POST /analyze
Content-Type: application/json
{"repository_url":"https://github.com/vaishnaviBhagat18/BookMySlot"}
```

Success JSON fields include `project_name`, `statistics`, `files`, `directories`, `technology`, `code_analysis`, `ai_insights`, and `repository_url`.

## Implementation notes

- Frontend source is in root `src/`, matching the merged main branch; Python backend source stays in root `backend/`.
- The graph has directed edges: `source` imports `target`.
- The frontend only visualizes returned evidence. It does not run a second analysis on the client.
- Results are cached only in the current browser tab session, not stored in a database.
- Static JS/TS extraction is implemented, while other language grammars may parse without equivalent specialized extraction.
- `OLLAMA_HOST` normally defaults to localhost, and Python Ollama client contacts the locally running server.
