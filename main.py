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
    return templates.TemplateResponse("agent.html", {"request": request, "title": "Agent"})

@app.api_route("/admin",methods=["GET","POST"], response_class=HTMLResponse)
async def read_list(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request, "title": "Admin"})


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
async def get_bbien(request: Request,id_user: int, db: Session = Depends(get_db) ):
    
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
    versement=db.query(RapportFinancier).filter(RapportFinancier.id_proprietaire == Prop.id_proprietaire).all()
    # Pass the vente_details to the read_list function along with the request
    return await read_listtt(request=request, vente_details=vente_details,versement=versement)

async def read_listtt(request: Request, vente_details: List,versement:List,db: Session = Depends(get_db)):
    # Render the HTML template and pass the vente_details as 'propbien'
    
    return templates.TemplateResponse("prop.html", {"request": request, "title": "Mes Propriétés", "propbien": vente_details,"versement":versement})


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
    versement=db.query(PaiementLoyer).filter(PaiementLoyer.id_locataire == Location.id_locataire).all()    
    # Pass the vente_details to the read_list function along with the request
    return await read_listt(request=request, vente_details=location_details,versement=versement)

async def read_listt(request: Request, vente_details: List,versement:List):
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
@app.get("/allusers", response_class=HTMLResponse)
def get_rental(request: Request, db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
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


@app.post("/add-sale")
async def add_sale(request: Request, 
    id_bien: str = Form(...),
    id_agent: str = Form(...),
    id_utilisateur: str = Form(...),
    date_vente: str = Form(...),
    prix: str = Form(...),
    montant_paye: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if the vente already exists
    existing_vente = db.query(Vente).filter(Vente.id_bien == id_bien).first()
    if existing_vente:
        raise HTTPException(status_code=400, detail="Vente already exists")
    else:
       existing_offre = db.query(Offre).filter(Offre.id_bien == id_bien).first() 
       existing_offre.etat="expire"
    
    existing_prop = db.query(Proprietaire).filter(Proprietaire.id_utilisateur == id_utilisateur).first()

    if not existing_prop :
         new_prop=Proprietaire(
              id_utilisateur=id_utilisateur
         )
         
         db.add(new_prop)
         db.commit()
         db.refresh(new_prop)
         
    user=db.query(Utilisateur).filter(Utilisateur.id_utilisateur==id_utilisateur).first()
    if user.role == "visit":
        user.role="proprietaire"

    db.commit()
    db.refresh(user)

    # Create a new vente
    new_vente = Vente(
        id_bien=id_bien,
        id_agent=id_agent,
        id_proprietaire=new_prop.id_proprietaire,
        date_vente=date_vente,
        prix=prix,
        montant_paye=montant_paye,
    )


    try:
        db.add(new_vente)
        db.commit()
        db.refresh(new_vente)
    except Exception as e:
        db.rollback()  # Rollback the session in case of an error
        raise HTTPException(status_code=500, detail="An error occurred while adding the sale: " + str(e))

    
    return RedirectResponse(url=f"/sales" , status_code=200)
    
@app.get("/add-sale")
def addS(request:Request):
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
    return RedirectResponse(url=f"/bien" , status_code=200)


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





@app.get("/add-offre")
async def to_sale(request: Request, db: Session = Depends(get_db)):
        return templates.TemplateResponse("ajouter_offre.html", {"request": request, "title": "add user"}) 

@app.post("/add-offre")
async def add_off(
    id_agent: int =Form(...),
    id_bien: int = Form(...),
    montant: float = Form(...),
    date_debut: str = Form(...),
    date_fin: str = Form(...),
    type: str = Form(...),
   
    db: Session = Depends(get_db)
):
    
        # Create a new user
    existing_user = db.query(Offre).filter(Offre.id_bien == id_bien,Offre.etat=="actif").first()
    if existing_user:
        raise HTTPException(status_code=400, detail="offre already exists")

    # Create a new user
    new_offre = Offre(
        id_agent=id_agent,
        id_bien=id_bien,
        montant=montant,
        date_debut=date_debut,
        date_fin=date_fin,
        type=type,
        etat="actif"
    )

    try:
        db.add(new_offre)
        db.commit()
        db.refresh(new_offre)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while adding the offre: " + str(e))

    
    
    return RedirectResponse(url=f"/offers" , status_code=200)


@app.api_route("/delete-offre/{offre_id}",methods=["GET","POST"])
async def delete_user(
    offre_id: int,
    db: Session = Depends(get_db)
):
    # Query the offer to delete
    bien_to_delete = db.query(Offre).filter(Offre.id_offre == offre_id).first()

    # If the offer does not exist, raise a 404 error
    if not bien_to_delete:
        raise HTTPException(status_code=404, detail="Offer not found")

    try:
        # Delete the offer
        db.delete(bien_to_delete)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while deleting the offer: " + str(e))

    # Redirect to the offers page after successful deletion
    return RedirectResponse(url="/offers", status_code=303)



@app.post("/update-offre")
async def update_offre(
    id_offre: int = Form(...),
    id_agent: int = Form(...),
    id_bien: int = Form(...),
    montant: float = Form(...),
    date_debut: str = Form(...),
    date_fin: str = Form(...),
    type: str = Form(...),
    db: Session = Depends(get_db)
):
    # Query the offer to update
    bien_to_update = db.query(Offre).filter(Offre.id_offre == id_offre).first()
    
    # If the offer does not exist, raise a 404 error
    if not bien_to_update:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Update the offer fields
    bien_to_update.id_agent = id_agent
    bien_to_update.id_bien = id_bien
    bien_to_update.montant = montant
    bien_to_update.date_debut = date_debut
    bien_to_update.date_fin = date_fin
    bien_to_update.type = type

    try:
        # Commit the changes to the database
        db.commit()
        db.refresh(bien_to_update)
    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the offer: " + str(e))
    
    # Redirect to the bien page after successful update
    return RedirectResponse(url="/bien", status_code=303)


@app.get("/update-offre/{id_offre}")
def update_user(request:Request,id_offre: int, db: Session = Depends(get_db)):
    bien=db.query(Offre).filter(Offre.id_offre == id_offre).first()
    return templates.TemplateResponse("update_offre.html", {"request": request, "title": "Offre","offer": bien})

######################################
@app.post("/add-trans")
async def add_trans(
    montant: int = Form(...),
    id_vente: Optional[int] = Form(None),
    id_location: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    # Create a new Transaction object
    if id_vente is None:
        new_trans = Transaction(
            montant=montant,
            date_transaction=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Use current date and time
            id_location=id_location
        )
    else:
        new_trans = Transaction(
            montant=montant,
            date_transaction=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Use current date and time
            id_vente=id_vente
        )
    
    try:
        # Add the new transaction to the database
        db.add(new_trans)
        db.commit()
        db.refresh(new_trans)

        # If id_vente is provided, fetch id_proprietaire and insert into rapport_financiere
        if id_vente is not None:
            # Fetch id_proprietaire from the vente table
            vente = db.query(Vente).filter(Vente.id_vente == id_vente).first()
            if not vente:
                raise HTTPException(status_code=404, detail="Vente not found")

            id_proprietaire = vente.id_proprietaire
            vente.montant_paye=vente.montant_paye+montant

            db.commit()
            db.refresh(vente)
            # Create a new RapportFinanciere record
            new_rapport = RapportFinancier(
                id_proprietaire=id_proprietaire,
                id_transaction=new_trans.id_transaction,
                montant=montant,
                date_rapport=datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Use current date and time
            )

            # Add the new rapport_financiere to the database
            db.add(new_rapport)
            db.commit()
            db.refresh(new_rapport)
# If id_location is provided, insert into paiement_loyer
        if id_location is not None:
            # Fetch id_locataire from the location table
            location = db.query(Location).filter(Location.id_location == id_location).first()
            if not location:
                raise HTTPException(status_code=404, detail="Location not found")

            
            location.payment = location.payment+ montant
    
            try:
        
                db.commit()
                db.refresh(location)
            except Exception as e:
        # Rollback in case of an error
                db.rollback()
                raise HTTPException(status_code=500, detail="An error occurred while updating the location: " + str(e))
    


            id_locataire = location.id_locataire
            
            # Create a new PaiementLoyer record
            new_paiement = PaiementLoyer(
                id_locataire=id_locataire,
                id_location=id_location,
                montant=montant,
                date_paiement=datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Use current date and time
            )

            # Add the new paiement_loyer to the database
            db.add(new_paiement)
            db.commit()
            db.refresh(new_paiement)
    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while adding the transaction: " + str(e))
    
    # Redirect to the transactions page after successful addition
    return RedirectResponse(url="/transactions", status_code=303)
@app.get("/add-trans")
def update_user(request:Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("ajouter_transaction.html", {"request": request, "title": "Transaction"})
    



@app.api_route("/delete-trans/{trans_id}",methods=["GET","POST"])
async def delete_transaction(
    trans_id: int,
    db: Session = Depends(get_db)
):
    # Query the database to find the transaction to delete
    bien_to_delete = db.query(Transaction).filter(Transaction.id_transaction == trans_id).first()

    # If the transaction does not exist, raise a 404 error
    if not bien_to_delete:
        raise HTTPException(status_code=404, detail="Transaction not found")

    try:


        # Delete the transaction
        db.delete(bien_to_delete)
        db.commit()
    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while deleting the transaction: " + str(e))

    # Redirect to the rentals page after successful deletion
    return RedirectResponse(url="/transactions", status_code=303)


@app.post("/update-trans")
async def update_location(
    id_transaction: int = Form(...),
    montant: int = Form(...),
    date: str = Form(...),
    id_vente: int = Form(...),
    id_location: int = Form(...),
    db: Session = Depends(get_db)
):
    # Query the database to find the transaction to update
    bien_to_update = db.query(Transaction).filter(Transaction.id_transaction == id_transaction).first()
    
    # If the transaction is not found, raise a 404 error
    if not bien_to_update:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update the transaction fields
    bien_to_update.Montant = montant
    bien_to_update.Date = date  # Assuming Date is in "YYYY-MM-DD" format
    bien_to_update.id_vente = id_vente
    bien_to_update.id_location = id_location
    try:
        # Commit the changes to the database
        db.commit()
        db.refresh(bien_to_update)
    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the offer: " + str(e))
    
    # Redirect to the bien page after successful update
    return RedirectResponse(url="/transactions", status_code=303)


@app.get("/update-trans/{id_bien}")
def update_user(request:Request,id_bien: int, db: Session = Depends(get_db)):
    bien=db.query(Transaction).filter(Transaction.id_transaction == id_bien).first()
    return templates.TemplateResponse("update_transaction.html", {"request": request, "title": "AGENT","bien": bien})

##############################################
@app.post("/add-loc")
async def add_location(
    id_bien: int = Form(...),
    date_debut: str = Form(...),
    date_fin: str = Form(...),
    prix: int = Form(...),
    id_utilisateur: int = Form(...),
    etat: str = Form(...),
    payment: int = Form(...),
    db: Session = Depends(get_db)
):
    # Query the database to check if a location already exists for the given id_bien and is not canceled
    existing_location = db.query(Location).filter(
        Location.id_bien == id_bien,
        Location.etat != "annuler"
    ).first()
    
    # If a location already exists, raise a 400 error (Bad Request)
    if existing_location:
        raise HTTPException(status_code=400, detail="A location for this property already exists and is not canceled.")
    
    locataire=db.query(Locataire).filter(Locataire.id_utilisateur==id_utilisateur).first()
    if locataire is None:
        new_locataire = Locataire(
            id_utilisateur=id_utilisateur
        )
        db.add(new_locataire)
        db.commit()
        db.refresh(new_locataire)
        user=db.query(Utilisateur).filter(Utilisateur.id_utilisateur==id_utilisateur).first()
        if user.role == "visit":
            user.role="locataire"

    
    
    else:
        new_locataire=locataire


    # Create a new Location object
    new_location = Location(
        id_bien=id_bien,
        date_debut=datetime.strptime(date_debut, "%Y-%m-%d"),  # Convert string to date
        date_fin=datetime.strptime(date_fin, "%Y-%m-%d"),  # Convert string to date
        prix=prix,
        id_locataire=new_locataire.id_locataire,
        etat=etat,
        payment=payment
    )
    
    try:
        # Add the new location to the database
        db.add(new_location)
        db.commit()
        db.refresh(new_location)
    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while adding the location: " + str(e))
    
    # Return the newly created location
    
    return RedirectResponse(url="/rentals", status_code=303)


@app.get("/add-loc")
async def to_sale(request: Request, db: Session = Depends(get_db)):
        return templates.TemplateResponse("ajouter_location.html", {"request": request, "title": "add rental"}) 

@app.api_route("/delete-loc/{loc_id}",methods=["GET","POST"])
async def delete_transaction(
    loc_id: int,
    db: Session = Depends(get_db)
):
    # Query the database to find the transaction to delete
    bien_to_delete = db.query(Location).filter(Location.id_location == loc_id).first()

    # If the transaction does not exist, raise a 404 error
    if not bien_to_delete:
        raise HTTPException(status_code=404, detail="Transaction not found")

    try:
        # Delete the transaction
        db.delete(bien_to_delete)
        db.commit()
    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while deleting the transaction: " + str(e))

    # Redirect to the rentals page after successful deletion
    return RedirectResponse(url="/rentals", status_code=303)


@app.post("/update-loc")
async def update_location(
    
    id_bien: int = Form(...),
    date_debut: str = Form(...),
    date_fin: str = Form(...),
    prix: int = Form(...),
    
    etat: str = Form(...),
    payment: int = Form(...),
    db: Session = Depends(get_db)
):
    # Query the database to find the location to update
    bien_to_update = db.query(Location).filter(Location.id_bien == id_bien and ( Location.etat!="terminé" and Location.etat!="annulé")).first()
    
    # If the location is not found, raise a 404 error
    if not bien_to_update:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Update the location fields
    bien_to_update.id_bien = id_bien
    bien_to_update.date_debut = date_debut  # Convert string to date
    bien_to_update.date_fin = date_fin  # Convert string to date
    bien_to_update.prix = prix
    
    bien_to_update.etat = etat
    bien_to_update.payment = payment
    
    try:
        # Commit the changes to the database
        db.commit()
        db.refresh(bien_to_update)
    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the location: " + str(e))
    
    # Redirect to the transactions page after successful update
    return RedirectResponse(url="/rentals", status_code=303)

@app.get("/update-loc/{id_bien}")
def update_user(request:Request,id_bien: int, db: Session = Depends(get_db)):
    bien=db.query(Location).filter(Location.id_location == id_bien).first()
    return templates.TemplateResponse("update_loc.html", {"request": request, "title": "AGENT","loc": bien})



#################################


@app.get("/add-rec")
async def to_rec(request: Request, db: Session = Depends(get_db)):
        return templates.TemplateResponse("ajouter_reclamation.html", {"request": request, "title": "add user"}) 

@app.post("/add-rec")
async def add_rec(
    
    id_location: int = Form(...),
    
    description: str = Form(...),
    
    etat: str = Form(...),
   
    db: Session = Depends(get_db)
):
    
        # Create a new user
    existing_user = db.query(DemandeMaintenance).filter(DemandeMaintenance.id_location == id_location).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="offre already exists")

    # Create a new user
    new_rec = Offre(
        id_location=id_location,
        description=description,
        etat=etat
       
    )

    try:
        db.add(new_rec)
        db.commit()
        db.refresh(new_rec)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while adding the offre: " + str(e))

    
    
    return RedirectResponse(url=f"/" , status_code=200)























