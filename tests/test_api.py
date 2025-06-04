import sys
from pathlib import Path
import pytest

# Ensure packages in this repo are importable
root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / 'backend'))

from fastapi.testclient import TestClient
from backend.main import app
from backend.core.project_manager import project_manager
from backend.core.lightrag_manager import lightrag_manager

@pytest.fixture
def client(tmp_path):
    project_manager.projects_base_dir = tmp_path
    lightrag_manager.projects_base_dir = tmp_path
    return TestClient(app)

def test_health(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json()['status'] == 'healthy'

def test_projects(client):
    resp = client.get('/projects')
    assert resp.status_code == 200
    assert resp.json() == []

    proj = client.post('/projects/', json={'name': 'sample'})
    assert proj.status_code == 200
    pid = proj.json()['id']

    resp = client.get('/projects')
    assert any(p['id'] == pid for p in resp.json())

def test_bucket_upload_text(client):
    proj = client.post('/projects/', json={'name': 'proj'}).json()
    client.post(f"/projects/{proj['id']}/buckets/", json={'name': 'bucket'})
    upload = client.post(
        f"/projects/{proj['id']}/buckets/bucket/upload-text",
        data={'filename': 'test.txt', 'content': 'hello'}
    )
    assert upload.status_code == 200
    assert upload.json()['filename'] == 'test.txt'

