from src.api.project_client import ProjectClient
from src.utils.data_generator import unique_project_name

def test_create_project_api(api_token, env_config):
    client=ProjectClient(env_config['api_base'],api_token,'company1')
    name=unique_project_name(); r=client.create(name)
    assert r.status_code in (200,201)
    data=r.json(); assert data['id']; assert data['name']==name; assert data['status']=='active'
    cleanup=client.delete(data['id']); assert cleanup.status_code in (200,204)
