from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from schemas import UtilisateurCreate, UtilisateurResponse
from models import Utilisateur
from database import *
from security import *
from jose import jwt
from starlette.responses import RedirectResponse
from urllib.parse import parse_qs
import crud
router = APIRouter(prefix="/users", tags=["Users"])




# Route to register a new user
@router.post("/register")
def register_user(
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    telephone: str = Form(...),
    mot_de_passe: str = Form(...),
    role: str = Form("visit"),  # Default value
    date_creation: str = Form("2024-12-12"),  # Default value
    db: Session = Depends(get_db)):
   # Create a new user
       # Check if the email already exists
    existing_user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create a new user in the database
    mot_de_passe=hash_password(mot_de_passe)

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
def login_user(user:Annotated[dict,Depends(get_current_user_from_token)],db: Session = Depends(get_db)):
    
    if user is None:
         raise HTTPException(status_code=401, detail="Invalid credentials")


    return {"user":user}

 
 

# Route to get the current user's information
@router.get("/me", response_model=UtilisateurResponse)
def get_current_user(current_user: Token_data = Depends(get_current_user_from_token),db:Session=Depends(get_db)):
    current_user=crud.get_user(current_user.user_id,db)
    return current_user







