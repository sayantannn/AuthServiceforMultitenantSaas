from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional
import smtplib
from email.mime.text import MIMEText
import os
import resend

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT Token creation
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")  # Load from environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Email Sending
resend.api_key = os.getenv("RESEND_API_KEY", "re_8v8NKwEC_9LigAx4wuCS6mn1T35iQ9r2V")

def send_email(subject: str, recipient: str, body: str):
    params = {
        "from": "Acme <onboarding@resend.dev>",
        "to": [recipient],
        "subject": subject,
        "html": body
    }

    try:
        # Send email using Resend API
        email = resend.Emails.send(params)
        print("Email sent successfully:", email)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
