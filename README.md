# TeliaWeb — Project Assignment App

Internal web app for employees to register a profile and select projects they're interested in.

**Stack:** FastAPI · Supabase (PostgreSQL) · Vue 3 + Vite

---

## Database Setup (Supabase)

| Table | Purpose |
|---|---|
| `projects` | Master list of available projects (source for the dropdown) |
| `employees` | One row per registered employee |
| `employee_project_selections` | Many-to-many: which employee selected which projects |

---

## Backend Setup

```bash
cd backend

# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Edit .env and fill in:
#   SUPABASE_URL        → Supabase Dashboard → Project Settings → API → Project URL
#   SUPABASE_SERVICE_KEY → Supabase Dashboard → Project Settings → API → service_role key

# 4. Start the development server
uvicorn main:app --reload
# API available at http://localhost:8000
```

---

## Frontend Setup

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. (Optional) Set backend URL for production builds
#    Create frontend/.env.local and add:
#    VITE_API_BASE=https://your-backend-domain.com
#    In development the Vite proxy handles /api → localhost:8000 automatically.

# 3. Start the dev server
npm run dev
# App available at http://localhost:5173
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/projects/` | List active projects (populates the dropdown) |
| `GET` | `/api/employees/{id}` | Get employee by UUID |
| `GET` | `/api/employees/by-email/{email}` | Look up employee by email |
| `POST` | `/api/employees/` | Register a new employee profile |
| `PUT` | `/api/employees/{id}` | Update profile + replace project selections |
| `GET` | `/api/health` | Health check |

Interactive API docs: `http://localhost:8000/docs`

---

## How the Form Works

1. **New user** — fills in email, completes the form, clicks *Save Profile*. The employee UUID is stored in `localStorage` for the next visit.
2. **Returning user (same browser)** — on load the stored UUID is used to pre-fill the form automatically.
3. **Returning user (new browser)** — enters their email and clicks out of the field; if the address exists the profile is loaded automatically.
4. **Clear Form** — resets all fields and removes the stored UUID.
