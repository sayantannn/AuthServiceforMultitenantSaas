from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.orm import Session
from auth.auth import verify_password, get_password_hash, create_access_token, send_email
from db.db import get_db
from sqlalchemy.exc import SQLAlchemyError
from model.Adminmodel import User, Organization, Member, Role
from datetime import datetime, timedelta
from typing import List
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED
)

member_router = APIRouter()


@member_router.post("/signup", response_model=str, tags=["Member"])
def signup(email: str, password: str, org_name: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Email already registered")

        created_at = datetime.utcnow() + timedelta(hours=5, minutes=30)

        hashed_password = get_password_hash(password)
        new_user = User(email=email, password=hashed_password, created_at=created_at)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        new_org = Organization(name=org_name, created_at=created_at)
        db.add(new_org)
        db.commit()
        db.refresh(new_org)

        owner_role = db.query(Role).filter(Role.name == "owner", Role.org_id == new_org.id).first()
        if not owner_role:
            owner_role = Role(name="owner", org_id=new_org.id, created_at=created_at)
            db.add(owner_role)
            db.commit()
            db.refresh(owner_role)

        new_member = Member(user_id=new_user.id, org_id=new_org.id, role_id=owner_role.id, created_at=created_at)
        db.add(new_member)
        db.commit()
        db.refresh(new_member)

        send_email("Welcome to the Platform", new_user.email, f"Welcome to {org_name}! You are now the owner.")

        return JSONResponse(status_code=HTTP_201_CREATED, content={"message": "User and organization created successfully"})
    
    except HTTPException as http_err:
        raise http_err
    
    except SQLAlchemyError as e:
        logger.debug(f"Database error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating user or organization.")
    
    except Exception as e:
        logger.debug(f"Unexpected error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
    


@member_router.post("/signin",response_model=str, tags=["Member"])
def signin(email: str, password: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

        access_token = create_access_token(data={"sub": user.email})

        send_email("Login Alert", user.email, "You have successfully logged in.")

        return JSONResponse(status_code=HTTP_200_OK, content={"access_token": access_token, "token_type": "bearer"})
    
    except HTTPException as http_err:
        raise http_err
    
    except SQLAlchemyError as e:
        logger.debug(f"Database error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while signing in.")
    
    except Exception as e:
        logger.debug(f"Unexpected error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")



@member_router.post("/reset-password", response_model=str, tags=["Member"])
def reset_password(email: str, new_password: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

        user.password = get_password_hash(new_password)
        db.commit()

        send_email("Password Updated", user.email, "Your password has been successfully updated. Your password is: "+ new_password)

        return JSONResponse(status_code=HTTP_200_OK, content={"message": "Password updated successfully"})

    except HTTPException as http_err:
        raise http_err
    
    except SQLAlchemyError as e:
        logger.debug(f"Database error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the password.")
    
    except Exception as e:
        logger.debug(f"Unexpected error: {e}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
