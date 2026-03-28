from pydantic import BaseModel, EmailStr


class EmailVerificationDTO(BaseModel):
    email: EmailStr
    verification_code: str
