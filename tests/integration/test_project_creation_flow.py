"""
Part 3: API + UI Integration Test

This test validates the complete flow of project creation across all layers:
API creation, Desktop Web UI verification, Mobile UI verification (local viewport),
and API/UI Security boundaries (Tenant Isolation).

Strategy & Edge Case Handling:
- Test Data: We generate a unique UUID project name to prevent test collision. Data setup/teardown 
  is managed via API (faster and more reliable than UI).
- Network Failures / Slow API: Handled by `ProjectClient` which implements exponential backoff retries.
- Slow UI Loading: Handled by Playwright's auto-waiting `expect(locator).to_be_visible(timeout=10000)`.
- Cross-Platform: Desktop UI runs in the configured browser. Mobile is emulated locally via
  Playwright's iPhone 14 device descriptor (using the `playwright` fixture from pytest-playwright).
"""

import os
import json
import urllib.parse
import pytest
from playwright.sync_api import expect
from src.api.project_client import ProjectClient
from src.utils.data_generator import unique_project_name

def test_project_creation_flow(playwright, page, api_token, credentials, env_config):
    # Setup test data variables
    project_name = unique_project_name()
    company1_client = ProjectClient(env_config['api_base'], api_token, 'company1')
    company2_client = ProjectClient(env_config['api_base'], api_token, 'company2')
    project_id = None
    
    try:
        # ---------------------------------------------------------------------
        # 1. API: Create project
        # ---------------------------------------------------------------------
        # We create the project via API because it is much faster and less flaky 
        # than driving the UI to create test data.
        create_resp = company1_client.create(project_name)
        assert create_resp.status_code in (200, 201), f"API creation failed: {create_resp.text}"
        
        project_data = create_resp.json()
        project_id = project_data['id']
        assert project_data['name'] == project_name
        assert project_data['status'] == 'active'

        # ---------------------------------------------------------------------
        # 2. Web UI: Verify project display
        # ---------------------------------------------------------------------
        # Navigate to the app and authenticate as Company 1 admin
        page.goto(f"{env_config['base_url']}/login")
        page.get_by_label('Email').fill(credentials['admin']['email'])
        page.get_by_label('Password').fill(credentials['admin']['password'])
        page.get_by_role('button', name='Log in').click()
        page.wait_for_url(f"{env_config['base_url']}/dashboard", timeout=15000)

        # Navigate to projects with the search query param applied server-side.
        # The Flask app filters via GET ?search=; using URL navigation is more robust
        # than filling the search input and submitting the form manually.
        search_param = urllib.parse.urlencode({'search': project_name})
        page.goto(f"{env_config['base_url']}/projects?{search_param}")

        # Edge Case: Dynamic rendering / Slow networks
        # Playwright auto-retries the visibility assertion until the timeout is reached.
        project_card = page.locator('.project-card', has_text=project_name)
        expect(project_card).to_be_visible(timeout=10000)


        # ---------------------------------------------------------------------
        # 3. Mobile: Check mobile accessibility
        # ---------------------------------------------------------------------
        # We use Playwright's built-in iPhone 14 device emulation for local runs.
        # Using the `playwright` fixture from pytest-playwright avoids the event loop
        # conflict that would occur if sync_playwright() were called inside a test.
        #
        # To switch to BrowserStack real-device execution, replace the context creation:
        #   cap = {"browser": "chrome", "os": "iOS", "os_version": "16",
        #          "browserstack.username": os.getenv("BROWSERSTACK_USERNAME"),
        #          "browserstack.accessKey": os.getenv("BROWSERSTACK_ACCESS_KEY")}
        #   cdp_url = f"wss://cdp.browserstack.com/playwright?caps={json.dumps(cap)}"
        #   mobile_browser = playwright.chromium.connect(cdp_url)

        iphone = playwright.devices["iPhone 14"]
        mobile_browser = playwright.chromium.launch()
        mobile_context = mobile_browser.new_context(**iphone)
        mobile_page = mobile_context.new_page()

        try:
            # Verify project is visible on mobile viewport
            mobile_page.goto(f"{env_config['base_url']}/login")
            mobile_page.get_by_label('Email').fill(credentials['admin']['email'])
            mobile_page.get_by_label('Password').fill(credentials['admin']['password'])
            mobile_page.get_by_role('button', name='Log in').click()
            mobile_page.wait_for_url(f"{env_config['base_url']}/dashboard", timeout=15000)

            mobile_page.goto(f"{env_config['base_url']}/projects?{search_param}")
            expect(mobile_page.locator('.project-card', has_text=project_name)).to_be_visible(timeout=10000)
        finally:
            mobile_context.close()
            mobile_browser.close()


        # ---------------------------------------------------------------------
        # 4. Security: Verify tenant isolation
        # ---------------------------------------------------------------------
        # Ensure Company 2 cannot access or mutate Company 1's project via API.
        
        # Read constraint bounding: Company 2 should not be able to fetch the project. 
        # (Assuming a GET /projects/{id} endpoint exists for the sake of the security test).
        # We test the DELETE constraint here since it's the implemented endpoint in the demo:
        delete_attempt = company2_client.delete(project_id)
        assert delete_attempt.status_code in (403, 404), (
            f"Isolation failure: Tenant 2 deleted Tenant 1's project (got {delete_attempt.status_code})"
        )
        
    finally:
        # ---------------------------------------------------------------------
        # Teardown: Clean up test data
        # ---------------------------------------------------------------------
        # We use a try/finally block to ensure the project is deleted from the backend 
        # even if an assertion in the UI/Mobile steps fails.
        if project_id:
            company1_client.delete(project_id)
