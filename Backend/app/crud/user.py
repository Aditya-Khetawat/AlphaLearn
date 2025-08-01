from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.models import User
from app.schemas.schemas import UserCreate, UserUpdate


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by ID
    """
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email
    """
    return db.query(User).filter(User.email == email).first()


def get_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get a user by username
    """
    return db.query(User).filter(User.username == username).first()


def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[User]:
    """
    Get multiple users with pagination
    """
    return db.query(User).offset(skip).limit(limit).all()


def create(db: Session, obj_in: UserCreate) -> User:
    """
    Create a new user
    """
    db_obj = User(
        email=obj_in.email,
        username=obj_in.username,
        full_name=obj_in.full_name,
        hashed_password=get_password_hash(obj_in.password),
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, 
    db_obj: User, 
    obj_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    """
    Update a user
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field in update_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def authenticate(
    db: Session, 
    email: str, 
    password: str
) -> Optional[User]:
    """
    Authenticate a user
    """
    user = get_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def is_active(user: User) -> bool:
    """
    Check if user is active
    """
    return user.is_active


def is_admin(user: User) -> bool:
    """
    Check if user is admin
    """
    return user.is_admin
