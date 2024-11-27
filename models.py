# models.py

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection URL - Replace with your MySQL credentials
DATABASE_URL = "mysql+pymysql://admin:admin@localhost:3306/gestion_immobiliere"

# Create an engine to the MySQL database
engine = create_engine(DATABASE_URL, echo=True)

# Create a base class for the database models
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, DECIMAL, Enum, ForeignKey, DateTime, TIMESTAMP
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

# Enum for 'etat' columns
class EtatEnum(str, enum.Enum):
    loue = "loue"
    vendu = "vendu"
    dispo = "dispo"
    retard = "retard"
    payee = "payée"
    non_payée = "non_payée"
    annuler = "annuler"
    termine = "terminé"
    actif = "actif"
    expire = "expire"

# Enum for 'type' columns
class TypeEnum(str, enum.Enum):
    villa = "villa"
    maison = "maison"
    appartement = "appartement"
    bureau = "bureau"
    location = "location"
    vente = "vente"

# Enum for 'role' column in 'utilisateur'
class RoleEnum(str, enum.Enum):
    agent = "agent"
    proprietaire = "proprietaire"
    locataire = "locataire"
    admin = "admin"
    visit = "visit"

# User class for 'utilisateur' table
class Utilisateur(Base):
    __tablename__ = 'utilisateur'
    
    id_utilisateur = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(40), default=None)
    prenom = Column(String(40), default=None)
    email = Column(String(60), default=None)
    mot_de_passe = Column(String(100), default=None)
    role = Column(Enum(RoleEnum), default=None)
    date_creation = Column(DateTime, default=None)
    telephone = Column(String(12), default=None)

    # Relationships
    administrateur = relationship("Administrateur", back_populates="utilisateur", uselist=False)
    agent = relationship("Agent", back_populates="utilisateur", uselist=False)
    locataire = relationship("Locataire", back_populates="utilisateur", uselist=False)
    proprietaire = relationship("Proprietaire", back_populates="utilisateur", uselist=False)

# Administrateur class for 'administrateur' table
class Administrateur(Base):
    __tablename__ = 'administrateur'
    
    id_admin = Column(Integer, primary_key=True, autoincrement=True)
    id_utilisateur = Column(Integer, ForeignKey('utilisateur.id_utilisateur'), default=None)
    
    # Relationship
    utilisateur = relationship("Utilisateur", back_populates="administrateur")

# Agent class for 'agent' table
class Agent(Base):
    __tablename__ = 'agent'
    
    id_agent = Column(Integer, primary_key=True, autoincrement=True)
    id_utilisateur = Column(Integer, ForeignKey('utilisateur.id_utilisateur'), default=None)
    
    # Relationship
    utilisateur = relationship("Utilisateur", back_populates="agent")
    offres = relationship("Offre", back_populates="agent")
    rapports = relationship("Rapport", back_populates="agent")
    biens = relationship("Bien", back_populates="agent")
    ventes = relationship('Vente', back_populates='agent')

# Locataire class for 'locataire' table
class Locataire(Base):
    __tablename__ = 'locataire'
    
    id_locataire = Column(Integer, primary_key=True, autoincrement=True)
    id_utilisateur = Column(Integer, ForeignKey('utilisateur.id_utilisateur'), default=None)
    
    # Relationship
    utilisateur = relationship("Utilisateur", back_populates="locataire")
    demandes_maintenance = relationship("DemandeMaintenance", back_populates="locataire")
    locations = relationship("Location", back_populates="locataire")
    paiements_loyer = relationship("PaiementLoyer", back_populates="locataire")

# Proprietaire class for 'proprietaire' table
class Proprietaire(Base):
    __tablename__ = 'proprietaire'
    
    id_proprietaire = Column(Integer, primary_key=True, autoincrement=True)
    id_utilisateur = Column(Integer, ForeignKey('utilisateur.id_utilisateur'), default=None)
    
    # Relationship
    utilisateur = relationship("Utilisateur", back_populates="proprietaire")
    biens = relationship("Bien", back_populates="proprietaire")
    rapports_financiers = relationship("RapportFinancier", back_populates="proprietaire")
    ventes = relationship('Vente', back_populates='proprietaire')

# Bien class for 'bien' table (already defined in previous response)
# Ensure it also includes relationships for 'proprietaire' and 'agent'
class Bien(Base):
    __tablename__ = 'bien'
    
    id_bien = Column(Integer, primary_key=True, autoincrement=True)
    adresse = Column(String(100), default=None)
    superficie = Column(Integer, default=None)
    etat = Column(Enum(EtatEnum), default=None)
    type = Column(Enum(TypeEnum), default=None)
    ville = Column(String(50), default=None)
    id_proprietaire = Column(Integer, ForeignKey('proprietaire.id_proprietaire'), default=None)
    id_agent = Column(Integer, ForeignKey('agent.id_agent'), default=None)
    
    # Relationships
    proprietaire = relationship("Proprietaire", back_populates="biens")
    agent = relationship("Agent", back_populates="biens")
    location = relationship('Location', back_populates='bien')
    offres = relationship('Offre', back_populates='bien')
    ventes = relationship('Vente', back_populates='bien')

# Location class for 'location' table
class Location(Base):
    __tablename__ = 'location'
    
    id_location = Column(Integer, primary_key=True, autoincrement=True)
    id_bien = Column(Integer, ForeignKey('bien.id_bien'), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    prix = Column(Integer, nullable=False)
    id_locataire = Column(Integer, ForeignKey('locataire.id_locataire'), nullable=False)
    etat = Column(Enum(EtatEnum), default="non_payée", nullable=False)
    payment = Column(Integer, default=0)
    
    # Relationships
    bien = relationship("Bien", back_populates="location")
    locataire = relationship("Locataire", back_populates="locations")
    paiements_loyer = relationship("PaiementLoyer", back_populates="location")
    demandes_maintenance = relationship('DemandeMaintenance', back_populates='location')
    transactions = relationship('Transaction', back_populates='location')

# Offre class for 'offre' table
class Offre(Base):
    __tablename__ = 'offre'
    
    id_offre = Column(Integer, primary_key=True, autoincrement=True)
    id_agent = Column(Integer, ForeignKey('agent.id_agent'), default=None)
    id_bien = Column(Integer, ForeignKey('bien.id_bien'), default=None)
    montant = Column(DECIMAL(10, 2), default=None)
    date_debut = Column(Date, default=None)
    date_fin = Column(Date, default=None)
    type = Column(Enum(TypeEnum), nullable=False)
    etat = Column(Enum(EtatEnum), default="actif", nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="offres")
    bien = relationship("Bien", back_populates="offres")

# PaiementLoyer class for 'paiement_loyer' table
class PaiementLoyer(Base):
    __tablename__ = 'paiement_loyer'
    
    id_paiement = Column(Integer, primary_key=True, autoincrement=True)
    id_locataire = Column(Integer, ForeignKey('locataire.id_locataire'), default=None)
    id_location = Column(Integer, ForeignKey('location.id_location'), default=None)
    montant = Column(DECIMAL(10, 2), default=None)
    date_paiement = Column(Date, default=None)
    
    # Relationships
    locataire = relationship("Locataire", back_populates="paiements_loyer")
    location = relationship("Location", back_populates="paiements_loyer")

# DemandeMaintenance class for 'demande_maintenance' table
class DemandeMaintenance(Base):
    __tablename__ = 'demande_maintenance'
    
    id_demande = Column(Integer, primary_key=True, autoincrement=True)
    id_locataire = Column(Integer, ForeignKey('locataire.id_locataire'), default=None)
    id_location = Column(Integer, ForeignKey('location.id_location'), default=None)
    description = Column(Text, default=None)
    date_demande = Column(Date, default=None)
    etat = Column(String(20), default=None)
    
    # Relationships
    locataire = relationship("Locataire", back_populates="demandes_maintenance")
    location = relationship("Location", back_populates="demandes_maintenance")

# Rapport class for 'rapport' table
class Rapport(Base):
    __tablename__ = 'rapport'
    
    id_rapport = Column(Integer, primary_key=True, autoincrement=True)
    id_agent = Column(Integer, ForeignKey('agent.id_agent'), default=None)
    description = Column(Text, default=None)
    date_creation = Column(Date, default=None)
    
    # Relationships
    agent = relationship("Agent", back_populates="rapports")

# RapportFinancier class for 'rapport_financiere' table
class RapportFinancier(Base):
    __tablename__ = 'rapport_financiere'
    
    id_rapport_financier = Column(Integer, primary_key=True, autoincrement=True)
    id_proprietaire = Column(Integer, ForeignKey('proprietaire.id_proprietaire'), default=None)
    id_transaction = Column(Integer, ForeignKey('transaction.id_transaction'), default=None)
    montant = Column(DECIMAL(10, 2), default=None)
    date_rapport = Column(Date, default=None)
    
    # Relationships
    proprietaire = relationship("Proprietaire", back_populates="rapports_financiers")
    transaction = relationship("Transaction", back_populates="rapports_financiers")

# Transaction class for 'transaction' table
class Transaction(Base):
    __tablename__ = 'transaction'
    
    id_transaction = Column(Integer, primary_key=True, autoincrement=True)
    montant = Column(DECIMAL(10, 2), default=None)
    date_transaction = Column(TIMESTAMP, default=None)
    id_vente = Column(Integer, ForeignKey('vente.id_vente'), default=None)
    id_location = Column(Integer, ForeignKey('location.id_location'), default=None)
    
    # Relationships
    vente = relationship("Vente", back_populates="transactions")
    location = relationship("Location", back_populates="transactions")
    rapports_financiers = relationship("RapportFinancier", back_populates="transaction")

# Vente class for 'vente' table
class Vente(Base):
    __tablename__ = 'vente'
    
    id_vente = Column(Integer, primary_key=True, autoincrement=True)
    id_bien = Column(Integer, ForeignKey('bien.id_bien'), default=None)
    id_agent = Column(Integer, ForeignKey('agent.id_agent'), default=None)
    id_proprietaire = Column(Integer, ForeignKey('proprietaire.id_proprietaire'), default=None)
    date_vente = Column(Date, default=None)
    montant_paye = Column(DECIMAL(10, 2), default=None)
    etat = Column(Enum(EtatEnum), default="non_payée", nullable=False)
    prix = Column(DECIMAL(10, 2), default=None)
    
    # Relationships
    agent = relationship("Agent", back_populates="ventes")
    proprietaire = relationship("Proprietaire", back_populates="ventes")
    bien = relationship("Bien", back_populates="ventes")
    transactions = relationship("Transaction", back_populates="vente")


# Create the session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)





