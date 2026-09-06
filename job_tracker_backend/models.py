import enum
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime,
    ForeignKey, Enum, func
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class ApplicationStatus(str, enum.Enum):
    APPLIED = "applied"
    OA = "oa"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class RoleType(str, enum.Enum):
    SDE = "sde"
    DATA = "data"
    ML_AI = "ml_ai"
    PRODUCT = "product"
    DESIGN = "design"
    OTHER = "other"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=True)
    resume_text = Column(Text, nullable=True)
    years_of_experience = Column(Integer, nullable=True, default=0)   # <-- new field

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    applications = relationship(
        "Application", back_populates="owner", cascade="all, delete-orphan"
    )


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    company_name = Column(String(150), nullable=False)
    role_title = Column(String(150), nullable=False)
    job_description = Column(Text, nullable=True)

    status = Column(Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.APPLIED, index=True)
    applied_date = Column(DateTime, nullable=False)
    source = Column(String(100), nullable=True)

    match_score = Column(Float, nullable=True)
    predicted_role_type = Column(Enum(RoleType), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="applications")
    status_history = relationship(
        "StatusHistory", back_populates="application",
        cascade="all, delete-orphan", order_by="StatusHistory.changed_at"
    )
    cover_letters = relationship(
        "CoverLetter", back_populates="application", cascade="all, delete-orphan"
    )


class StatusHistory(Base):
    __tablename__ = "status_history"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)

    status = Column(Enum(ApplicationStatus), nullable=False)
    changed_at = Column(DateTime, server_default=func.now(), nullable=False)
    note = Column(String(255), nullable=True)

    application = relationship("Application", back_populates="status_history")


class CoverLetter(Base):
    __tablename__ = "cover_letters"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)

    content = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=True)
    generated_at = Column(DateTime, server_default=func.now())

    application = relationship("Application", back_populates="cover_letters")