from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from database import supabase
from models import EmployeeCreate, EmployeeOut, EmployeeUpdate

router = APIRouter()


def _attach_projects(employee: dict) -> dict:
    """Fetch the employee's selected projects and attach them to the dict."""
    result = (
        supabase.table("employee_project_selections")
        .select("project_id, projects(*)")
        .eq("employee_id", employee["id"])
        .execute()
    )
    employee["projects"] = [
        row["projects"] for row in result.data if row.get("projects")
    ]
    return employee


# IMPORTANT: the /by-email route must be declared before /{employee_id}
# so FastAPI does not try to parse "by-email" as a UUID.

@router.get("/by-email/{email}", response_model=EmployeeOut)
def get_employee_by_email(email: str):
    """Look up an employee profile by email address (used for returning users)."""
    result = (
        supabase.table("employees")
        .select("*")
        .eq("email", email)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _attach_projects(result.data[0])


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: UUID):
    """Fetch a single employee profile by ID."""
    result = (
        supabase.table("employees")
        .select("*")
        .eq("id", str(employee_id))
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _attach_projects(result.data[0])


@router.post("/", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate):
    """Register a new employee profile with their project selections."""
    # Guard against duplicate emails
    existing = (
        supabase.table("employees")
        .select("id")
        .eq("email", payload.email)
        .execute()
    )
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this email is already registered.",
        )

    employee_data = payload.model_dump(exclude={"project_ids"})
    result = supabase.table("employees").insert(employee_data).execute()
    employee = result.data[0]

    if payload.project_ids:
        selections = [
            {"employee_id": employee["id"], "project_id": str(pid)}
            for pid in payload.project_ids
        ]
        supabase.table("employee_project_selections").insert(selections).execute()

    return _attach_projects(employee)


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: UUID, payload: EmployeeUpdate):
    """Update an existing employee profile and replace their project selections."""
    existing = (
        supabase.table("employees")
        .select("id")
        .eq("id", str(employee_id))
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = payload.model_dump(exclude={"project_ids"}, exclude_none=True)
    if update_data:
        supabase.table("employees").update(update_data).eq("id", str(employee_id)).execute()

    # Replace selections only when project_ids is explicitly provided
    if payload.project_ids is not None:
        supabase.table("employee_project_selections").delete().eq(
            "employee_id", str(employee_id)
        ).execute()
        if payload.project_ids:
            selections = [
                {"employee_id": str(employee_id), "project_id": str(pid)}
                for pid in payload.project_ids
            ]
            supabase.table("employee_project_selections").insert(selections).execute()

    result = (
        supabase.table("employees")
        .select("*")
        .eq("id", str(employee_id))
        .execute()
    )
    return _attach_projects(result.data[0])
