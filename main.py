# main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from models import Bien, Offre  # Ensure Bien and Offre are correctly imported
from database import get_db

app = FastAPI()

# Mount the static directory to serve static files (CSS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Specify the templates directory
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Accueil - AADL 2.0"})

@app.get("/list", response_class=HTMLResponse)
async def read_list(request: Request):
    return templates.TemplateResponse("list.html", {"request": request, "title": "Nos Propriétés"})

#for the bien
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from decimal import Decimal

# Enum classes for EtatEnum and TypeEnum if not already defined
class RoleEnum(str, Enum):
    agent = "agent"
    proprietaire = "proprietaire"
    locataire = "locataire"
    admin = "admin"
    visit = "visit"

class EtatEnum(str, Enum):
    loue = "loue"
    vendu = "vendu"
    dispo = "dispo"
    retard = "retard"
    payee = "payée"
    non_payee = "non_payée"
    annuler = "annuler"
    termine = "terminé"
    actif = "actif"
    expire = "expire"

class TypeEnum(str, Enum):
    villa = "villa"
    maison = "maison"
    appartement = "appartement"
    bureau = "bureau"
    location = "location"
    vente = "vente"

class ProprietaireBase(BaseModel):
    id_proprietaire: int
    # Add other fields as necessary

    class Config:
        orm_mode = True

class AgentBase(BaseModel):
    id_agent: int
    # Add other fields as necessary

    class Config:
        orm_mode = True

class BienBase(BaseModel):
    adresse: Optional[str] = None
    superficie: Optional[int] = None
    etat: Optional[EtatEnum] = None
    type: Optional[TypeEnum] = None
    ville: Optional[str] = None
    id_proprietaire: Optional[int] = None
    id_agent: Optional[int] = None

    # Including related models as nested Pydantic models
    proprietaire: Optional[ProprietaireBase] = None
    agent: Optional[AgentBase] = None

    class Config:
        orm_mode = True  # Tells Pydantic to read from ORM models

# Response model with the ID included
class BienResponse(BienBase):
    id_bien: int

    class Config:
        orm_mode = True





@app.get("/biens", response_model=List[BienResponse])
def get_available_biens(db: Session = Depends(get_db)):
    # Query to get ids of biens where their offer's state is 'dispo'
    available_biens = db.query(Bien).join(Offre, Bien.id_bien == Offre.id_bien).filter(Offre.etat == "actif").all()
    
    if not available_biens:
        raise HTTPException(status_code=404, detail="No available properties found")
    
    return available_biens



@app.get("/prop", response_class=HTMLResponse)
async def read_list(request: Request):
    return templates.TemplateResponse("prop.html", {"request": request, "title": "Mes Propriétés","propbien":[]})

