from fastapi import HTTPException
from loguru import logger
from sqlmodel import create_engine, Session
from sqlalchemy.exc import PendingRollbackError
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = int(os.getenv("DB_PORT"))
database_name = os.getenv("DB_NAME")

mysql_url = f"mysql://{username}:{password}@{host}:{port}/{database_name}"

engine = create_engine(
    mysql_url,
    pool_size=20,
    max_overflow=100,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False
)


def get_db():
    db = Session(engine)
    try:
        logger.debug(f"DB session created: {db}")
        yield db
    except PendingRollbackError as pre:
        logger.error("PendingRollbackError occurred, performing rollback.")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database transaction failed. Please try again.")
    except HTTPException as ht:
        raise ht
    except Exception as e:
        logger.debug("Session can't be created.")
        logger.error(f"Unhandled error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again.")
    finally:
        logger.debug("Closing DB session.")
        db.close()
