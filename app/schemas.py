from pydantic import BaseModel
from typing import List

class DocumentUploadResponse(BaseModel):
    id: int
    filename: str

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: List[str]
