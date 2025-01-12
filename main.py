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

@app.api_route("/", response_class=HTMLResponse,methods=["POST","GET"])
async def read_root(request: Request):
    if request.method=="POST":
        return templates.TemplateResponse("index.html", {"request": request, "title": "Accueil - AADL 2.0","connected":False})
    else:
        return templates.TemplateResponse("index.html", {"request": request, "title": "Accueil - AADL 2.0","connected":True})



@app.get("/list", response_class=HTMLResponse)
async def read_list(request: Request):
    return templates.TemplateResponse("list.html", {"request": request, "title": "Nos Propriétés"})

@app.api_route("/agent",methods=["GET","POST"], response_class=HTMLResponse)
async def read_list(request: Request):
    return templates.TemplateResponse("agent.html", {"request": request, "title": "Nos Propriétés"})


@app.get("/get_bien/{id_bien}")
async def get_bien(id_bien: int,db: Session = Depends(get_db)):
    property_details = db.query(Bien).filter(Bien.id_bien == id_bien).all()
    
    if not property_details:
        raise HTTPException(status_code=404, detail="Property not found")
    return property_details


@app.get("/bien", response_model=List[BienResponse])
def get_available_biens(request: Request,db: Session = Depends(get_db)):
    # Query to get ids of biens where their offer's state is 'dispo'
    available_biens = crud.get_all_bien(db)
    if not available_biens:
        raise HTTPException(status_code=404, detail="No available properties found")
    
    return templates.TemplateResponse("bien.html", {"request": request, "title": "biens", "biens": available_biens})


@app.get("/biens", response_model=List[BienResponse])
def get_available_biens(db: Session = Depends(get_db)):
    # Query to get ids of biens where their offer's state is 'dispo'
    available_biens = db.query(Bien).join(Offre, Bien.id_bien == Offre.id_bien).filter(Offre.etat == "actif").all()
    
    if not available_biens:
        raise HTTPException(status_code=404, detail="No available properties found")
    
    return available_biens


@app.api_route("/prop/{id_user}",methods=["GET","POST"])
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


@app.api_route("/loc/{id_user}",methods=["GET","POST"])
async def get_bien(request: Request,id_user: int, db: Session = Depends(get_db) ):
    
    Prop=db.query(Locataire).filter(Locataire.id_utilisateur == id_user).first()
    if not Prop:
        raise HTTPException(status_code=404, detail="Locataire not found")
    # Fetch the details of the property using the provided id
    location_details = db.query(Location).filter(Location.id_locataire == Prop.id_locataire).all()
    
    # If no data found, return 404
    if not location_details:
        raise HTTPException(status_code=404, detail="Property not found")
    
     # Fetch and associate the address for each Vente entry
    for vente in location_details:
        # Fetch the address associated with the Bien linked to this Vente
        bien = db.query(Bien).filter(Bien.id_bien == vente.id_bien).first()
        if bien:
            vente.adresse = bien.adresse  # Add the address to the vente object
        
    # Pass the vente_details to the read_list function along with the request
    return await read_listt(request=request, vente_details=location_details)

async def read_listt(request: Request, vente_details: List):
    # Render the HTML template and pass the vente_details as 'propbien'
    return templates.TemplateResponse("locataire.html", {"request": request, "title": "Mes Locations", "propbien": vente_details})



@app.api_route("/agent/{user_id}",methods=["GET","POST"])
async def get_bien(request: Request,user_id:int ,db: Session = Depends(get_db) ):
    
    id_agent=db.query(Agent.id_agent).filter(Agent.id_utilisateur == user_id).first()
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
    
    # Decode the token
    token_data = decode_access_token(token)
    
    # Check the role and handle redirection or fetching data
    match token_data.role:
        case "admin":
            return RedirectResponse(url="/admin")
        case "visit":
            return RedirectResponse(url="/")
        case "proprietaire":
             return RedirectResponse(url=f"/prop/{token_data.user_id}")
        case "locataire":
            return RedirectResponse(url=f"/loc/{token_data.user_id}")
        case "agent":   
            return RedirectResponse(url=f"/agent")
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
    
    return templates.TemplateResponse("liste_offres.html", {"request": request, "title": "Locations", "offers": offres})

@app.get("/sales", response_class=HTMLResponse)
def get_sale(request: Request, db: Session = Depends(get_db)):
    ventes = crud.get_sales(db)
    
    add={}
    for vente in ventes:
    # Fetch the address associated with the Bien linked to this Vente
        bien = db.query(Bien).filter(Bien.id_bien == vente.id_bien).first()
        if bien:
            add[vente.id_vente]=bien.adresse 
    
        
    return templates.TemplateResponse("liste_ventes.html", {"request": request, "title": "Locations", "propbien": ventes,"address":add})




@app.get("/transactions", response_class=HTMLResponse)
def get_rental(request: Request, db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db)
    
    return templates.TemplateResponse("transactions.html", {"request": request, "title": "Locations", "transactions": transactions})


@app.api_route("/add-sale",methods=["GET","POST"])
async def add_sale(request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":
        # Get the data from the form
        data = await request.json()
        # Create a new Vente
        
        vente = crud.add_vente(db, data)  
        # Redirect to the new Vente
        return RedirectResponse(url=f"/sales" , status_code=200)
    
    else:
        return templates.TemplateResponse("ajouter_vente.html", {"request": request, "title": "ventes"}) 



@app.get("/add-user")
async def to_sale(request: Request, db: Session = Depends(get_db)):
        return templates.TemplateResponse("ajouter_utilisateur.html", {"request": request, "title": "add user"}) 

@app.post("/add-user")
async def add_sale(
    request: Request,
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str =  Form(...),
    telephone: str = Form(...),
    mot_de_passe: str = Form(...),
    role: str =Form(...),
    db: Session = Depends(get_db)
):
    
        # Create a new user
    existing_user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create a new user
    new_user = Utilisateur(
        nom=nom,
        prenom=prenom,
        email=email,
        telephone=telephone,
        mot_de_passe=mot_de_passe,
        role=role
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while adding the user: " + str(e))

    
    
    return RedirectResponse(url=f"/users" , status_code=200)


@app.api_route("/delete-user/{user_id}",methods=["GET","POST"])
async def delete_user(request:Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a user by their ID.
    """
    # Fetch the user from the database
    user_to_delete = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == user_id).first()

    # If the user does not exist, raise a 404 error
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User  not found")
    
    try:
        # Delete the user
        db.delete(user_to_delete)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while deleting the user: " + str(e))
    
    return templates.TemplateResponse("agent.html", {"request": request, "title": "AGENT"})


@app.post("/update-user")
async def update_user(
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    telephone: str = Form(...),
    mot_de_passe: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    user_to_update = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")
    
    mot_de_passe=hash_password(mot_de_passe)

    user_to_update.nom = nom
    user_to_update.prenom = prenom
    user_to_update.email = email
    user_to_update.telephone = telephone
    user_to_update.mot_de_passe = mot_de_passe
    user_to_update.role = role
    
    try:
        db.commit()
        db.refresh(user_to_update)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the user: " + str(e))
    
    return RedirectResponse(url=f"/users" , status_code=200)



@app.get("/update-user/{id_user}")
def update_user(request:Request,id_user: int, db: Session = Depends(get_db)):
    user=db.query(Utilisateur).filter(Utilisateur.id_utilisateur == id_user).first()
    return templates.TemplateResponse("update_user.html", {"request": request, "title": "AGENT","user": user})






@app.get("/add-bien")
async def to_sale(request: Request, db: Session = Depends(get_db)):
        return templates.TemplateResponse("ajouter_bien.html", {"request": request, "title": "add user"}) 

@app.post("/add-bien")
async def add_sale(
    
    
    adresse: str = Form(...),
    superficie: int =  Form(...),
    etat: str = Form(...),
    type: str = Form(...),
    ville: str =Form(...),
    
    db: Session = Depends(get_db)
):
    
        # Create a new user
    existing_bien = db.query(Bien).filter(Bien.adresse == adresse , Bien.superficie==superficie,Bien.ville==ville).first()
    if existing_bien:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create a new user
    new_bien = Bien(
        
        adresse=adresse,
        superficie=superficie,
        etat=etat,
        type=type,
        ville=ville,
        
    )

    try:
        db.add(new_bien)
        db.commit()
        db.refresh(new_bien)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while adding the Bien: " + str(e))

    
    
    return RedirectResponse(url=f"/bien" , status_code=200)



@app.api_route("/delete-bien/{bien_id}",methods=["GET","POST"])
async def delete_user(request:Request,
    bien_id: int,
    db: Session = Depends(get_db)
):
    
    bien_to_delete = db.query(Bien).filter(Bien.id_bien == bien_id).first()

    # If the user does not exist, raise a 404 error
    if not bien_to_delete:
        raise HTTPException(status_code=404, detail="User  not found")
    if bien_to_delete.etat=="dispo":
        try:
        # Delete the user
            db.delete(bien_to_delete)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="An error occurred while deleting the user: " + str(e))
    else:
        raise HTTPException(status_code=400, detail="Bien can't be deleted")
    return templates.TemplateResponse("agent.html", {"request": request, "title": "AGENT"})






@app.post("/update-bien")
async def update_user(
     
    adresse: str = Form(...),
    superficie: int =  Form(...),
    etat: str = Form(...),
    type: str = Form(...),
    ville: str =Form(...),
    
    db: Session = Depends(get_db)
):
    bien_to_update = db.query(Bien).filter(Bien.adresse == adresse,Bien.ville==ville ).first()
    
    if not bien_to_update:
        raise HTTPException(status_code=404, detail="User not found")
    
    bien_to_update.adresse = adresse
    bien_to_update.superficie = superficie
    bien_to_update.etat = etat
    bien_to_update.type = type
    bien_to_update.ville = ville
    
    
    try:
        db.commit()
        db.refresh(bien_to_update)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the bien: " + str(e))
    
    return RedirectResponse(url=f"/bien" , status_code=200)



@app.get("/update-bien/{id_bien}")
def update_user(request:Request,id_bien: int, db: Session = Depends(get_db)):
    bien=db.query(Bien).filter(Bien.id_bien == id_bien).first()
    return templates.TemplateResponse("update_bien.html", {"request": request, "title": "AGENT","bien": bien})
















