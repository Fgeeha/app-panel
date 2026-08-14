import logging
import os

import yaml
from flask import Flask, render_template_string

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

CONFIG_PATH = os.environ.get("APPS_YAML_PATH", "apps.yaml")
PORT = int(os.environ.get("PORT", "8082"))
TITLE = os.environ.get("PANEL_TITLE", "Панель приложений")


def load_apps() -> list[dict]:
    """Read the YAML configuration on demand.

    Returns an empty list instead of raising, so a missing or broken config
    shows an empty panel rather than a 500 page.
    """
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning("Config not found: %s", CONFIG_PATH)
        return []
    except yaml.YAMLError as e:
        logger.error("Invalid YAML in %s: %s", CONFIG_PATH, e)
        return []

    if not isinstance(data, list):
        logger.error("Config %s must be a list of apps, got %s", CONFIG_PATH, type(data).__name__)
        return []

    apps = []
    for item in data:
        if isinstance(item, dict) and item.get("name") and item.get("url"):
            apps.append(item)
        else:
            logger.warning("Skipping entry without name/url: %r", item)
    return apps


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title }}</title>
    <style>
        :root {
            --bg: #f5f6f8; --card: #ffffff; --fg: #1c1e21;
            --muted: #6b7280; --accent: #0066cc; --border: #e2e5e9;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #16181c; --card: #1f2226; --fg: #e6e8ea;
                --muted: #9aa1a9; --accent: #6aa9ff; --border: #2c3036;
            }
        }
        * { box-sizing: border-box; }
        body {
            margin: 0; padding: 2rem 1rem;
            font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
            background: var(--bg); color: var(--fg);
        }
        main { max-width: 640px; margin: 0 auto; }
        h1 { margin: 0 0 .25rem; font-size: 1.6rem; }
        p.sub { margin: 0 0 1.5rem; color: var(--muted); }
        ul { list-style: none; padding: 0; margin: 0;
             display: grid; gap: .75rem; }
        li a {
            display: block; padding: .9rem 1.1rem;
            background: var(--card); border: 1px solid var(--border);
            border-radius: 10px; color: var(--accent);
            font-size: 1.05rem; text-decoration: none;
        }
        li a:hover { border-color: var(--accent); }
        li a .desc { display: block; margin-top: .2rem;
                     font-size: .875rem; color: var(--muted); }
        .empty { padding: 1.1rem; background: var(--card);
                 border: 1px dashed var(--border); border-radius: 10px;
                 color: var(--muted); }
        code { font-family: ui-monospace, monospace; }
    </style>
</head>
<body>
<main>
    <h1>{{ title }}</h1>
    <p class="sub">Выберите приложение:</p>
    {% if apps %}
    <ul>
    {% for app in apps %}
        <li>
            <a href="{{ app.url }}" target="_blank" rel="noopener">
                {{ app.name }}
                {% if app.description %}<span class="desc">{{ app.description }}</span>{% endif %}
            </a>
        </li>
    {% endfor %}
    </ul>
    {% else %}
    <div class="empty">Список пуст. Проверьте файл <code>{{ config_path }}</code>.</div>
    {% endif %}
</main>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE, apps=load_apps(), title=TITLE, config_path=CONFIG_PATH
    )


@app.route("/healthz")
def healthz():
    apps = load_apps()
    return {"status": "ok" if apps else "degraded", "apps": len(apps)}


if __name__ == "__main__":
    logger.info("Starting on port %s, config %s", PORT, CONFIG_PATH)
    app.run(host="0.0.0.0", port=PORT)
