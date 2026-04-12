import logging

from dotenv import load_dotenv

load_dotenv(override=True)
from fastapi import FastAPI  # noqa: E402

from api.routers.journal_router import router as journal_router  # noqa: E402

iso_8601 = "%Y-%m-%dT%H:%M:%S"
fmt = "\033[34mCUSTOM\033[0m:   {asctime}  {name} - {message} ({filename}:{lineno})"
logging.basicConfig(level=logging.INFO, datefmt=iso_8601, format=fmt, style="{")

logging.info("App is starting...")
app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
)
app.include_router(journal_router)
