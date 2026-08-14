# app-panel

Простая стартовая страница на Flask со списком ссылок на локальные приложения.

- Конфигурация `apps.yaml` перечитывается при каждом запросе — изменения вступают в силу без перезапуска.
- Отсутствующий или сломанный `apps.yaml` не роняет страницу: показывается пустой список, причина пишется в лог.
- Тёмная тема подхватывается из настроек системы, вёрстка адаптивная.

## Быстрый старт

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp apps.yaml.example apps.yaml
.venv/bin/python app.py
```

Панель доступна на `http://localhost:8082`.

## Конфигурация `apps.yaml`

Список приложений. Обязательные поля — `name` и `url`, `description` необязательно.
Записи без `name` или `url` пропускаются с предупреждением в логе.

```yaml
- name: Grafana
  url: http://192.168.1.10:3000
  description: Мониторинг и дашборды

- name: Router
  url: http://192.168.1.1
```

Файл `apps.yaml` не хранится в репозитории — за образец берите `apps.yaml.example`.

## Переменные окружения

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `APPS_YAML_PATH` | `apps.yaml` | Путь к файлу конфигурации |
| `PORT` | `8082` | Порт HTTP-сервера |
| `PANEL_TITLE` | `Панель приложений` | Заголовок страницы |

## Эндпоинты

| Маршрут | Описание |
|---|---|
| `/` | Страница со списком приложений |
| `/healthz` | JSON вида `{"status": "ok", "apps": 3}`; `degraded`, если список пуст |

## Запуск через systemd

```bash
sudo cp systemd/app-panel.service /etc/systemd/system/
sudo sed -i "s/USER/$USER/g" /etc/systemd/system/app-panel.service
sudo systemctl daemon-reload
sudo systemctl enable --now app-panel
```

## Проверка

```bash
.venv/bin/python test_app.py
```

Скрипт проверяет разбор конфигурации, обработку ошибок и оба маршрута; при успехе выводит `OK`.
