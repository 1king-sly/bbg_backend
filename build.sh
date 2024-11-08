#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

# Generate Prisma client
prisma generate

# Fetch Prisma schema
prisma py fetch

# Start FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000
