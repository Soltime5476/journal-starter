
from dotenv import load_dotenv

load_dotenv(override=True)

import logging

from fastapi import FastAPI

from api.routers.journal_router import router as journal_router

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)
iso_8601 = '%Y-%m-%dT%H:%M:%S'
fmt = "\033[34mCUSTOM\033[0m:   {asctime}  {name} - {message} ({filename}:{lineno})"
formatter = logging.Formatter(fmt, iso_8601, style='{')
handler.setFormatter(formatter)
logger.info("App is starting...")
app = FastAPI(title="Journal API", description="A simple journal API for tracking daily work, struggles, and intentions")
app.include_router(journal_router)
