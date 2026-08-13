import time, requests

class BaseAPIClient:
    def __init__(self, base_url, token, tenant_id, retries=2):
        self.base_url=base_url.rstrip('/'); self.token=token; self.tenant_id=tenant_id; self.retries=retries
    @property
    def headers(self): return {'Authorization':f'Bearer {self.token}','X-Tenant-ID':self.tenant_id}
    def request(self, method, path, **kwargs):
        kwargs.setdefault('timeout',10); kwargs.setdefault('headers', self.headers)
        last=None
        for attempt in range(self.retries+1):
            try:
                r=requests.request(method, self.base_url+path, **kwargs)
                if r.status_code < 500: return r
                last=r
            except requests.RequestException as e: last=e
            if attempt < self.retries: time.sleep(0.25*(2**attempt))
        if isinstance(last, Exception): raise last
        return last
