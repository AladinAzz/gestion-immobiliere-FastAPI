from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from schemas import *
from models import *
from database import *
from security import *
from jose import jwt



db = APIRouter(prefix="/db", tags=["db"])

def get_bien(id_bien: int,db: Session = Depends(get_db)):
        property_details = db.query(Bien).filter(Bien.id_bien == id_bien).all()
    
        if not property_details:
            raise HTTPException(status_code=404, detail="Property not found")
        return property_details

def get_user(id_utilisateur: int):
        utilisateur = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == id_utilisateur).first()
        if not utilisateur:
            raise HTTPException(status_code=404, detail="user not found")
        return utilisateur

def get_agent(id_utilisateur: int):
      agent = db.query(Agent).filter(Agent.id_utilisateur == id_utilisateur).first()
      if not agent:
            raise HTTPException(status_code=404, detail="agent not found")
      return agent

def get_agent_by_id(id_agent: int):
        user = db.query(Utilisateur).join(Utilisateur,Agent.id_utilisateur==Utilisateur.id_utilisateur).filter(Agent.id_agent == id_agent).first()
        if not user:
            raise HTTPException(status_code=404, detail="user not found")
        return user




db.get("/get-users")
def get_users(db: Session = Depends(get_db)):
        users = db.query(Utilisateur).filter(Utilisateur.role!="admin" and Utilisateur.role!="agent").all()
        if not users:
            raise HTTPException(status_code=404, detail="users not found")
        return users

db.get("/get-offers")
def get_offers(db: Session = Depends(get_db)):
      offers = db.query(Offre).all()
      if not offers:
            raise HTTPException(status_code=404, detail="offers not found")
      return offers

db.get("/get-rentals")
def get_rentals(db: Session = Depends(get_db)):
      rentals = db.query(Location).all()
      if not rentals:
            raise HTTPException(status_code=404, detail="rentals not found")
      return rentals


db.get("/get-rentals-by-agent/{agent_id}")
def get_rentals_by_agent(agent_id: int, db: Session = Depends(get_db)):
      rentals = db.query(Location).filter(Location.id_agent == agent_id).all()
      if not rentals:
            raise HTTPException(status_code=404, detail="rentals not found")
      return rentals

db.get("/get-sales")
def get_sales(db: Session = Depends(get_db)):
      sales = db.query(Vente).all()
      if not sales:
            raise HTTPException(status_code=404, detail="sales not found")
      return sales


db.get("/get-sales-by-agent")
def get_sales_by_agent(agent_id: int, db: Session = Depends(get_db)):
      sales = db.query(Vente).filter(Vente.id_agent == agent_id).all()
      if not sales:
            raise HTTPException(status_code=404, detail="sales not found")
      return sales


db.get("/get-transactions")
def get_transactions(db: Session = Depends(get_db)):
      transactions = db.query(Transaction).all()
      if not transactions:
            raise HTTPException(status_code=404, detail="transactions not found")
      return transactions

db.get("/get-transaction-by-agent")
def get_transaction_by_agent(agent_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).join(Vente, Vente.id_vente == Transaction.id_vente).filter(Transaction.id_agent == agent_id).union(
        db.query(Transaction).join(Location, Location.id_location == Transaction.id_location).filter(Transaction.id_agent == agent_id)
        ).all()
    if not transactions:
          raise HTTPException(status_code=404, detail="transactions not found")
    return transactions


