# TeliaWeb — Project Assignment App

Internal web app for employees to register a profile and select projects they're interested in.

**Stack:** FastAPI · Supabase (PostgreSQL) · Vue 3 + Vite

---

## Database Setup (Supabase)
Supabase for used for the convenience of adding tables and classes.
The project also has clean_dump.sql, which is used when there isn't a connection to Supabase database.

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
#   SUPABASE_URL 
#   SUPABASE_SERVICE_KEY 

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

# 2. Start the dev server
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

---

## Running the Tests

The test suite uses [Cypress](https://cypress.io) for end-to-end tests. All three tests use `cy.intercept()` to stub API responses, so they are fully repeatable without touching the database.

### Prerequisites

Both the backend and the frontend preview server must be running before Cypress starts.

```bash
# Terminal 1 — backend
cd backend
uvicorn main:app --reload
# Runs on http://localhost:8000

# Terminal 2 — frontend preview (matches Cypress baseUrl: http://localhost:4173)
cd frontend
npm run build && npm run preview
# Runs on http://localhost:4173
```

### Run tests headlessly (CI / quick check)

```bash
cd frontend
npx cypress run --spec "cypress/e2e/project_assignment.cy.js"
```

### Run tests in the interactive Cypress UI

```bash
cd frontend
npx cypress open
# Select E2E Testing → choose a browser → click project_assignment.cy.js
```

### What the tests cover

| # | Test | How it works |
|---|---|---|
| 1 | **Create profile** — fills out the full form for `test2@test.com` and submits | POST `/api/employees/` is intercepted; always returns success regardless of DB state |
| 2 | **Load returning user** — enters `test2@test.com`, blurs the email field, verifies the form auto-populates with the correct data | GET `/api/employees/by-email/*` is intercepted; returns a fixed employee fixture |
| 3 | **Invalid email rejected** — submits the form with `not-an-email` as the email address | No intercepts needed; validation is client-side |

---

## How the Form Works

1. **New user** — fills in email, completes the form, clicks *Save Profile*. The employee UUID is stored in `localStorage` for the next visit.
2. **Returning user (same browser)** — on load the stored UUID is used to pre-fill the form automatically.
3. **Returning user (new browser)** — enters their email and clicks out of the field; if the address exists the profile is loaded automatically.
4. **Clear Form** — resets all fields and removes the stored UUID.

## Use of AI

AI was used for visually designing the frontpage and creating the script for reading the dump.sql file. 