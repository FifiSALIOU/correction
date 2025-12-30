from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_SECRET_KEY_VERY_IMPORTANT_TO_CHANGE")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe avec bcrypt"""
    try:
        # S'assurer que le hash est bien une chaîne
        if not hashed_password or not isinstance(hashed_password, str):
            return False
        
        # Vérifier que le hash commence par $2b$ (format bcrypt)
        if not hashed_password.startswith('$2'):
            return False
        
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        # Logger l'erreur pour le débogage (en production, utiliser un vrai logger)
        print(f"Erreur lors de la vérification du mot de passe: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    
    # Vérifier le statut de l'utilisateur (doit être actif)
    if not user.actif:
        return None
    
    # Vérifier le mot de passe
    if not verify_password(password, user.password_hash):
        return None
    
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_id=UUID(user_id))
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.get(models.User, token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


def require_role(*allowed_roles: str):
    def dependency(current_user: models.User = Depends(get_current_user)) -> models.User:
        if current_user.role is None or current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        return current_user

    return dependency


