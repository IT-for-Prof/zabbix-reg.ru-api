# REG.RU Zabbix Template

Шаблон мониторинга REG.RU API для Zabbix 7.0 с автообнаружением услуг и контролем сроков истечения.

**Версия:** 2.1.0
**Автор:** [Konstantin Tyutyunnik](https://itforprof.com)
**Лицензия:** MIT

## Возможности

- **LLD автообнаружение** всех типов услуг (домены, VPS, хостинг, SSL и др.)
- **4-уровневые алерты** истечения услуг:
  - Information: ≤30 дней
  - Warning: ≤14 дней
  - High: ≤7 дней
  - Disaster: просрочено
- **Мониторинг баланса** с алертом низкого баланса
- **Неоплаченные счета** — количество и сумма
- **API ошибки** с текстом ошибки в алерте
- **Nodata триггеры** для всех master items
- **Dashboard** с виджетами проблем и таблицей услуг

## Требования

- Zabbix Server 7.0+
- Аккаунт REG.RU с доступом к API
- API пароль (настраивается в [личном кабинете](https://b2b.reg.ru/user/account/#/settings/api/))

## Установка

### 1. Импорт шаблона

```bash
# Через веб-интерфейс
Configuration → Templates → Import → выбрать zabbix-reg.ru-api_template.yaml

# Или через API
python3 import_template.py
```

### 2. Создание хоста

1. Configuration → Hosts → Create host
2. Host name: `reg.ru` (или любое)
3. Groups: выбрать группу
4. Templates: добавить `REG.RU`

### 3. Настройка макросов

На уровне хоста задать:

| Макрос | Значение | Описание |
|--------|----------|----------|
| `{$RR_USERNAME}` | `your_login` | Логин REG.RU |
| `{$RR_PASSWORD}` | `api_password` | API пароль (тип: Secret) |

## Макросы шаблона

| Макрос | По умолчанию | Описание |
|--------|--------------|----------|
| `{$RR_USERNAME}` | `user@mail.arpa` | Логин аккаунта REG.RU |
| `{$RR_PASSWORD}` | — | API пароль (Secret) |
| `{$RR_BALANCE_MINIMAL}` | `200` | Порог низкого баланса (RUB) |
| `{$RR_EXPIRE_INFO}` | `30` | Дней до истечения — Information |
| `{$RR_EXPIRE_WARNING}` | `14` | Дней до истечения — Warning |
| `{$RR_EXPIRE_HIGH}` | `7` | Дней до истечения — High |
| `{$RR_EXCLUDE_TYPES}` | `^(srv_parking)$` | Regex исключения типов услуг |
| `{$RR_API_TIMEOUT}` | `30s` | Таймаут HTTP запросов |
| `{$RR_UPDATE_INTERVAL}` | `1h` | Интервал опроса API |

## Мониторинг

### Items

**Статические (12):**
- `rr-api-user-get_balance` — raw ответ API баланса
- `rr-prepay` — баланс (prepay)
- `rr-credit` — кредит
- `rr-currency` — валюта
- `rr-api-status` — статус API (success/error)
- `rr-api-error-code` — код ошибки API
- `rr-api-error-text` — текст ошибки API
- `rr.api.services.list` — raw список услуг
- `rr.services.total` — всего услуг
- `rr.api.bills.unpaid` — raw неоплаченные счета
- `rr.bills.unpaid.count` — количество неоплаченных счетов
- `rr.bills.unpaid.sum` — сумма неоплаченных счетов

**LLD Item Prototypes (4):**
- `rr.service.type[{#SERVICE_ID}]` — тип услуги
- `rr.service.state[{#SERVICE_ID}]` — статус (A/D/S/W)
- `rr.service.expire_date[{#SERVICE_ID}]` — дата истечения
- `rr.service.days_left[{#SERVICE_ID}]` — дней до истечения

### Triggers

**Статические (6):**
- `[High]` API error (4 consecutive failures)
- `[High]` Low balance
- `[Warning]` Unpaid bills
- `[Average]` No data from balance/bills/services API

**LLD Trigger Prototypes (4):**
- `[Disaster]` Service EXPIRED
- `[High]` Service expires ≤7 days
- `[Warning]` Service expires ≤14 days
- `[Information]` Service expires ≤30 days

### Dashboard

**REG.RU Overview** — 6 виджетов:
1. Баланс
2. API Статус
3. Всего услуг
4. Проблемы (фильтр по tag service=reg.ru)
5. Услуги: сроки истечения (таблица)
6. Тренд баланса (график)

## Особенности

### VPS и услуги без срока истечения

Услуги с почасовой/ежедневной оплатой (VPS) не имеют даты истечения. Шаблон корректно обрабатывает такие случаи — `days_left = 99999`, триггеры не срабатывают.

### Исключение типов услуг

Через макрос `{$RR_EXCLUDE_TYPES}` можно исключить типы услуг из мониторинга:

```
# Только parking (по умолчанию)
^(srv_parking)$

# Parking и хостинг
^(srv_parking|srv_hosting)$

# Все srv_* сервисы
^srv_

# Ничего не исключать
^$
```

### Ограничения API REG.RU

- **Autorenew статус** — недоступен через `service/get_list`, требует отдельного вызова для каждой услуги
- **SSL сертификаты** — нет методов мониторинга
- **Детали VPS/хостинга** — ограниченная информация

## Структура файлов

```
├── zabbix-reg.ru-api_template.yaml  # Шаблон Zabbix
├── import_template.py               # Скрипт импорта через API
├── README.md                        # Документация
├── CONTINUITY.md                    # Changelog
└── docs/
    └── plans/                       # Проектная документация
```

## Changelog

См. [CONTINUITY.md](CONTINUITY.md)

## Поддержка

- Issues: [GitHub](https://github.com/...)
- Сайт: [itforprof.com](https://itforprof.com)

---

**© 2025-2026 [Konstantin Tyutyunnik](https://itforprof.com)**
