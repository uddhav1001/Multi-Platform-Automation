from .base_client import BaseAPIClient

class ProjectClient(BaseAPIClient):
    def create(self, name, description='Created by automated integration test'):
        return self.request('POST','/projects',json={'name':name,'description':description,'team_members':[]})
    def delete(self, project_id): return self.request('DELETE',f'/projects/{project_id}')
