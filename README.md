# odoo-hackthon

This repository now contains both the TransitOps FastAPI backend and the Vite + React frontend branch under a single workspace.

## Structure

- `backend/` - FastAPI enterprise backend
- `frontend/` - React + TypeScript + Vite frontend app

## Backend verification

The backend is verified locally with the health endpoint responding successfully at `http://127.0.0.1:8000/api/v1/health`.

## Frontend verification

The frontend branch was validated with a production build:

- `npm install`
- `npm run build`

The app builds successfully in the `frontend/` directory.

