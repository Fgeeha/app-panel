from flask import Flask, render_template_string
import yaml
import os

app = Flask(__name__)

CONFIG_PATH = os.environ.get("APPS_YAML_PATH", "apps.yaml")


def load_apps():
    """Read the YAML configuration on demand."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Панель приложений</title>
    <style>
        body { font-family: sans-serif; padding: 2em; }
        h1 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 1em 0; }
        a { font-size: 1.2em; color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Добро пожаловать</h1>
    <p>Выберите приложение:</p>
    <ul>
    {% for app in apps %}
        <li><a href="{{ app.url }}" target="_blank">{{ app.name }}</a></li>
    {% endfor %}
    </ul>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, apps=load_apps())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
