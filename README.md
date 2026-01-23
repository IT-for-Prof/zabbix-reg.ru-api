# REG.RU Zabbix Templates

Шаблоны мониторинга REG.RU API для Zabbix 7.0 с автообнаружением услуг и ресурсов.

**Автор:** [Konstantin Tyutyunnik](https://itforprof.com)
**Лицензия:** MIT

---

## Шаблоны

| Шаблон | Версия | API | Назначение |
|--------|--------|-----|------------|
| **REG.RU** | 2.1.2 | api.reg.ru | Услуги REG.RU (домены, SSL, хостинг и др.) |
| **REG.RU CLOUD** | 1.1.0 | api.cloudvps.reg.ru | CloudVPS серверы, баланс, снапшоты |

> **Важно:** Шаблоны используют разные API с разной аутентификацией. Если у вас есть и услуги REG.RU, и CloudVPS — подключайте оба шаблона.

---

# REG.RU (Основной шаблон)

Мониторинг услуг REG.RU: домены, SSL, хостинг, VPS и другие.

## Возможности

- **LLD автообнаружение** всех типов услуг
- **4-уровневые алерты** истечения услуг (30/14/7/0 дней)
- **Мониторинг баланса** с алертом низкого баланса
- **Неоплаченные счета** — количество и сумма
- **API ошибки** с текстом ошибки в алерте
- **Dashboard** с виджетами проблем и таблицей услуг

## Установка

### 1. Импорт шаблона

```bash
Configuration → Templates → Import → zabbix-reg.ru-api_template.yaml
```

### 2. Настройка макросов хоста

| Макрос | Значение | Описание |
|--------|----------|----------|
| `{$RR_USERNAME}` | `your_login` | Логин REG.RU |
| `{$RR_PASSWORD}` | `api_password` | API пароль (Secret) |

API пароль настраивается в [личном кабинете REG.RU](https://b2b.reg.ru/user/account/#/settings/api/).

## Макросы

| Макрос | По умолчанию | Описание |
|--------|--------------|----------|
| `{$RR_USERNAME}` | `user@mail.arpa` | Логин аккаунта |
| `{$RR_PASSWORD}` | — | API пароль (Secret) |
| `{$RR_BALANCE_MINIMAL}` | `200` | Порог низкого баланса (RUB) |
| `{$RR_EXPIRE_INFO}` | `30` | Дней до истечения — Information |
| `{$RR_EXPIRE_WARNING}` | `14` | Дней до истечения — Warning |
| `{$RR_EXPIRE_HIGH}` | `7` | Дней до истечения — High |
| `{$RR_EXCLUDE_TYPES}` | `^(srv_parking)$` | Regex исключения типов |
| `{$RR_API_TIMEOUT}` | `30s` | Таймаут HTTP запросов |
| `{$RR_UPDATE_INTERVAL}` | `1h` | Интервал опроса API |

## Компоненты

**Items (12):** баланс, кредит, валюта, API статус, ошибки, счета

**LLD Discovery:** автообнаружение всех услуг с 4 item prototypes

**Triggers (10):** API ошибки, низкий баланс, неоплаченные счета, nodata

**Trigger Prototypes (4):** истечение услуг (Disaster/High/Warning/Info)

**Dashboard:** 6 виджетов — баланс, статус, проблемы, таблица услуг, график

---

# REG.RU CLOUD (CloudVPS)

Мониторинг REG.RU CloudVPS: серверы, баланс, снапшоты, IP, VPC.

## Возможности

- **Мониторинг баланса** с каскадными алертами (Warning → High → Disaster)
- **Дни до отключения** с алертами
- **LLD автообнаружение:**
  - VPS серверы (статус, CPU, RAM, диск, IP, регион, стоимость)
  - Снапшоты (размер, дата создания)
  - VPC сети (регион)
- **Инвентаризация ресурсов** — суммарные vCPU, RAM, диск
- **Nodata триггеры** для всех 5 API endpoints
- **Dashboard** с 2 страницами (Overview + Resources)

## Установка

### 1. Импорт шаблона

```bash
Configuration → Templates → Import → zabbix-reg.ru-cloud-api_template.yaml
```

### 2. Настройка макроса хоста

| Макрос | Значение | Описание |
|--------|----------|----------|
| `{$RRC_API_KEY}` | `your_token` | CloudVPS API Bearer токен (Secret) |

API токен получается в [панели CloudVPS](https://cloudvps.reg.ru/).

## Макросы

| Макрос | По умолчанию | Описание |
|--------|--------------|----------|
| `{$RRC_API_KEY}` | — | API Bearer токен (Secret) |
| `{$RRC_API_TIMEOUT}` | `30s` | Таймаут HTTP запросов |
| `{$RRC_UPDATE_INTERVAL}` | `1h` | Интервал опроса (balance, snapshots, ips, vpcs) |
| `{$RRC_UPDATE_INTERVAL_REGLETS}` | `5m` | Интервал опроса VPS статусов |
| `{$RRC_BALANCE_WARNING}` | `500` | Порог баланса — Warning |
| `{$RRC_BALANCE_HIGH}` | `200` | Порог баланса — High |
| `{$RRC_DAYSLEFT_WARNING}` | `7` | Порог дней — Warning |
| `{$RRC_DAYSLEFT_HIGH}` | `3` | Порог дней — High |
| `{$RRC_SNAPSHOTS_MAX}` | `10` | Макс. количество снапшотов |
| `{$RRC_SNAPSHOTS_SIZE_MAX}` | `107374182400` | Макс. размер снапшотов (100GB) |

## Компоненты

### Master Items (5 HTTP Agents)

| Endpoint | Key | Interval |
|----------|-----|----------|
| `/v1/balance_data` | `rrc-api-balance-data` | 1h |
| `/v1/reglets` | `rrc-api-reglets` | 5m |
| `/v1/snapshots` | `rrc-api-snapshots` | 1h |
| `/v1/ips` | `rrc-api-ips` | 1h |
| `/v1/vpcs` | `rrc-api-vpcs` | 1h |

### Dependent Items (18)

**Billing (7):** balance, bonus, days_left, hours_left, monthly_cost, hourly_cost, api_status

**VPS Summary (6):** total, active, stopped, vcpus_total, memory_total, disk_total

**Resources (5):** snapshots_count, snapshots_size, ipv4_count, ipv6_count, vpc_count

### Discovery Rules (3)

| Discovery | Item Prototypes | Trigger Prototypes |
|-----------|-----------------|-------------------|
| VPS Discovery | 11 (status, vcpus, memory, disk, ip, region, prices, backups, image, created) | 3 (not active, backups disabled, backups not configured) |
| Snapshots Discovery | 2 (size, created) | — |
| VPC Discovery | 1 (region) | — |

### Triggers (17)

| Категория | Triggers | Severities |
|-----------|----------|------------|
| **Nodata** | 5 | AVERAGE |
| **Balance** | 4 | DISASTER, HIGH, WARNING, AVERAGE |
| **Days Left** | 3 | DISASTER, HIGH, WARNING |
| **API Status** | 1 | HIGH |
| **VPS** | 2 | WARNING, INFO |
| **Snapshots** | 2 | WARNING |

### Trigger Prototypes (3)

| Trigger | Severity | Описание |
|---------|----------|----------|
| VPS [{#REGLET_NAME}]: Not active | HIGH | VPS не активен |
| VPS [{#REGLET_NAME}]: Backups were disabled | WARNING | Бэкапы были отключены (change detection) |
| VPS [{#REGLET_NAME}]: Backups not configured | INFO | Бэкапы не настроены изначально |

### Dashboard (2 страницы)

**Overview:**
- Баланс, дней осталось
- Всего VPS, активных VPS, месячная стоимость
- Проблемы (фильтр по tag)
- Таблица VPS статусов
- Графики: баланс, дни до отключения

**Resources:**
- Суммарные vCPU, RAM, Disk
- Количество снапшотов, VPC, IP
- Размер снапшотов

---

## Структура файлов

```
├── zabbix-reg.ru-api_template.yaml        # Шаблон REG.RU
├── zabbix-reg.ru-cloud-api_template.yaml  # Шаблон REG.RU CLOUD
├── README.md                               # Документация
└── CONTINUITY.md                           # Changelog
```

## Требования

- Zabbix Server 7.0+
- Для REG.RU: логин + API пароль
- Для CloudVPS: Bearer API токен

## Changelog

См. [CONTINUITY.md](CONTINUITY.md)

## Поддержка

- Сайт: [itforprof.com](https://itforprof.com)

---

**© 2025-2026 [Konstantin Tyutyunnik](https://itforprof.com)**
