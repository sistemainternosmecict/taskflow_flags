from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import flag_controller
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Flag Register API",
    version="1.0.0"
)

cors_origins_raw = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(
    flag_controller.router,
    prefix="/api/v1",
    tags=["Flag_controller"]
)

@app.get("/api/v1/health")
def status():
    return {"server_status":"ok"}

