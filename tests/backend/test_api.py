import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_upload_video():
    response = client.post("/api/upload", files={"file": ("test_video.mp4", open("tests/test_video.mp4", "rb"))})
    assert response.status_code == 200
    assert "video_url" in response.json()

def test_object_detection():
    response = client.post("/api/detect", json={"video_url": "http://example.com/test_video.mp4", "prompt": "Shark."})
    assert response.status_code == 200
    assert "output_video_url" in response.json()

def test_invalid_video_upload():
    response = client.post("/api/upload", files={"file": ("invalid_file.txt", open("tests/invalid_file.txt", "rb"))})
    assert response.status_code == 400
    assert "detail" in response.json()

def test_empty_prompt_detection():
    response = client.post("/api/detect", json={"video_url": "http://example.com/test_video.mp4", "prompt": ""})
    assert response.status_code == 400
    assert "detail" in response.json()