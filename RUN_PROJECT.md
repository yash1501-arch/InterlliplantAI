# Running IntelliPlant AI

## Prerequisites
- Python 3.13+ virtual environment at `.venv`
- Node.js 20+ for frontend
- Neo4j AuraDB / Qdrant Cloud credentials in `.env`

## Start Backend
```powershell
cd backend
$env:PYTHONPATH="D:\IntelliPlant AI\backend"
..\.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8001
```
Runs on: http://localhost:8001

## Start Frontend
```powershell
cd frontend
npm run dev
```
Runs on: http://localhost:3000

## Run All Tests
```powershell
cd backend
$env:PYTHONPATH="D:\IntelliPlant AI\backend"
$env:AUTH_ENABLED="false"
..\.venv\Scripts\pytest tests/ -v --no-header
```

## Notes
- Port 8000 may be in use (TIME_WAIT); use 8001 instead
- Frontend API base defaults to localhost:8000 — update `services/api.ts` if backend is on a different port
- Auth is enforced on all routes except `/health`, `/auth/login`, `/auth/register`, `/auth/refresh`
- Default admin: `admin@intelliplant.ai` / `password123`
