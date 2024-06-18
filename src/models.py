from pydantic import BaseModel


class User(BaseModel):
    verify_id: str
    avatar_base64: str


class Face(BaseModel):
    face_base64: str


class DeleteID(BaseModel):
    verify_id: str
