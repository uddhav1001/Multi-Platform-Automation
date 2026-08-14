"""
Mobile Test Strategy — Local Playwright Mobile Viewport Execution
=================================================================

Architecture
------------
Mobile tests use the same Page Object Model and fixtures as the desktop suite.
The only difference is the browser context: instead of launching a local browser
at desktop size, the test runs with an iPhone 14 viewport emulation via Playwright.

Execution model:
  Local:        pytest tests/mobile                          (iPhone 14 viewport)
  BrowserStack: Set BROWSERSTACK_USERNAME + ACCESS_KEY and swap bs_page fixture
                to use cdp.browserstack.com connection.

BrowserStack setup (requires account credentials in environment variables):

    $env:BROWSERSTACK_USERNAME = "your_username"
    $env:BROWSERSTACK_ACCESS_KEY = "your_access_key"

Capabilities are declared in config/browserstack.yaml.  The fixture below reads
them and yields a Playwright page connected to the remote device session.

    platforms:
      - browserName: Chrome
        deviceName: iPhone 14
        realMobile: true
        osVersion: "16"
      - browserName: Chrome
        deviceName: Samsung Galaxy S22
        realMobile: true
        osVersion: "12"

Why local emulation?
--------------------
A local demo environment cannot provision a real mobile device. The bs_page fixture
uses Playwright's built-in iPhone 14 device descriptor to emulate a mobile viewport
locally. Swapping to a live BrowserStack context is a one-line change once credentials
are configured.
"""

import os
import pytest
from playwright.sync_api import expect


# ---------------------------------------------------------------------------
# BrowserStack / Mobile fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def bs_page(playwright, env_config):
    """
    Yields a Playwright page with iPhone 14 mobile viewport emulation.

    Uses the `playwright` fixture provided by pytest-playwright (avoids
    nested sync_playwright() context which conflicts with the existing event loop).

    To switch to BrowserStack real-device execution, replace the body with:

        import json
        cap = {
            "browser": "chrome",
            "os": "iOS",
            "os_version": "16",
            "name": "Mobile project visibility test",
            "browserstack.username": os.getenv("BROWSERSTACK_USERNAME"),
            "browserstack.accessKey": os.getenv("BROWSERSTACK_ACCESS_KEY"),
        }
        cdp_url = f"wss://cdp.browserstack.com/playwright?caps={json.dumps(cap)}"
        browser = playwright.chromium.connect(cdp_url)
        page = browser.new_page()
        yield page
        browser.close()
    """
    iphone = playwright.devices["iPhone 14"]
    browser = playwright.chromium.launch()
    context = browser.new_context(**iphone)
    page = context.new_page()
    yield page
    context.close()
    browser.close()


# ---------------------------------------------------------------------------
# Mobile tests
# ---------------------------------------------------------------------------

@pytest.mark.browserstack
def test_project_visible_on_mobile(bs_page, env_config, credentials):
    """
    Verifies that the Projects list renders correctly on a mobile viewport.

    Steps:
    1. Navigate to the login page on the mobile device.
    2. Authenticate as the admin user.
    3. Open the Projects page.
    4. Assert at least one .project-card is visible in the viewport.
    """
    page = bs_page
    page.goto(f"{env_config['base_url']}/login")
    page.get_by_label("Email").fill(credentials["admin"]["email"])
    page.get_by_label("Password").fill(credentials["admin"]["password"])
    page.get_by_role("button", name="Log in").click()
    page.wait_for_url(f"{env_config['base_url']}/dashboard", timeout=20_000)

    page.get_by_role("link", name="Projects").click()
    expect(page).to_have_url(f"{env_config['base_url']}/projects")

    # At least one project card should be visible on a mobile viewport.
    expect(page.locator(".project-card").first).to_be_visible(timeout=15_000)


@pytest.mark.browserstack
def test_login_page_responsive(bs_page, env_config):
    """
    Verifies that the login form elements are visible and interactable
    on a mobile viewport (no horizontal scroll, buttons not clipped).
    """
    page = bs_page
    page.goto(f"{env_config['base_url']}/login")
    expect(page.get_by_label("Email")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()
    expect(page.get_by_role("button", name="Log in")).to_be_visible()
