from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from schemas import UtilisateurCreate, UtilisateurResponse
from models import Utilisateur
from database import *
from security import *
from jose import jwt
from starlette.responses import RedirectResponse
from urllib.parse import parse_qs

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
@router.post("/register")
def register_user(
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    telephone: str = Form(...),
    mot_de_passe: str = Form(...),
    role: str = Form("visit"),  # Default value
    date_creation: str = Form("2021-10-10"),  # Default value
    db: Session = Depends(get_db)):
   # Create a new user
       # Check if the email already exists
    existing_user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create a new user in the database
    new_user = Utilisateur(
        nom=nom,
        prenom=prenom,
        email=email,
        telephone=telephone,
        mot_de_passe=mot_de_passe,
        role=role,
        date_creation=date_creation,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id_utilisateur}
# Route to log in a user
@router.post("/login")
def login_user(
    email: str = Form(...),
    mot_de_passe: str = Form(...),
    db: Session = Depends(get_db),
):
    
    # Get user by email
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Verify the password
    if not verify_password(mot_de_passe, user.mot_de_passe):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Successful login
    
    # Create a JWT token
    token_data = {"user_id": user.id_utilisateur,  "role": user.role}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"token": token,"tokenType": "bearer"}

 
 

# Route to get the current user's information
@router.get("/me", response_model=UtilisateurResponse)
def get_current_user(current_user: Utilisateur = Depends(get_current_user_from_token)):
    return current_user







