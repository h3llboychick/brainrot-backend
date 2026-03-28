from pydantic import BaseModel


class ConnectYoutubeAccountDTO(BaseModel):
    user_id: str
    payload: dict


class DisconnectYoutubeAccountDTO(BaseModel):
    user_id: str


class CheckYoutubeAccountStatusDTO(BaseModel):
    user_id: str
