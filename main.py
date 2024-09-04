from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import time as t
from loguru import logger
from endpoints.table_endpoints import table_router
from endpoints.admin_endpoints import admin_router
from endpoints.member_endpoints import member_router
from endpoints.stats_endpoint import stats_router
from sqlmodel import Session
from starlette.status import HTTP_200_OK
from fastapi.middleware.cors import CORSMiddleware


os.environ['TZ'] = 'Asia/Kolkata'
t.tzset()

#Logger Set-Up
logger.add("app_log/app.log", format="{time} {level} {message}", level="INFO")
logger.add("app_log/app_debug.log", format="{time} {level} {message}", level="DEBUG")
logger.add("app_log/app_error.log", format="{time} {level} {message}", level="ERROR")
logger.add("logs/logger_log.log",rotation="500 MB",format="{time:DD-MM-YYYY HH:mm:ss} | {level: <8} | {message}", backtrace=True, diagnose=True)


@asynccontextmanager
async def lifespan(app:FastAPI):
    logger = logging.getLogger("uvicorn.access")
    file_handler = logging.FileHandler("logs/access.log")
    formatter = logging.Formatter("[%(asctime)s:%(msecs)03d] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False
    yield
    
description = """
## Developer Linkedin
* [**Sayantan Guha**](https://www.linkedin.com/in/sayantanguha75/)
"""


try:
    app = FastAPI(title="Product Fusion",lifespan=lifespan, description=description)
except Exception as e:
    logger.error("Cant Start Server")
else:
    logger.success("Bankend Server Startup Successful")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    max_age = 86400
)

app.include_router(table_router)
app.include_router(admin_router)
app.include_router(member_router)
app.include_router(stats_router)


@app.get("/healthcheck_backend",status_code=HTTP_200_OK,response_class=JSONResponse,response_model=str,tags=['Main'])
async def check_health():
    return JSONResponse(status_code=HTTP_200_OK, content="Backend Server is healthy.")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)