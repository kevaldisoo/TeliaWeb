from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator, model_validator


# ── Outbound ──────────────────────────────────────────────────────────────────

class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    is_active: bool


class EmployeeOut(BaseModel):
    id: UUID
    full_name: str
    email: str
    experience_level: str
    tech_stack: str
    preferred_duration: str
    additional_skills: Optional[str] = None
    availability_confirmed: bool
    created_at: datetime
    updated_at: datetime
    projects: list[ProjectOut] = []


# ── Inbound ───────────────────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    full_name: str
    email: EmailStr
    experience_level: Literal["junior", "mid", "senior"]
    tech_stack: Literal["backend", "frontend", "fullstack", "data", "devops", "mobile"]
    preferred_duration: Literal["short", "medium", "long"]
    additional_skills: Optional[str] = None
    availability_confirmed: bool = False
    project_ids: list[UUID] = []

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Full name is required.")
        if len(v) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        return v

    @field_validator("additional_skills")
    @classmethod
    def strip_additional_skills(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v

    @field_validator("project_ids")
    @classmethod
    def at_least_one_project(cls, v: list[UUID]) -> list[UUID]:
        if not v:
            raise ValueError("Please select at least one project.")
        return v

    @model_validator(mode="after")
    def availability_must_be_confirmed(self) -> "EmployeeCreate":
        if not self.availability_confirmed:
            raise ValueError("You must confirm your availability before registering.")
        return self


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    experience_level: Optional[Literal["junior", "mid", "senior"]] = None
    tech_stack: Optional[Literal["backend", "frontend", "fullstack", "data", "devops", "mobile"]] = None
    preferred_duration: Optional[Literal["short", "medium", "long"]] = None
    additional_skills: Optional[str] = None
    availability_confirmed: Optional[bool] = None
    project_ids: Optional[list[UUID]] = None

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Full name is required.")
        if len(v) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        return v

    @field_validator("additional_skills")
    @classmethod
    def strip_additional_skills(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v

    @field_validator("project_ids")
    @classmethod
    def at_least_one_project(cls, v: Optional[list[UUID]]) -> Optional[list[UUID]]:
        # None means "don't change selections"; empty list is an explicit clear and is rejected
        if v is not None and len(v) == 0:
            raise ValueError("Please select at least one project.")
        return v
