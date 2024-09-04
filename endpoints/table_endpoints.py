import traceback
from loguru import logger
from sqlmodel import SQLModel
from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
import asyncio
from db.db import engine
from tools.table_tools import database_tables

table_router = APIRouter()

@table_router.get("/make-table", response_model=str, status_code=HTTP_200_OK, tags=['Table'])
async def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine,tables=database_tables)
        return "Successfully Created New Tables."
    except Exception as ex:
        logger.error(ex)
        logger.debug("------DEBUG---------")
        logger.debug(traceback.format_exc())
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Failed To Create New Tables.",
        )
    
if __name__ == "__main__":
    asyncio.run(create_db_and_tables())