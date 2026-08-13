import pytest
from src.api.project_client import ProjectClient
from src.utils.data_generator import unique_project_name

@pytest.fixture
def created_project(api_token, env_config):
    client=ProjectClient(env_config['api_base'],api_token,'company1')
    name=unique_project_name(); r=client.create(name)
    assert r.status_code in (200,201), r.text
    project=r.json()
    assert project['status']=='active'
    yield project, name
    client.delete(project['id'])
