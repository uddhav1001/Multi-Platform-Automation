import os, pytest
from src.config_loader import load_environment, load_tenants

@pytest.fixture(scope='session')
def env_config(): return load_environment()

@pytest.fixture(scope='session')
def tenants(): return load_tenants()

@pytest.fixture
def credentials():
    return {
        'admin': {
            'email': os.getenv('TEST_ADMIN_EMAIL','admin@company1.com'),
            'password': os.getenv('TEST_ADMIN_PASSWORD','AdminPass123')},
        'tenant_user': {
            'email': os.getenv('TEST_TENANT_USER_EMAIL','tenant@company2.com'),
            'password': os.getenv('TEST_TENANT_USER_PASSWORD','TenantPass123')},
    }

@pytest.fixture
def api_token():
    return os.getenv('WORKFLOWPRO_API_TOKEN','local-demo-token')
