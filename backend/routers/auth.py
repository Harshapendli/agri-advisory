from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from models.user import User
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class RegisterRequest(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    state: Optional[str] = None
    preferred_language: str = "en"

class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    preferred_language: str

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await User.get(user_id)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    if not req.email and not req.phone:
        raise HTTPException(status_code=400, detail="Email or phone required")
    try:
        if req.email:
            existing = await User.get_by_email(req.email)
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")
        if req.phone:
            existing = await User.get_by_phone(req.phone)
            if existing:
                raise HTTPException(status_code=400, detail="Phone already registered")
        user = User(
            name=req.name,
            email=req.email,
            phone=req.phone,
            hashed_password=User.hash_password(req.password),
            state=req.state,
            preferred_language=req.preferred_language,
        )
        await user.insert()
        token = create_access_token({"sub": str(user.id)})
        return TokenResponse(access_token=token, user_id=str(user.id), name=user.name, preferred_language=user.preferred_language)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    user = None
    if req.email:
        user = await User.get_by_email(req.email)
    elif req.phone:
        user = await User.get_by_phone(req.phone)
    if not user or not user.verify_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user_id=str(user.id), name=user.name, preferred_language=user.preferred_language)

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": str(current_user.id), "name": current_user.name, "email": current_user.email,
            "phone": current_user.phone, "state": current_user.state, "preferred_language": current_user.preferred_language}
