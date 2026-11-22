# Бесплатный деплой на Oracle Cloud (Always Free)

Бот работает на маленьком сервере 24/7, база хранится на его диске, HTTPS получается автоматически и бесплатно (Caddy + поддомен DuckDNS).

**Перед началом:** остановите локальный бот и туннель на своём компьютере. Два запущенных экземпляра одного бота конфликтуют (ошибка `terminated by other getUpdates request`).

## 1. Аккаунт Oracle

1. Откройте https://www.oracle.com/cloud/free/ и зарегистрируйтесь. Без VPN, имя и адрес указывайте как в банке.
2. **Домашний регион выбрать можно один раз, сменить нельзя.** Берите регион, где обычно есть свободные ARM-серверы (например, Frankfurt).
3. Карта нужна для проверки личности: Oracle временно блокирует около 1 доллара и потом возвращает. **На карте на момент регистрации должно быть 1–2 доллара**, иначе проверка может не пройти. Принимаются только физические карты, виртуальные и предоплаченные отклоняются.
4. Никогда не нажимайте **Upgrade** и создавайте только ресурсы с пометкой **Always Free-eligible**. Тогда платить не придётся. Для надёжности включите бюджетное оповещение на 1 доллар (Billing → Budgets).

## 2. Сервер

Menu → Compute → Instances → **Create instance**:
- Image: **Ubuntu 24.04** (или 22.04)
- Shape: **VM.Standard.A1.Flex**, 1 OCPU и 6 GB (для бота этого с запасом). Если пишет *Out of capacity*, попробуйте позже или выберите **VM.Standard.E2.1.Micro**: ей хватает.
- SSH keys: **Generate a key pair** и скачайте приватный ключ (например, в `C:\keys\oracle.key`)
- Убедитесь, что у сервера есть публичный IP, и запишите его.

## 3. Открыть порты в облаке

Networking → Virtual cloud networks → ваша сеть → Security Lists → Default → **Add Ingress Rules** (два правила):
- Source CIDR `0.0.0.0/0`, IP Protocol TCP, Destination Port `80`
- Source CIDR `0.0.0.0/0`, IP Protocol TCP, Destination Port `443`

## 4. Бесплатный адрес

1. https://www.duckdns.org: войдите через Google или GitHub.
2. Придумайте поддомен (например, `myf1bot`), впишите публичный IP сервера в поле *current ip*, нажмите **update**.
3. Ваш адрес: `myf1bot.duckdns.org`.

## 5. Подключение и установка (PowerShell)

Если ключ не принимается (*UNPROTECTED PRIVATE KEY FILE*):
```
icacls C:\keys\oracle.key /inheritance:r
icacls C:\keys\oracle.key /grant:r "$($env:USERNAME):R"
```
Загрузите архив и зайдите на сервер (`IP` — адрес сервера):
```
scp -i C:\keys\oracle.key f1bot_v6.zip ubuntu@IP:~/
ssh -i C:\keys\oracle.key ubuntu@IP
```
Уже на сервере:
```
unzip f1bot_v6.zip && cd f1bot
bash deploy/setup_server.sh
exit
```
Подключитесь по `ssh` ещё раз (нужно, чтобы применилась группа docker).

## 6. Настройка и запуск

```
cd f1bot
cp .env.example .env
nano .env
```
Заполните три строки (сохранить: `Ctrl+O`, `Enter`, выйти: `Ctrl+X`):
```
BOT_TOKEN=токен_из_BotFather
WEBAPP_URL=https://myf1bot.duckdns.org
DOMAIN=myf1bot.duckdns.org
```
Запуск:
```
docker compose up -d --build
docker compose logs -f bot
```
В логе должна появиться строка «Мини-приложение слушает». Выход из логов: `Ctrl+C` (бот продолжит работать).

## 7. Проверка

- Откройте `https://myf1bot.duckdns.org/healthz`, должно быть `{"ok": true}`.
- В Telegram: `/start`, затем «Открыть приложение».

## Обновление и бэкап

- Обновление: загрузите новый архив, `unzip -o f1bot_v6.zip`, затем `cd f1bot && docker compose up -d --build`. Папка `data/` с базой сохранится.
- Бэкап базы: скопируйте `~/f1bot/data/f1bot.sqlite3` к себе (`scp`).
- Логи: `docker compose logs --tail 100 bot`. Перезапуск: `docker compose restart bot`.

## Если что-то не работает

- **Сертификат не выдаётся** (`docker compose logs caddy`): порты 80/443 закрыты. Проверьте правила в Security List (шаг 3) и что `setup_server.sh` отработал. Также проверьте, что поддомен указывает на правильный IP.
- **Кнопки «Открыть приложение» нет**: `WEBAPP_URL` пустой или не начинается с `https://`.
- **Out of capacity при создании сервера**: попробуйте позже, другой Availability Domain или шейп E2.1.Micro.
