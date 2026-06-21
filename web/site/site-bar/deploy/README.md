# Деплой site-bar (виджет-гид сайта)

Бэкенд — FastAPI-прокси к LLM (**GigaChat-2-Max** → fallback **OpenRouter/DeepSeek**).
Фронт — статический виджет в `site/assets/site-bar/`, подключён в `templates/base.html`.

Сервер: **144.124.250.77** (общий с TG-ботом), домен **tropa.fmin.xyz** (HTTPS уже выпущен).
Архитектура: nginx раздаёт статику сайта и проксирует `/api/` → `127.0.0.1:8000` (uvicorn).

## 1. Код бэкенда на сервер
```bash
rsync -av --exclude .venv --exclude .env site-bar/server/ root@144.124.250.77:/opt/tropa-bot/server/
```

## 2. Окружение и зависимости (на сервере)
```bash
cd /opt/tropa-bot/server
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# .env скопировать ОТДЕЛЬНО (в git его нет!) и дописать путь к RU CA:
#   GIGACHAT_CA=/usr/local/share/ca-certificates/russian_trusted_root_ca.crt
# Russian Trusted Root CA (для верификации TLS GigaChat):
curl -k -o /usr/local/share/ca-certificates/russian_trusted_root_ca.crt \
  https://gu-st.ru/content/Other/doc/russian_trusted_root_ca.cer
update-ca-certificates
```

## 3. systemd-сервис
```bash
cp tropa-bot-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now tropa-bot-api
systemctl status tropa-bot-api --no-pager
curl -s http://127.0.0.1:8000/api/health    # {"ok":true,...}
```

## 4. nginx
Вставить содержимое `nginx-api.snippet` в server-блок tropa.fmin.xyz, затем:
```bash
nginx -t && systemctl reload nginx
curl -s https://tropa.fmin.xyz/api/health    # снаружи через HTTPS
```

## 5. Статика сайта с виджетом
Пересобрать сайт (`python3 build.py`) и выложить `site/` в webroot nginx
(виджет уже в `base.html` — отдельных действий не нужно, только заново задеплоить статику).

## Проверка
Открыть любой сюжет → кнопка «Чем помочь?» справа-снизу → задать вопрос → ответ от гида.
