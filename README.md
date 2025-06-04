# Nell Beta 2

Nell Beta 2 is an experimental writing platform. The backend is built with FastAPI and
exposes project management and LightRAG bucket features, while the frontend
uses React (Vite) for the user interface.

## Project Creation Workflow

1. **Create a project**
   - Send a `POST` request to `/projects/` with a JSON payload:
     ```json
     {
       "name": "my_project",
       "description": "Optional description",
       "project_type": "creative_writing"
     }
     ```
   - A new folder is created under `backend/projects/` with a SQLite database and
     a `lightrag_data` directory.
   - Default tables such as `characters` and `scenes` (for `creative_writing` projects)
     are generated automatically.

2. **Interact with the project**
   - Use the API endpoints below to inspect tables, create LightRAG buckets and
     upload documents.

## API Endpoints

The backend server runs on `http://localhost:8000` by default.

### Projects
- `POST /projects/` – create a project.
- `GET /projects/` – list projects.
- `GET /projects/{project_id}` – get project details.
- `DELETE /projects/{project_id}` – delete a project.
- `GET /projects/{project_id}/tables` – list tables in the project database.
- `GET /projects/{project_id}/tables/{table_name}` – table schema and row count.
- `GET /projects/{project_id}/tables/{table_name}/data?limit=100` – preview table data.
- `GET /projects/{project_id}/status` – summary of project paths and tables.

### Buckets
- `POST /projects/{project_id}/buckets/` – create a LightRAG bucket.
- `GET /projects/{project_id}/buckets/` – list buckets for a project.
- `GET /projects/{project_id}/buckets/{bucket}` – bucket information.
- `POST /projects/{project_id}/buckets/{bucket}/upload` – upload a text file.
- `POST /projects/{project_id}/buckets/{bucket}/upload-text` – upload raw text content.
- `POST /projects/{project_id}/buckets/{bucket}/toggle` – activate or deactivate a bucket.
- `POST /projects/{project_id}/buckets/query` – query multiple buckets.
- `GET /projects/{project_id}/buckets/{bucket}/status` – bucket status.

### Utility
- `GET /health` – simple health check.

## Required Environment Variables

The backend reads configuration from `backend/.env` (or the environment):

- `OPENAI_API_KEY` – OpenAI key used by LightRAG.
- `LIGHTRAG_WORKING_DIR` – base directory for LightRAG data.
- `PROJECTS_DIR` – where project folders are stored.
- `DATABASE_URL` – connection string for the project index database.
- `DEBUG` and `LOG_LEVEL` – backend logging configuration.
- `API_HOST` and `API_PORT` – bind address for the FastAPI server.

The frontend expects `VITE_API_URL` to point to the backend URL.

## Running Tests

Install backend dependencies and run `pytest` from the repository root:

```bash
pip install -r backend/requirements.txt
pytest
```

(There are currently no unit tests but the command is provided for future use.)

## Contributing

1. Fork the repository and create a feature branch.
2. Install backend and frontend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```
3. Start the backend:
   ```bash
   uvicorn backend.main:app --reload
   ```
4. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```
5. Submit a pull request with your changes.

