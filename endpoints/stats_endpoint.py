from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.db import get_db
from sqlalchemy.exc import SQLAlchemyError
from model.Adminmodel import Member, Role, Organization  
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR
)

stats_router = APIRouter()


@stats_router.get("/stats/role-wise-users", response_model=str, tags=["Statistics"])
def role_wise_users(db: Session = Depends(get_db)):
    try:
        result = db.query(Role.name, func.count(Member.id)).join(Member).group_by(Role.name).all()
        data = [{"role": role, "user_count": user_count} for role, user_count in result]
        return JSONResponse(status_code=HTTP_200_OK, content={"data": data})
    except SQLAlchemyError as e:
        logger.debug(f"Database error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching role-wise user statistics.")
    except Exception as e:
        logger.debug(f"Unexpected error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


@stats_router.get("/stats/org-wise-members", response_model=str, tags=["Statistics"])
def org_wise_members(db: Session = Depends(get_db)):
    try:
        result = db.query(Organization.name, func.count(Member.id)).join(Member).group_by(Organization.name).all()
        data = [{"organization": org, "member_count": member_count} for org, member_count in result]
        return JSONResponse(status_code=HTTP_200_OK, content={"data": data})
    except SQLAlchemyError as e:
        logger.debug(f"Database error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching organization-wise member statistics.")
    except Exception as e:
        logger.debug(f"Unexpected error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")



@stats_router.get("/stats/org-role-wise-users", response_model=str, tags=["Statistics"])
def org_role_wise_users(db: Session = Depends(get_db)):
    try:
        result = db.query(Organization.name, Role.name, func.count(Member.id)).select_from(Member).join(Organization).join(Role).group_by(Organization.name, Role.name).all()
        data = [{"organization": org, "role": role, "user_count": user_count} for org, role, user_count in result]
        return JSONResponse(status_code=HTTP_200_OK, content={"data": data})
    except SQLAlchemyError as e:
        logger.debug(f"Database error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while fetching organization-role-wise user statistics.")
    except Exception as e:
        logger.debug(f"Unexpected error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")



