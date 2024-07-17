from pydantic import BaseModel


class User(BaseModel):
    registration_id: str
    avatar_base64: str
    event_id: str


class Face(BaseModel):
    event_id: str
    avatar_checkin_base64: str


class DeleteID(BaseModel):
    registration_id: str
    event_id: str