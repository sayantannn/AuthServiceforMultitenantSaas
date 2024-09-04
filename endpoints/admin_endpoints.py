from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.orm import Session
from auth.auth import verify_password, get_password_hash, create_access_token, send_email
from db.db import get_db
from sqlalchemy.exc import SQLAlchemyError
from model.Adminmodel import User, Organization, Member, Role
from typing import List, Optional
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED
)

admin_router = APIRouter()



@admin_router.post("/invite-member", response_model=str, tags=["Admin"])
def invite_member(user_email: str, org_id: int, role_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

        new_member = Member(user_id=user.id, org_id=org_id, role_id=role_id)
        db.add(new_member)
        db.commit()
        db.refresh(new_member)

        send_email("You are invited", user_email, f"You have been invited to join the Product Fusion with role ID {role_id}.")

        return JSONResponse(status_code=HTTP_200_OK, content={"message": "Member invited successfully"})
    
    except HTTPException as http_err:
        raise http_err
    
    except SQLAlchemyError as e:
        logger.debug(f"Database error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while inviting the member.")

    except Exception as e:
        logger.debug(f"Unexpected error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")



@admin_router.delete("/delete-member/{member_id}", response_model=str, tags=["Admin"])
def delete_member(member_id: int, db: Session = Depends(get_db)):
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Member not found")

        related_roles = db.query(Role).filter(Role.id == member.role_id).all()
        related_users = db.query(User).filter(User.id == member.user_id).all()
        related_org = db.query(Organization).filter(Organization.id == member.org_id).first()
        related_members = db.query(Member).filter(Member.org_id == member.org_id).all()

        db.delete(member)

        for role in related_roles:
            db.delete(role)

        for user in related_users:
            db.delete(user)

        if related_org:
            db.delete(related_org)

        for rm in related_members:
            db.delete(rm)

        db.commit()

        return JSONResponse(status_code=HTTP_200_OK, content={"message": "Member and related data deleted successfully"})

    except HTTPException as http_err:
        raise http_err
    
    except SQLAlchemyError as e:
        logger.debug(f"Database error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while deleting the member and related data.")

    except Exception as e:
        logger.debug(f"Unexpected error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")




@admin_router.put("/update-member-role/{member_id}", response_model=str, tags=["Admin"])
def update_member_role(member_id: int, role_name: str, db: Session = Depends(get_db)):
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Member not found")

        role = db.query(Role).filter(Role.name == role_name, Role.org_id == member.org_id).first()
        if not role:
            role = Role(name=role_name, org_id=member.org_id)  # Set org_id here
            db.add(role)
            db.commit()
            db.refresh(role)

        member.role_id = role.id
        db.commit()

        return JSONResponse(status_code=HTTP_200_OK, content={"message": "Member role updated successfully"})

    except HTTPException as http_err:
        raise http_err
    
    except SQLAlchemyError as e:
        logger.debug(f"Database error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the member role.")
    
    except Exception as e:
        logger.debug(f"Unexpected error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


