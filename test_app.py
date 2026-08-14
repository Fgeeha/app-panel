"""Self-check: python test_app.py"""

import os
import tempfile


def with_config(content: str | None):
    """Point the app at a temp config (or a nonexistent path) and reload it."""
    import app as app_module

    if content is None:
        app_module.CONFIG_PATH = "/nonexistent/apps.yaml"
        return app_module

    fd, path = tempfile.mkstemp(suffix=".yaml")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    app_module.CONFIG_PATH = path
    return app_module


def main() -> None:
    m = with_config(None)
    assert m.load_apps() == [], "missing config must yield empty list"

    m = with_config("- name: A\n  url: http://a\n- name: B\n  url: http://b\n")
    assert len(m.load_apps()) == 2

    m = with_config("- name: A\n  url: http://a\n- name: NoUrl\n- 42\n")
    apps = m.load_apps()
    assert len(apps) == 1 and apps[0]["name"] == "A", "invalid entries must be skipped"

    m = with_config("a: [unclosed\n")
    assert m.load_apps() == [], "broken YAML must yield empty list"

    m = with_config("name: not-a-list\n")
    assert m.load_apps() == [], "non-list config must yield empty list"

    m = with_config("- name: Grafana\n  url: http://g\n  description: Мониторинг\n")
    client = m.app.test_client()
    body = client.get("/").get_data(as_text=True)
    assert client.get("/").status_code == 200
    assert "Grafana" in body and "Мониторинг" in body
    assert client.get("/healthz").get_json() == {"status": "ok", "apps": 1}

    m = with_config(None)
    assert m.app.test_client().get("/").status_code == 200, "empty panel, not a 500"
    assert m.app.test_client().get("/healthz").get_json()["status"] == "degraded"

    print("OK")


if __name__ == "__main__":
    main()
