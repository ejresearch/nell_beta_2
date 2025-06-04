# Nell Beta 2

An **AI writing platform** with modular workflows:
**Start**, **Intake**, **Brainstorm**, **Write**.

## Backend Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

### Environment Variables

The backend reads configuration from environment variables (see `backend/.env` for defaults):

- `OPENAI_API_KEY` – API key for language model access
- `LIGHTRAG_WORKING_DIR` – directory for LightRAG data
- `PROJECTS_DIR` – where projects are stored
- `DATABASE_URL` – SQLite connection string
- `DEBUG`/`LOG_LEVEL` – development settings
- `API_HOST` and `API_PORT` – FastAPI server address

### Running the server

Start the FastAPI app with uvicorn:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server (default `http://localhost:5173`) communicates with the backend at
`http://localhost:8000`. Set `VITE_API_URL` to override the API base URL.

## Usage Notes

The root endpoint shows the backend status:
```bash
curl http://localhost:8000/
```

Create a project:
```bash
curl -X POST http://localhost:8000/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"demo","description":"Demo project"}'
```

List projects:
```bash
curl http://localhost:8000/projects
```

Other endpoints expose bucket management and text generation (e.g. `/brainstorm`, `/write`).

## Workflows

1. **Start** – initialize a project.
2. **Intake** – upload and ingest text into buckets.
3. **Brainstorm** – generate ideas with the language model.
4. **Write** – produce final content using generated outputs.
