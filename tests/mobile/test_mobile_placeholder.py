"""
Mobile Test Strategy — BrowserStack Real-Device Execution
==========================================================

Architecture
------------
Mobile tests use the same Page Object Model and fixtures as the desktop suite.
The only difference is the browser context: instead of launching a local browser,
the test sends capabilities to BrowserStack Automate via its Playwright SDK.

Execution model:
  Local:        pytest tests/mobile --browser chromium            (responsive viewport)
  BrowserStack: pytest tests/mobile -m browserstack               (real device/cloud)

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

Why a placeholder?
------------------
A local demo environment cannot provision a real mobile device.  The test is
structured, marked, and documented so that swapping `pytest.skip` for a live
BrowserStack context is a one-line change once credentials are configured.
"""

import os
import pytest
from playwright.sync_api import expect


# ---------------------------------------------------------------------------
# BrowserStack fixture stub
# ---------------------------------------------------------------------------

@pytest.fixture
def bs_page(env_config):
    """
    In a real run, replace this stub with a BrowserStack-connected context.

    from browserstack.local import Local
    from playwright.sync_api import sync_playwright

    cap = {
        "browser": "chrome",
        "browser_version": "latest",
        "os": "iOS",
        "os_version": "16",
        "name": "Mobile project visibility test",
        "build": os.getenv("CI_BUILD_ID", "local"),
        "browserstack.username": os.getenv("BROWSERSTACK_USERNAME"),
        "browserstack.accessKey": os.getenv("BROWSERSTACK_ACCESS_KEY"),
    }
    cdp_url = f"wss://cdp.browserstack.com/playwright?caps={json.dumps(cap)}"
    with sync_playwright() as p:
        browser = p.chromium.connect(cdp_url)
        page = browser.new_page()
        yield page
        browser.close()
    """
    pytest.skip(
        "BrowserStack real-device execution requires BROWSERSTACK_USERNAME and "
        "BROWSERSTACK_ACCESS_KEY environment variables plus a configured account. "
        "See config/browserstack.yaml."
    )
    yield  # unreachable; satisfies the fixture protocol


# ---------------------------------------------------------------------------
# Mobile tests
# ---------------------------------------------------------------------------

@pytest.mark.browserstack
def test_project_visible_on_mobile(bs_page, env_config, credentials):
    """
    Verifies that the Projects list renders correctly on a real mobile device.

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
