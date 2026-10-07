from pydantic import BaseModel, Field
from typing import List, Optional

class RecipientCreate(BaseModel):
    recipient_name: str = Field(..., min_length=1, description="Name of the recipient")
    course_name: str = Field(..., min_length=1, description="Name of the course")

class JobCreate(BaseModel):
    recipients: List[RecipientCreate] = Field(..., min_length=1, description="List of recipients")

class CertificateResponse(BaseModel):
    id: int
    recipient_name: str
    course_name: str
    status: str
    error_message: Optional[str]

    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    id: int
    status: str
    certificates: List[CertificateResponse]

    class Config:
        from_attributes = True