# WaferVision AI

WaferVision AI is a wafer-defect inspection system built around a Python inference backend and a React dashboard. It classifies wafer map defects with a CNN ensemble, generates defect heatmaps, stores inspection history in MongoDB, optionally uploads artifacts to AWS S3, and produces Gemini-based operator insights for both the current wafer and recent manufacturing trends.

## Overview

The project is split into two main parts:

- `backend/`: FastAPI API, Streamlit app, model inference, MongoDB, AWS, and Gemini integration
- `frontend/`: React dashboard built with Vite

The current UI exposes four main pages:

- `Overview`: KPI dashboard, trends, severity, and recent inspections
- `Analyze`: image upload, prediction, heatmap, current-wafer insight, and manufacturing-process insight
- `History`: historical inspection records from MongoDB
- `Analytics`: defect distribution and process pattern monitoring

## Architecture

### Backend

The backend contains:

- `backend/api/main.py`: FastAPI endpoints used by the React frontend
- `backend/app/`: Streamlit dashboard entry point and pages
- `backend/services/inference_service.py`: CNN ensemble inference and heatmap generation
- `backend/services/gemini_service.py`: current-wafer and manufacturing-process insight generation
- `backend/services/mongo_service.py`: MongoDB persistence and history access
- `backend/services/aws_service.py`: optional S3 uploads for images and heatmaps
- `backend/database/mongodb.py`: MongoDB client/collection setup
- `backend/database/schema.py`: helper for stored wafer analysis documents
- `backend/models/`: trained CNN and YOLO model assets used by the backend

### Frontend

The frontend contains:

- `frontend/src/App.jsx`: application shell and routing
- `frontend/src/pages/OverviewPage.jsx`
- `frontend/src/pages/AnalyzePage.jsx`
- `frontend/src/pages/HistoryPage.jsx`
- `frontend/src/pages/AnalyticsPage.jsx`

## Core Features

- CNN ensemble prediction using ResNet18, MobileNetV2, and EfficientNetB0
- Heatmap generation for localized visual explanation
- MongoDB-backed inspection history
- Gemini insights:
	- current wafer insight
	- manufacturing process insight based on the last 30 to 40 wafers
- Optional AWS S3 storage for uploaded wafer images and generated heatmaps
- FastAPI endpoints for frontend integration
- Streamlit dashboard retained alongside the React frontend

## Project Structure

```text
Wafer Map Pattern System/
├─ backend/
│  ├─ api/
│  ├─ app/
│  ├─ database/
│  ├─ models/
│  ├─ services/
│  ├─ main.py
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  ├─ package.json
│  └─ vite.config.js
├─ requirements.txt
└─ test_pipeline.py
```

## Prerequisites

- Python 3.11+ recommended
- Node.js 18+ recommended
- MongoDB database
- Optional: AWS S3 bucket and Gemini API key

## Python Dependencies

The root `requirements.txt` currently includes:

- `fastapi`
- `uvicorn[standard]`
- `streamlit`
- `torch`
- `torchvision`
- `numpy<2`
- `pillow`
- `ultralytics`
- `pymongo`
- `boto3`
- `google-genai`
- `python-multipart`
- `python-dotenv`

## Environment Variables

Create a file at `backend/.env` for backend configuration.

Expected backend variables:

```env
MONGO_URI=
DATABASE_NAME=
COLLECTION_NAME=

GEMINI_API_KEY=

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_BUCKET_NAME=
```

Create a file at `frontend/.env` for the frontend.

Expected frontend variables:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Installation

### Backend

From the project root:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

From the `frontend/` folder:

```powershell
npm install
```

## Running the Project

### Run the FastAPI backend

From the project root:

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### Run the React frontend

From the `frontend/` folder:

```powershell
npm run dev
```

### Run the Streamlit dashboard

From the project root:

```powershell
streamlit run backend/app/main.py
```

## API Endpoints

The FastAPI service currently exposes:

- `GET /health`
- `GET /overview`
- `GET /analytics`
- `GET /history`
- `POST /analyze`

### `POST /analyze`

Accepts an uploaded wafer image and returns:

- `prediction`
- `heatmap_base64`
- `image_url`
- `heatmap_url`
- `recent_similar_wafers`
- `current_wafer_insight`
- `process_insight`
- `insight` (backward-compatible alias for current wafer insight)

## Stored Inspection Data

Each saved analysis document includes:

- timestamp
- uploaded image URL
- heatmap URL
- prediction
- detections
- current wafer insight
- manufacturing process insight
- human feedback fields for review/verification

## Notes

- The React app is the primary modern dashboard.
- The Streamlit app still exists for quick internal inspection and debugging workflows.
- `Yield Rate` on the current Overview page is a classifier-based proxy, not true fab yield.
- YOLO detections are still available in backend results, but are currently de-emphasized in the UI.

## Testing

There is a simple pipeline script at `test_pipeline.py` that can be used to validate inference wiring.

Example:

```powershell
python test_pipeline.py
```

## Recommended Workflow

1. Start MongoDB and ensure backend environment variables are set.
2. Start the backend API.
3. Start the frontend.
4. Upload a wafer image from the Analyze page.
5. Review prediction, heatmap, current wafer insight, and manufacturing process insight.
6. Use Overview, History, and Analytics to inspect recent behavior across stored records.

## Repository Notes

- Backend source of truth: `backend/`
- Frontend source of truth: `frontend/`
- Legacy top-level Streamlit files were removed so `backend/app/` is the only active Streamlit app path.
