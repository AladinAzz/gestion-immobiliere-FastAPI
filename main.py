# main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from models import *  # Ensure Bien and Offre are correctly imported
from database import get_db
from schemas import *  
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


@app.get("/get_bien/{id_bien}")
async def get_bien(id_bien: int,db: Session = Depends(get_db)):
    property_details = db.query(Bien).filter(Bien.id_bien == id_bien).all()
    
    if not property_details:
        raise HTTPException(status_code=404, detail="Property not found")
    return property_details


@app.get("/biens", response_model=List[BienResponse])
def get_available_biens(db: Session = Depends(get_db)):
    # Query to get ids of biens where their offer's state is 'dispo'
    available_biens = db.query(Bien).join(Offre, Bien.id_bien == Offre.id_bien).filter(Offre.etat == "actif").all()
    
    if not available_biens:
        raise HTTPException(status_code=404, detail="No available properties found")
    
    return available_biens



@app.get("/prop/{id_prop}")
async def get_bien(request: Request,id_prop: int, db: Session = Depends(get_db) ):
    # Fetch the details of the property using the provided id
    vente_details = db.query(Vente).filter(Vente.id_proprietaire == id_prop).all()
    
    # If no data found, return 404
    if not vente_details:
        raise HTTPException(status_code=404, detail="Property not found")
    
     # Fetch and associate the address for each Vente entry
    for vente in vente_details:
        # Fetch the address associated with the Bien linked to this Vente
        bien = db.query(Bien).filter(Bien.id_bien == vente.id_bien).first()
        if bien:
            vente.adresse = bien.adresse  # Add the address to the vente object
    
    # Pass the vente_details to the read_list function along with the request
    return await read_list(request, vente_details)

async def read_list(request: Request, vente_details: List[VenteResponse]):
    # Render the HTML template and pass the vente_details as 'propbien'
    return templates.TemplateResponse("prop.html", {"request": request, "title": "Mes Propriétés", "propbien": vente_details})







