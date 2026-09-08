from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ---------- User schemas ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Token schema ----------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

from models import ApplicationStatus, RoleType

# ---------- Application schemas ----------

class ApplicationCreate(BaseModel):
    company_name: str
    role_title: str
    job_description: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
    applied_date: datetime
    source: Optional[str] = None


class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    job_description: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    applied_date: Optional[datetime] = None
    source: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    company_name: str
    role_title: str
    job_description: Optional[str] = None
    status: ApplicationStatus
    applied_date: datetime
    source: Optional[str] = None
    match_score: Optional[float] = None
    predicted_role_type: Optional[RoleType] = None
    created_at: datetime

    class Config:
        from_attributes = True


from typing import Dict, List


# ---------- Analytics schemas ----------

class MonthCount(BaseModel):
    month: str   # e.g. "2026-09"
    count: int


class AnalyticsOut(BaseModel):
    by_status: Dict[str, int]
    by_month: List[MonthCount]

class ResumeUpdate(BaseModel):
    resume_text: str

class SkillGapOut(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]
    required_years_experience: int
    user_years_experience: int
    experience_gap: bool

class ExperienceUpdate(BaseModel):
    years_of_experience: int
