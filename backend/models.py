from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


# ── Outbound ─────────────────────────────────────────────────────────────────

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


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    experience_level: Optional[Literal["junior", "mid", "senior"]] = None
    tech_stack: Optional[Literal["backend", "frontend", "fullstack", "data", "devops", "mobile"]] = None
    preferred_duration: Optional[Literal["short", "medium", "long"]] = None
    additional_skills: Optional[str] = None
    availability_confirmed: Optional[bool] = None
    project_ids: Optional[list[UUID]] = None
