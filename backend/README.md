# Backend

This folder contains the Python backend for the project.

Backend structure now includes:

- `api/` FastAPI endpoints
- `app/` Streamlit dashboard
- `database/` MongoDB connection code
- `models/` trained model files
- `services/` inference, AWS, Gemini, and Mongo helpers
- `utils/` shared utilities

## Run the API

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

## Run the Streamlit app

```powershell
streamlit run backend/app/main.py
```

The FastAPI implementation lives in `backend/api/main.py` and uses the services within this same backend folder.
