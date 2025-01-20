#!/bin/bash

# Run the migrations
alembic upgrade head

if [[ "$DEBUG" == "true" ]]; then
    pip install debugpy
    python3 -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
fi

# Run the API
uvicorn app.main:app --host 0.0.0.0 --port 8000