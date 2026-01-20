import logging
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from lib.helpers import *
logger = setup_logger()
WOPR_API_URL = "https://api.wopr.tailandtraillabs.org/api/v2"

api_models = APIRouter(tags=["models"])

