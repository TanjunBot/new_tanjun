"""Unit tests for botstatus-api microservice."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

# Add botstatus-api directory to sys.path for testing
_botstatus_dir = str(Path(__file__).resolve().parent.parent.parent.parent / "botstatus-api")
if _botstatus_dir not in sys.path:
    sys.path.insert(0, _botstatus_dir)

import app as botstatus_module
from app import StatusManager, app, settings


@pytest.fixture
def client(tmp_path):
    state_file = str(tmp_path / "state.json")
    botstatus_module.manager = StatusManager(state_file, timeout_seconds=90)
    settings.state_file = state_file
    settings.api_key = ""
    with TestClient(app) as test_client:
        yield test_client


def test_health_check_initially(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "botstatus-api"


def test_heartbeat_and_status(client):
    payload = {
        "id": "1234567890",
        "status": "alive",
        "latency": 0.045,
        "guild_count": 50,
        "version": "1.2.145",
    }
    post_resp = client.post("/api/status", json=payload)
    assert post_resp.status_code == 200
    assert post_resp.json()["status"] == "ok"
    assert post_resp.json()["bot"]["latency_ms"] == 45
    assert post_resp.json()["bot"]["status"] == "online"

    # Query status
    status_resp = client.get("/status")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["status"] == "online"
    assert data["total_bots"] == 1
    assert data["online_bots"] == 1
    assert data["bots"][0]["id"] == "1234567890"

    # Query single bot
    single_resp = client.get("/status/1234567890")
    assert single_resp.status_code == 200
    assert single_resp.json()["id"] == "1234567890"


def test_badge_endpoint(client):
    payload = {
        "id": "832297321793323028",
        "status": "alive",
        "latency": "0.020",
    }
    client.post("/", json=payload)

    badge_resp = client.get("/badge")
    assert badge_resp.status_code == 200
    badge_data = badge_resp.json()
    assert badge_data["color"] == "brightgreen"
    assert "20ms" in badge_data["message"]


def test_metrics_endpoint(client):
    payload = {
        "id": "1234567890",
        "status": "alive",
        "latency": 0.050,
        "guild_count": 10,
    }
    client.post("/", json=payload)

    metrics_resp = client.get("/metrics")
    assert metrics_resp.status_code == 200
    text = metrics_resp.text
    assert 'bot_online{bot_id="1234567890"} 1' in text
    assert 'bot_latency_ms{bot_id="1234567890"} 50' in text
    assert 'bot_guild_count{bot_id="1234567890"} 10' in text


def test_api_key_auth(client):
    settings.api_key = "supersecret"
    payload = {"id": "1", "status": "alive"}

    unauth_resp = client.post("/", json=payload)
    assert unauth_resp.status_code == 401

    auth_resp = client.post("/", json=payload, headers={"Authorization": "Bearer supersecret"})
    assert auth_resp.status_code == 200
