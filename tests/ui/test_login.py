from playwright.sync_api import expect

def _appears(locator, timeout_ms):
    try: locator.wait_for(state='visible', timeout=timeout_ms); return True
    except Exception: return False

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

    page.get_by_role('link', name='Projects').click()

    expect(page).to_have_url(
        f"{env_config['base_url']}/projects"
    )

    expect(
        page.get_by_role('heading', name='Company2 Demo Project')
    ).to_be_visible(timeout=10000)