# main.py
from fastapi import FastAPI, Request, Depends, HTTPException,Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import crud
from models import *  
from database import get_db
from schemas import *  
from routes import user
from security import *
from starlette.responses import RedirectResponse
import logging
from fastapi.responses import JSONResponse
import httpx
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(user.router)
app.include_router(crud.db)
app.include_router(auth)
# Mount the static directory to serve static files (CSS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Specify the templates directory
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Accueil - AADL 2.0","connected":False})

@app.post("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Accueil - AADL 2.0","connected":True})



@app.get("/list", response_class=HTMLResponse)
async def read_list(request: Request):
    return templates.TemplateResponse("list.html", {"request": request, "title": "Nos Propriétés"})

@app.get("/agent", response_class=HTMLResponse)
async def read_list(request: Request):
    return templates.TemplateResponse("agent.html", {"request": request, "title": "Nos Propriétés"})


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


@app.get("/prop/{id_user}")
async def get_bien(request: Request,id_user: int, db: Session = Depends(get_db) ):
    
    Prop=db.query(Proprietaire).filter(Proprietaire.id_utilisateur == id_user).first()
    if not Prop:
        raise HTTPException(status_code=404, detail="Proprietaire not found")
    # Fetch the details of the property using the provided id
    vente_details = db.query(Vente).filter(Vente.id_proprietaire == Prop.id_proprietaire).all()
    
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
    return await read_listt(request=request, vente_details=vente_details)

async def read_listt(request: Request, vente_details: List):
    # Render the HTML template and pass the vente_details as 'propbien'
    return templates.TemplateResponse("prop.html", {"request": request, "title": "Mes Propriétés", "propbien": vente_details})

@app.get("/agent/{id_user}")
async def get_bien(request: Request,id_user: int, db: Session = Depends(get_db) ):
    
    id_agent=db.query(Agent.id_agent).filter(Agent.id_utilisateur == id_user).first()
    # Fetch the details of the property using the provided id
    vente_details = db.query(Vente).filter(Vente.id_agent == id_agent).all()
    
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
    return await read_list2(request, vente_details)

async def read_list2(request: Request, vente_details: List[VenteResponse]):
    # Render the HTML template and pass the vente_details as 'propbien'
    return templates.TemplateResponse("agent.html", {"request": request, "title": "Agent Space", "propbien": vente_details})





@app.get("/login", response_class=HTMLResponse)
async def read_list(request: Request):
    return templates.TemplateResponse("log.html", {"request": request, "title": "Log In"}) 



logger = logging.getLogger(__name__)


@app.post("/redirect")
async def redirect(request: Request, token: str = Form(...)):
    logger.info(f"Received request with token: {token}")
    
    # Decode the token
    token_data = decode_access_token(token)
    
    # Get the base URL from the request
    base_url = f"http://{request.client.host}:{request.client.port}"  # Adjust for https if needed
    
    # Check the role and handle redirection or fetching data
    match token_data.role:
        case "admin":
            return RedirectResponse(url="/admin")
        case "visit":
            return RedirectResponse(url="/")
        case "proprietaire":
            link=f"{base_url}/prop/{token_data.user_id}"
            async with httpx.AsyncClient() as client:
                # Construct the full URL for the GET request
                response = await client.get(link)
                
                # Log the response status code and content
                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response content: {response.text}")
                
                # Check if the response is successful
                if response.status_code == 200:
                    return JSONResponse(content=response.json(), status_code=response.status_code)
                else:
                    raise HTTPException(status_code=response.status_code, detail="Error fetching property data")
        case "locataire":
            return RedirectResponse(url=f"/loc/{token_data.user_id}")
        case "agent":   
            return RedirectResponse(url=f"/agent/{token_data.user_id}")
        case _:
            raise HTTPException(status_code=400, detail="Unknown role")
        


@app.get("/rentals", response_class=HTMLResponse)
def get_rental(request: Request, db: Session = Depends(get_db)):
    locations = crud.get_rentals(db)
    return templates.TemplateResponse("liste_locations.html", {"request": request, "title": "Locations", "locations": locations})

@app.get("/users", response_class=HTMLResponse)
def get_rental(request: Request, db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return templates.TemplateResponse("acces_utilisateurs.html", {"request": request, "title": "Users", "users": users})



@app.get("/offers", response_class=HTMLResponse)
def get_rental(request: Request, db: Session = Depends(get_db)):
    offres = crud.get_offers(db)
    if not offres:
        raise HTTPException(status_code=404, detail="offres not found")
    return templates.TemplateResponse("liste_offres.html", {"request": request, "title": "Locations", "offers": offres})

@app.get("/sales", response_class=HTMLResponse)
def get_sale(request: Request, db: Session = Depends(get_db)):
    ventes = crud.get_sales(db)
    if not ventes:
        raise HTTPException(status_code=404, detail="vente not found")
    for vente in ventes:
        # Fetch the address associated with the Bien linked to this Vente
        bien = db.query(Bien).filter(Bien.id_bien == vente.id_bien).first()
        if bien:
            vente.adresse = bien.adresse
    
        
    return templates.TemplateResponse("liste_ventes.html", {"request": request, "title": "Locations", "propbien": ventes})

