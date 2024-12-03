#schemas.py
from pydantic import BaseModel, Field, EmailStr, condecimal
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# Enum for EtatEnum
class EtatEnum(str, Enum):
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

# Enum for TypeEnum
class TypeEnum(str, Enum):
    villa = "villa"
    maison = "maison"
    appartement = "appartement"
    bureau = "bureau"
    location = "location"
    vente = "vente"

# Enum for RoleEnum
class RoleEnum(str, Enum):
    agent = "agent"
    proprietaire = "proprietaire"
    locataire = "locataire"
    admin = "admin"
    visit = "visit"
    

### SCHEMAS ###
# Utilisateur Schema
class UtilisateurBase(BaseModel):
    nom: Optional[str]
    prenom: Optional[str]
    email: Optional[EmailStr]
    telephone: Optional[str]
    role: Optional[RoleEnum]
    date_creation: Optional[datetime]

    class Config:
        orm_mode = True

class UtilisateurCreate(BaseModel):
    nom: str
    prenom: str
    email: str
    telephone: str
    mot_de_passe: str
    role: Optional[str] = "visit"
    date_creation: Optional[str] 




class UtilisateurResponse(UtilisateurBase):
    id_utilisateur: int


# Administrateur Schema
class AdministrateurBase(BaseModel):
    id_utilisateur: int

    class Config:
        orm_mode = True


class AdministrateurResponse(AdministrateurBase):
    id_admin: int


# Agent Schema
class AgentBase(BaseModel):
    id_utilisateur: int

    class Config:
        orm_mode = True


class AgentResponse(AgentBase):
    id_agent: int


# Locataire Schema
class LocataireBase(BaseModel):
    id_utilisateur: int

    class Config:
        orm_mode = True


class LocataireResponse(LocataireBase):
    id_locataire: int


# Proprietaire Schema
class ProprietaireBase(BaseModel):
    id_utilisateur: int

    class Config:
        orm_mode = True


class ProprietaireResponse(ProprietaireBase):
    id_proprietaire: int


# Bien Schema
class BienBase(BaseModel):
    adresse: Optional[str]
    superficie: Optional[int]
    etat: Optional[EtatEnum]
    type: Optional[TypeEnum]
    ville: Optional[str]
    id_proprietaire: Optional[int]
    id_agent: Optional[int]

    class Config:
        orm_mode = True


class BienCreate(BienBase):
    pass


class BienResponse(BienBase):
    id_bien: int


# Vente Schema
class VenteBase(BaseModel):
    id_bien: Optional[int]
    id_agent: Optional[int]
    id_proprietaire: Optional[int]
    date_vente: Optional[date]
    montant_paye: Optional[Decimal]
    etat: EtatEnum
    prix: Optional[Decimal]

    class Config:
        orm_mode = True


class VenteCreate(VenteBase):
    pass


class VenteResponse(VenteBase):
    id_vente: int


# Location Schema
class LocationBase(BaseModel):
    id_bien: int
    date_debut: date
    date_fin: date
    prix: int
    id_locataire: int
    etat: EtatEnum
    payment: Optional[int]

    class Config:
        orm_mode = True


class LocationCreate(LocationBase):
    pass


class LocationResponse(LocationBase):
    id_location: int


# Offre Schema
class OffreBase(BaseModel):
    id_agent: int
    id_bien: int
    montant: Decimal
    date_debut: Optional[date]
    date_fin: Optional[date]
    type: TypeEnum
    etat: EtatEnum

    class Config:
        orm_mode = True


class OffreCreate(OffreBase):
    pass


class OffreResponse(OffreBase):
    id_offre: int


# PaiementLoyer Schema
class PaiementLoyerBase(BaseModel):
    id_locataire: int
    id_location: int
    montant: Decimal
    date_paiement: Optional[date]

    class Config:
        orm_mode = True


class PaiementLoyerCreate(PaiementLoyerBase):
    pass


class PaiementLoyerResponse(PaiementLoyerBase):
    id_paiement: int


# DemandeMaintenance Schema
class DemandeMaintenanceBase(BaseModel):
    id_locataire: int
    id_location: int
    description: Optional[str]
    date_demande: Optional[date]
    etat: Optional[str]

    class Config:
        orm_mode = True


class DemandeMaintenanceCreate(DemandeMaintenanceBase):
    pass


class DemandeMaintenanceResponse(DemandeMaintenanceBase):
    id_demande: int


# Rapport Schema
class RapportBase(BaseModel):
    id_agent: int
    description: Optional[str]
    date_creation: Optional[date]

    class Config:
        orm_mode = True


class RapportCreate(RapportBase):
    pass


class RapportResponse(RapportBase):
    id_rapport: int


# RapportFinancier Schema
class RapportFinancierBase(BaseModel):
    id_proprietaire: int
    id_transaction: Optional[int]
    montant: Optional[Decimal]
    date_rapport: Optional[date]

    class Config:
        orm_mode = True


class RapportFinancierCreate(RapportFinancierBase):
    pass


class RapportFinancierResponse(RapportFinancierBase):
    id_rapport_financier: int


# Transaction Schema
class TransactionBase(BaseModel):
    montant: Decimal
    date_transaction: Optional[datetime]
    id_vente: Optional[int]
    id_location: Optional[int]

    class Config:
        orm_mode = True


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id_transaction: int

#secutity
class Token(BaseModel):
    acces_token: str
    token_type: str







