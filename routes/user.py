from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import UtilisateurCreate, UtilisateurResponse
from models import Utilisateur
from database import get_db
from security import *
from jose import jwt
from starlette.responses import RedirectResponse
router = APIRouter(prefix="/users", tags=["Users"])

# Utility function to extract the current user from the JWT token
def get_current_user_from_token(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Route to register a new user
@router.post("/register", response_model=UtilisateurResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UtilisateurCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    existing_user = db.query(Utilisateur).filter(Utilisateur.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the user's password
    hashed_password = hash_password(user.mot_de_passe)
    user_data = Utilisateur(**user.dict())
    user_data.mot_de_passe = hashed_password
    user_data.date_creation=None
    # Save the user to the database
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data

# Route to log in a user
@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    # Find the user by email
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user or not verify_password(password, user.mot_de_passe):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create a JWT token
    token_data = {"user_id": user.id_utilisateur, "email": user.email, "role": user.role}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"token": token,"tokenType": "bearer"}

 


# Route to get the current user's information
@router.get("/me", response_model=UtilisateurResponse)
def get_current_user(current_user: Utilisateur = Depends(get_current_user_from_token)):
    return current_user


