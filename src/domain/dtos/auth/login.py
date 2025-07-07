from pydantic import BaseModel

class EmailLoginDTO(BaseModel):
    email: str
    password: str

class GoogleSignInDTO(BaseModel):
    google_id: str
    email: str