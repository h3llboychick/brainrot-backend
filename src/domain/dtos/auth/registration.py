from pydantic import BaseModel, EmailStr


class EmailRegistrationDTO(BaseModel):
    email: EmailStr
    password: str
