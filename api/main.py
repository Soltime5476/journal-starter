
import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from api.routers.journal_router import router as journal_router

load_dotenv(override=True)

iso_8601 = '%Y-%m-%dT%H:%M:%S'
fmt = "\033[34mCUSTOM\033[0m:   {asctime}  {name} - {message} ({filename}:{lineno})"
logging.basicConfig(level=logging.INFO, datefmt=iso_8601, format=fmt, style="{")

logging.info("App is starting...")
app = FastAPI(title="Journal API", description="A simple journal API for tracking daily work, struggles, and intentions")
app.include_router(journal_router)
