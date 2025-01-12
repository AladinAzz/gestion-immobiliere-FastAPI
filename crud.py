#crud.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from schemas import *
from models import *
from database import *
from security import *
from jose import jwt



db = APIRouter(prefix="/db", tags=["db"])
@db.get("/")
def get_db_status():
    return {"status": "Database is healthy"}




def get_all_bien(db: Session = Depends(get_db)):
        property_details = db.query(Bien).all()
    
        
        return property_details



def get_bien(id_bien: int,db: Session = Depends(get_db)):
        property_details = db.query(Bien).filter(Bien.id_bien == id_bien).all()
    
        
        return property_details


@db.get("/get-user",response_model=UtilisateurResponse)
def get_user(id_utilisateur: int, db: Session = Depends(get_db))->UtilisateurResponse:
    utilisateur = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == id_utilisateur).first()
    
    return utilisateur




def get_agent(id_utilisateur: int,db: Session = Depends(get_db)):
      agent = db.query(Agent).filter(Agent.id_utilisateur == id_utilisateur).first()
      
      return agent

def get_agent_by_id(id_agent: int,db: Session = Depends(get_db)):
        user = db.query(Utilisateur).join(Utilisateur,Agent.id_utilisateur==Utilisateur.id_utilisateur).filter(Agent.id_agent == id_agent).first()
        
        return user








@db.get("/get-users")
def get_users(db: Session = Depends(get_db)):
        users = db.query(Utilisateur).filter(Utilisateur.role!="admin" and Utilisateur.role!="agent").all()
        
        return users




@db.get("/get-offers")
def get_offers(db: Session = Depends(get_db)):
      offers = db.query(Offre).all()
      return offers

@db.get("/get-rentals")
def get_rentals(db: Session = Depends(get_db)):
      rentals = db.query(Location).all()
     
      return rentals


@db.get("/get-rentals-by-agent/{agent_id}", response_model=List[LocationResponse])
def get_rentals_by_agent(agent_id: int, db: Session = Depends(get_db)):
    # Fetch all 'Bien' entries for the agent
    biens = db.query(Bien).filter(Bien.id_agent == agent_id).all()
    if not biens:
        raise HTTPException(status_code=404, detail="Bien not found")

    # Fetch all rentals for the agent's properties
    rentals = []
    for bien in biens:
        locations = db.query(Location).filter(Location.id_bien == bien.id_bien).all()
        if locations:
            rentals.extend(locations)
    
    if not rentals:
        raise HTTPException(status_code=404, detail="Rentals not found")
    
    # Optionally convert to LocationResponse schema
    return rentals
@db.get("/get-sales")
def get_sales(db: Session = Depends(get_db)):
      sales = db.query(Vente).all()

      return sales


@db.get("/get-sales-by-agent")
def get_sales_by_agent(agent_id: int, db: Session = Depends(get_db)):
      sales = db.query(Vente).filter(Vente.id_agent == agent_id).all()
      return sales


@db.get("/get-transactions")
def get_transactions(db: Session = Depends(get_db)):
      transactions = db.query(Transaction).all()
      
      return transactions

@db.get("/get-transaction-by-agent")
def get_transaction_by_agent(agent_id: int, db: Session = Depends(get_db)):
      transactions = db.query(Transaction).join(Vente, Vente.id_vente == Transaction.id_vente).filter(Vente.id_agent == agent_id).all()
      biens = db.query(Bien).filter(Bien.id_agent == agent_id).all()
      if not biens:
            raise HTTPException(status_code=404, detail="Bien not found")  
      rentals = []
      for bien in biens:
        locations = db.query(Location).filter(Location.id_bien == bien.id_bien).all()
        if locations:
            rentals.extend(locations)
      for rent in rentals:
            transactions.extend(db.query(Transaction).join(Location, Location.id_location == Transaction.id_location).filter(Location.id_location == rent.id_location).all())
      if not transactions:
          raise HTTPException(status_code=404, detail="transactions not found")
      return transactions

@db.post("/add_sale")
def add_vente(
    id_bien: str = Form(...),
    id_agent: str = Form(...),
    id_proprietaire: str = Form(...),
    date_vente: str = Form(...),
    prix: str = Form(...),
    montant_paye: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if the vente already exists
    existing_vente = db.query(Vente).filter(Vente.id_bien == id_bien).first()
    if existing_vente:
        raise HTTPException(status_code=400, detail="Vente already exists")

    # Create a new vente
    new_vente = Vente(
        id_bien=id_bien,
        id_agent=id_agent,
        id_proprietaire=id_proprietaire,
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

    return {"message": "Vente registered successfully", "vente_id": new_vente.id_vente}


@db.post("/add_transaction")
def add_transaction(
    id_vente: str = Form(...),
    id_location: str = Form(...),
    montant: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if the vente already exists
    if id_vente != "":
            existing_vente = db.query(Vente).filter(Vente.id_vente == id_vente).first()
            if not existing_vente:
                  raise HTTPException(status_code=400, detail="Vente doesn't exists")
    else:
         existing_location = db.query(Location).filter(Location.id_location == id_location).first()
         if not existing_location:
            raise HTTPException(status_code=400, detail="location doesn't exists")  
    # Create a new vente
    new_trans = Transaction(
        id_vente=id_vente,
        id_location=id_location,
        montant=montant
    )


    try:
        db.add(new_trans)
        db.commit()
        db.refresh(new_trans)
    except Exception as e:
        db.rollback()  # Rollback the session in case of an error
        raise HTTPException(status_code=500, detail="An error occurred while adding the sale: " + str(e))

    return {"message": "Vente registered successfully", "vente_id": new_trans.id_transaction}



@db.post("/add_user")
def add_user(
    
    nom: str,
    prenom: str,
    email: str,
    telephone: str,
    mot_de_passe: str,
    role: str,
    db#: Session = Depends(get_db)
):
    # Check if the user already exists
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

    return new_user




