from pydantic import BaseModel

class EmailRegistrationDTO(BaseModel):
    email: str
    password: str

