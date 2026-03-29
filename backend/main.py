from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import employees, projects

app = FastAPI(title="Project Assignment API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:4173",  # Vite preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok"}
