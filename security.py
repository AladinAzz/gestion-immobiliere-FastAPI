from datetime import datetime, timedelta
from typing import Optional,Annotated
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi import APIRouter
from database import get_db
from sqlalchemy.orm import Session
from schemas import Token
from models import Utilisateur
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
auth = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "BDD_Project"  # Use a strong, random key for production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_Bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token with the provided data and expiration time.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token format")



def get_current_user_from_token(token: Annotated[str, Depends(oauth2_Bearer)]):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        role=payload.get('role')
        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token1")
        return {'user_id':user_id,'role':role} 
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token2")





  # URL of the login endpoint


db_dependency=Annotated[Session,Depends(get_db)]

@auth.post("/token",response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm , Depends()],db:db_dependency):
    user=authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect email or password")
    token_data = {"user_id": user.id_utilisateur,  "role": user.role}
    token=create_access_token(token_data,expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {'acces_token':token,'token_type':'bearer'}

def authenticate_user(email: str, password: str, db: Session) -> Optional[Utilisateur]:
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.mot_de_passe):
        return False
    return user


