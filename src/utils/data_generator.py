import uuid

def unique_project_name(): return f'QA Test Project {uuid.uuid4().hex[:8]}'
