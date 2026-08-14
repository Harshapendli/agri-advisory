from beanie import Document, Indexed
from pydantic import EmailStr, Field
from typing import Optional
from datetime import datetime
import bcrypt as _bcrypt

class _BcryptContext:
    """Simple bcrypt wrapper that works with bcrypt 4.x and 5.x."""
    def hash(self, password: str) -> str:
        return _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')

    def verify(self, password: str, hashed: str) -> bool:
        try:
            return _bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

pwd_context = _BcryptContext()

class User(Document):
    email: Optional[Indexed(EmailStr, unique=True)] = None
    phone: Optional[Indexed(str, unique=True)] = None
    hashed_password: str
    name: str
    preferred_language: str = "en"
    state: Optional[str] = None
    district: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "users"

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        return await cls.find_one(cls.email == email)

    @classmethod
    async def get_by_phone(cls, phone: str) -> Optional["User"]:
        return await cls.find_one(cls.phone == phone)
