# Nell Beta 2

Nell is a modular AI writing platform that combines a React frontend with a FastAPI backend. Projects use SQLite for structured data and integrate [LightRAG](https://github.com/jessevig/light-rag) for knowledge retrieval.

## Getting Started

### Backend
1. Activate the virtual environment and run the API server:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload
   ```
   The API is served at http://localhost:8000.

### Frontend
1. Install dependencies and start Vite:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Access the app at http://localhost:5173.

### Environment
Set `OPENAI_API_KEY` before starting the backend to enable LightRAG operations.

## Project Structure
- `backend/` – FastAPI service with project and bucket management
- `frontend/` – React application using Vite and TailwindCSS

Visit http://localhost:8000/docs for interactive API docs.
