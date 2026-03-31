import asyncio
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_builder import router as builder_router
from api.routes_dashboard import router as dashboard_router
from api.routes_vault import router as vault_router
from strategy.engine import StrategyEngine

load_dotenv()
logging.basicConfig(level=logging.INFO)

frontend_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:3000,http://localhost:3001"
    ).split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    strategy = StrategyEngine()
    task = asyncio.create_task(strategy.start())
    app.state.strategy = strategy
    yield
    strategy.stop()
    task.cancel()


app = FastAPI(title="FluxVault API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vault_router, prefix="/vault")
app.include_router(builder_router, prefix="/builder")
app.include_router(dashboard_router, prefix="/dashboard")


@app.get("/health")
async def health():
    return {"status": "ok"}
