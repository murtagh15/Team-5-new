from ege_calculator.web.app import create_app


def test_health():
    app = create_app()
    client = app.test_client()
    r = client.get("/api/universities")
    assert r.status_code == 200
