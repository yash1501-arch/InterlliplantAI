# IntelliPlant AI

This workspace contains an initial starter implementation for the IntelliPlant AI platform based on the provided architecture documents.

## Structure

- backend/: FastAPI service with auth, document, search, and chat endpoints
- frontend/: lightweight browser UI that talks to the backend

## Run locally

1. Install backend dependencies:
   - `cd backend`
   - `pip install -r requirements.txt`
2. Start the API:
   - `python run.py`
3. Open the frontend file in a browser or serve it with a simple static server.

## Notes

The current starter version includes placeholder endpoints and a demo UI so the architecture can be expanded into the full multi-agent platform described in the design docs.
