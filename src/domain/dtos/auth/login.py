from pydantic import BaseModel, EmailStr


class EmailLoginDTO(BaseModel):
    email: EmailStr
    password: str


class GoogleSignInDTO(BaseModel):
    google_id: str
    email: EmailStr
