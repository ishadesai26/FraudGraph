"""Main FastAPI application entrypoint for FraudGraph Phase 5."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import (
    health_router,
    dashboard_router,
    customers_router,
    transactions_router,
    fraud_rings_router,
    investigation_router,
    network_router,
    agents_router,
    simulation_router,
)
from backend.api.data_service import DataService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fraudgraph.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Pre-warms data caches and graph structures on server startup."""
    logger.info("Initializing FraudGraph in-memory data repository...")
    DataService.get_instance()
    logger.info("FraudGraph Data Service initialized successfully.")
    yield
    logger.info("Shutting down FraudGraph API server.")


app = FastAPI(
    title="FraudGraph API",
    description="AI-Powered Heterogeneous Graph Intelligence & Coordinated Fraud-Ring Detection API",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(customers_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")
app.include_router(fraud_rings_router, prefix="/api")
app.include_router(investigation_router, prefix="/api")
app.include_router(network_router, prefix="/api")
app.include_router(agents_router)
app.include_router(simulation_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Standardized JSON error handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Safely catches unhandled exceptions without leaking stack traces."""
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": 500,
            "message": "An unexpected internal server error occurred while processing the request.",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="127.0.0.1", port=8000, reload=True)
