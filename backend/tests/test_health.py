from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_v1_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_ready_endpoint(monkeypatch):
    # Mock redis to avoid dependency on actual redis container in simple API tests
    class MockRedis:
        def ping(self):
            return True
            
    import app.api.health as health_api
    from app.database import get_db
    monkeypatch.setattr(health_api.redis, "from_url", lambda url: MockRedis())
    
    app.dependency_overrides[get_db] = lambda: None # Override db so we don't hit the closed connection from test pollution
    
    # We need to mock the db check inside health.py or just let the test pass if the DB part fails?
    # Wait, if we override get_db with None, db.execute will raise AttributeError which gets caught.
    # We should override it with a Mock DB session.
    class MockDB:
        def execute(self, *args, **kwargs):
            return True
            
    app.dependency_overrides[get_db] = lambda: MockDB()
    
    try:
        response = client.get("/api/v1/ready")
        assert response.status_code == 200, response.json()
        assert response.json()["status"] == "ok"
        assert "database" in response.json()["components"]
        assert "redis" in response.json()["components"]
    finally:
        app.dependency_overrides.clear()
