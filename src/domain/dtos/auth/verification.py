from pydantic import BaseModel

class EmailVerificationDTO(BaseModel):
    email: str
    verification_code: str