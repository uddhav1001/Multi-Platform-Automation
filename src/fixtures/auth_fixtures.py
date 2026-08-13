"""
Role-based authenticated storage-state fixtures.

How it works:
  1. A one-time session fixture logs in as each role and saves Playwright's
     storage state (cookies + localStorage) to a temp file.
  2. Individual tests receive a pre-authenticated `page` via `browser.new_context`
     so the login page is never hit again, removing a whole class of timing flakes.

Usage:
    def test_admin_action(admin_page, env_config):
        admin_page.goto(f"{env_config['base_url']}/admin/settings")
        ...

    def test_employee_cannot_delete(employee_page, env_config):
        employee_page.goto(f"{env_config['base_url']}/projects")
        ...
"""

import os
import tempfile
import pytest
from playwright.sync_api import sync_playwright


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _login_and_save_state(email: str, password: str, base_url: str) -> str:
    """Log in headlessly, persist storage state to a temp file, return its path."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(f"{base_url}/login")
        page.get_by_label("Email").fill(email)
        page.get_by_label("Password").fill(password)
        page.get_by_role("button", name="Log in").click()
        page.wait_for_url(f"{base_url}/dashboard", timeout=15_000)
        # Handle optional 2FA: probe for TOTP field here in a real project.
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        ctx.storage_state(path=tmp.name)
        browser.close()
        return tmp.name


# ---------------------------------------------------------------------------
# Role credentials (override with environment variables in CI)
# ---------------------------------------------------------------------------

ROLE_CREDENTIALS = {
    "admin": {
        "email":    os.getenv("TEST_ADMIN_EMAIL",    "admin@company1.com"),
        "password": os.getenv("TEST_ADMIN_PASSWORD", "AdminPass123"),
    },
    "manager": {
        "email":    os.getenv("TEST_MANAGER_EMAIL",    "manager@company1.com"),
        "password": os.getenv("TEST_MANAGER_PASSWORD", "ManagerPass123"),
    },
    "employee": {
        "email":    os.getenv("TEST_EMPLOYEE_EMAIL",    "tenant@company2.com"),
        "password": os.getenv("TEST_EMPLOYEE_PASSWORD", "TenantPass123"),
    },
}


# ---------------------------------------------------------------------------
# Session-scoped storage-state fixtures (login once per test run)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def admin_state(env_config):
    creds = ROLE_CREDENTIALS["admin"]
    path = _login_and_save_state(creds["email"], creds["password"], env_config["base_url"])
    yield path
    os.unlink(path)


@pytest.fixture(scope="session")
def manager_state(env_config):
    creds = ROLE_CREDENTIALS["manager"]
    path = _login_and_save_state(creds["email"], creds["password"], env_config["base_url"])
    yield path
    os.unlink(path)


@pytest.fixture(scope="session")
def employee_state(env_config):
    creds = ROLE_CREDENTIALS["employee"]
    path = _login_and_save_state(creds["email"], creds["password"], env_config["base_url"])
    yield path
    os.unlink(path)


# ---------------------------------------------------------------------------
# Function-scoped page fixtures — each test gets a fresh page in the right role
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_page(playwright, admin_state):
    browser = playwright.chromium.launch()
    ctx = browser.new_context(storage_state=admin_state)
    page = ctx.new_page()
    yield page
    browser.close()


@pytest.fixture
def manager_page(playwright, manager_state):
    browser = playwright.chromium.launch()
    ctx = browser.new_context(storage_state=manager_state)
    page = ctx.new_page()
    yield page
    browser.close()


@pytest.fixture
def employee_page(playwright, employee_state):
    browser = playwright.chromium.launch()
    ctx = browser.new_context(storage_state=employee_state)
    page = ctx.new_page()
    yield page
    browser.close()
