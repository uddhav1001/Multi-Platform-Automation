import os, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_environment(name=None):
    name = name or os.getenv('TEST_ENV','dev')
    data = yaml.safe_load((ROOT/'config'/'environments.yaml').read_text())
    if name not in data: raise ValueError(f'Unknown environment: {name}')
    return data[name]

def load_tenants():
    return yaml.safe_load((ROOT/'config'/'tenants.yaml').read_text())
