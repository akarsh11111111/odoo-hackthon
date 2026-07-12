# TransitOps Backend

Phase 1 establishes the production backend scaffold for TransitOps:

- FastAPI application factory
- MongoDB connection via Motor and Beanie
- Centralized config, logging, and exception handling
- Standard response envelope
- Request context middleware
- Health endpoint for deployment verification

Business modules such as authentication, vehicles, drivers, trips, maintenance, fuel, expenses, and reporting will be added after approval.

## Local run

1. Copy `.env.example` to `.env` and update values.
2. Install dependencies with `pip install -e .[dev]`.
3. Start the app with `uvicorn src.main:app --reload` from the `backend/` folder.
