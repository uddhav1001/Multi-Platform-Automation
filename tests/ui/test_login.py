import urllib.parse
from playwright.sync_api import expect


def login(page, email, password, base_url):
    page.goto(f'{base_url}/login')
    page.get_by_label('Email').fill(email)
    page.get_by_label('Password').fill(password)
    page.get_by_role('button', name='Log in').click()
    # In the real app, probe for the optional 2FA field here.
    page.wait_for_url(f'{base_url}/dashboard', timeout=15000)


def test_user_login(page, credentials, env_config):
    login(page, credentials['admin']['email'], credentials['admin']['password'], env_config['base_url'])
    expect(page).to_have_url(f"{env_config['base_url']}/dashboard")
    expect(page.locator('.welcome-message')).to_be_visible(timeout=10000)


def test_multi_tenant_access(page, credentials, env_config):
    login(
        page,
        credentials['tenant_user']['email'],
        credentials['tenant_user']['password'],
        env_config['base_url']
    )

    # Navigate to projects with the seed project name as a search filter.
    # The Flask app filters via GET ?search=, so we use URL navigation directly.
    seed_project = 'Company2 Demo Project'
    params = urllib.parse.urlencode({'search': seed_project})
    page.goto(f"{env_config['base_url']}/projects?{params}")

    expect(page).to_have_url(
        f"{env_config['base_url']}/projects?{params}"
    )

    expect(
        page.get_by_role('heading', name=seed_project)
    ).to_be_visible(timeout=10000)