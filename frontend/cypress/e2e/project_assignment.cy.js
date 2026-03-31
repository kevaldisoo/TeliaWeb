// ── Shared fixture data ───────────────────────────────────────────────────────
// Using fixed UUIDs lets the intercepts stay consistent across all three tests.

const PROJECT_API_GATEWAY = {
  id: '9b71d3ba-f5b2-4d76-94ad-8117b51d8e75',
  name: 'API Gateway Implementation',
  description: null,
  is_active: true,
}
const PROJECT_CLOUD_INFRA = {
  id: 'bf4fd3e6-d564-4189-a667-e225e076b568',
  name: 'Cloud Infrastructure Setup',
  description: null,
  is_active: true,
}

const ALL_PROJECTS = [
  { id: '65b49885-5342-483b-9528-56b70f47bebe', name: 'Customer Portal Redesign',                description: null, is_active: true },
  { id: '9ca9a991-05db-4251-89a8-192b0248cd16', name: 'Data Pipeline Migration',                 description: null, is_active: true },
  { id: '3700902a-b0aa-460c-9997-065155a1bea8', name: 'Mobile App Enhancement',                  description: null, is_active: true },
  { id: '1ba1da57-5794-45d8-b8f5-ecce36347172', name: 'Internal Analytics Dashboard',            description: null, is_active: true },
  PROJECT_API_GATEWAY,
  PROJECT_CLOUD_INFRA,
  { id: 'e5239c4b-daad-4bb6-a18b-09e73a8e067c', name: 'E-commerce Platform Update',             description: null, is_active: true },
  { id: 'e667ec2c-f7f1-405e-bde2-0d4e98aefc5a', name: 'Reporting System Automation',            description: null, is_active: true },
  { id: '95d578d2-5e16-4e82-ae85-4f63110ea6d1', name: 'Microservices Architecture Transition',  description: null, is_active: true },
  { id: '7ee75d00-7b72-40ca-b0ab-275253e6465b', name: 'Customer Data Platform Integration',     description: null, is_active: true },
]

const EMPLOYEE = {
  id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
  full_name: 'Test User Two',
  email: 'test2@test.com',
  experience_level: 'junior',
  tech_stack: 'backend',
  preferred_duration: 'medium',
  additional_skills: null,
  availability_confirmed: true,
  created_at: '2026-03-31T12:00:00+00:00',
  updated_at: '2026-03-31T12:00:00+00:00',
  projects: [PROJECT_API_GATEWAY, PROJECT_CLOUD_INFRA],
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe('Project Assignment Form', () => {
  beforeEach(() => {
    // Intercept the projects list for every test so the multi-select always populates
    cy.intercept('GET', '/api/projects/', { body: ALL_PROJECTS }).as('getProjects')
    cy.clearLocalStorage()
    cy.visit('/')
    cy.wait('@getProjects')
    // Confirm options are rendered before any test body runs
    cy.get('#projects option').should('have.length', ALL_PROJECTS.length)
  })

  // ── Test 1: create a new profile ───────────────────────────────────────────
  // The POST is intercepted so the test is repeatable regardless of what is
  // already stored in Supabase / the fallback database.

  it('creates a new employee profile for test2@test.com', () => {
    cy.intercept('POST', '/api/employees/', {
      statusCode: 201,
      body: EMPLOYEE,
    }).as('createEmployee')

    cy.get('#full_name').type('Test User Two')
    cy.get('#email').type('test2@test.com')
    cy.get('#experience_level').select('junior')
    cy.get('#tech_stack').select('backend')
    cy.get('#projects').select(['API Gateway Implementation', 'Cloud Infrastructure Setup'])
    cy.get('input[type="radio"][value="medium"]').check()
    cy.get('input[type="checkbox"]').check()

    cy.get('button[type="submit"]').click()
    cy.wait('@createEmployee')

    cy.get('.notification.success')
      .should('be.visible')
      .and('contain', 'Profile registered successfully')
  })

  // ── Test 2: load existing profile by email ─────────────────────────────────
  // The by-email lookup is intercepted and returns the same fixture used in
  // test 1, so this test is independent of test 1 having run against a real DB.

  it('loads the existing profile for test2@test.com with correct data', () => {
    cy.intercept('GET', '/api/employees/by-email/*', {
      body: EMPLOYEE,
    }).as('getByEmail')

    cy.get('#email').type('test2@test.com').blur()
    cy.wait('@getByEmail')

    cy.get('.notification.success')
      .should('be.visible')
      .and('contain', 'Existing profile loaded')

    cy.get('#full_name').should('have.value', 'Test User Two')
    cy.get('#experience_level').should('have.value', 'junior')
    cy.get('#tech_stack').should('have.value', 'backend')
    cy.get('input[type="radio"][value="medium"]').should('be.checked')

    cy.get('#projects option:selected').then(($opts) => {
      const names = [...$opts].map((o) => o.text.trim())
      expect(names).to.include('API Gateway Implementation')
      expect(names).to.include('Cloud Infrastructure Setup')
      expect(names).to.have.length(2)
    })
  })

  // ── Test 3: invalid email is rejected ─────────────────────────────────────
  // All other fields are valid; only the email is intentionally wrong.
  // No additional intercepts are needed — the form is rejected client-side
  // before any network request is made.

  it('shows a validation error when submitting an invalid email address', () => {
    cy.get('#full_name').type('Some Name')
    cy.get('#email').type('not-an-email')
    cy.get('#experience_level').select('junior')
    cy.get('#tech_stack').select('backend')
    cy.get('#projects').select(['API Gateway Implementation'])
    cy.get('input[type="radio"][value="short"]').check()
    cy.get('input[type="checkbox"]').check()

    cy.get('button[type="submit"]').click()

    cy.contains('p.error-msg', 'Please enter a valid email address').should('be.visible')
    cy.get('.notification.error').should('be.visible')
  })
})
