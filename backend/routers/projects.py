from fastapi import APIRouter, HTTPException

from database import supabase
from models import ProjectOut

router = APIRouter()


@router.get("/", response_model=list[ProjectOut])
def list_projects():
    """Return all active projects for the multi-select dropdown."""
    result = (
        supabase.table("projects")
        .select("*")
        .eq("is_active", True)
        .order("name")
        .execute()
    )
    return result.data
