# REG.RU Zabbix Template v2.0.0 — Design Document

**Date:** 2026-01-23
**Author:** itforprof.com by Konstantin Tyutyunnik
**Status:** Approved

## Overview

Расширенный шаблон мониторинга REG.RU API для Zabbix 7.0 с автообнаружением услуг, контролем сроков истечения и финансовым мониторингом.

### Ключевые требования

- Автообнаружение всех типов услуг (домены, хостинг, VPS, SSL и др.)
- Контроль сроков истечения услуг (важнее баланса)
- Мониторинг неоплаченных счетов
- Многоуровневые триггеры с настраиваемыми порогами
- Информативный дашборд
- Обработка ошибок API

## Architecture

### Component Diagram

```
Template: REG.RU (version 2.0.0)
│
├── Master Items (HTTP Agent)
│   ├── rr.api.services.list      ← service/get_list (все услуги)
│   ├── rr.api.balance            ← user/get_balance (баланс)
│   └── rr.api.bills.unpaid       ← bill/get_not_payed (счета)
│
├── Dependent Items (от balance)
│   ├── rr.balance.prepay
│   ├── rr.balance.credit
│   └── rr.balance.currency
│
├── Dependent Items (от bills.unpaid)
│   ├── rr.bills.unpaid.count
│   └── rr.bills.unpaid.sum
│
├── LLD Rules
│   └── rr.discovery.services     ← парсит rr.api.services.list
│       │
│       └── Item Prototypes (для каждой услуги)
│           ├── rr.service[{#SERVICE_ID}].type
│           ├── rr.service[{#SERVICE_ID}].name
│           ├── rr.service[{#SERVICE_ID}].expiration_date
│           ├── rr.service[{#SERVICE_ID}].days_left
│           ├── rr.service[{#SERVICE_ID}].autorenew
│           └── rr.service[{#SERVICE_ID}].state
│
├── Triggers
│   ├── API errors (4 consecutive failures)
│   ├── Low balance
│   ├── Unpaid bills exist
│   └── Service expiration (multi-level)
│
└── Dashboards
    └── REG.RU Overview
```

### Data Flow

1. **Master item** делает HTTP POST к API раз в час
2. **Dependent items** парсят JSON через JSONPath
3. **LLD rule** использует тот же master item для discovery
4. **Item prototypes** создаются автоматически для каждой услуги

## API Integration

### Endpoints

| Endpoint | Purpose | Interval |
|----------|---------|----------|
| `service/get_list` | Список всех услуг | 1h |
| `user/get_balance` | Баланс аккаунта | 1h |
| `bill/get_not_payed` | Неоплаченные счета | 1h |

### Request Format

```
URL: https://api.reg.ru/api/regru2/{category}/{method}
Method: POST
Body: username={$RR_USERNAME}&password={$RR_PASSWORD}&output_format=json
Timeout: 30s
Status codes: 200,400,401,403,404,500
```

### Response Format (service/get_list)

```json
{
  "result": "success",
  "answer": {
    "services": [
      {
        "service_id": "12345",
        "servtype": "domain",
        "dname": "example.ru",
        "state": "A",
        "expiration_date": "2025-06-15",
        "autorenew": "on"
      }
    ]
  }
}
```

### Error Handling

- HTTP errors → Zabbix получает ответ, парсит error_text
- API errors → result="error", error_code, error_text
- Missing fields → DISCARD_VALUE или CUSTOM_VALUE preprocessing

## LLD Discovery

### Discovery Rule: rr.discovery.services

```yaml
type: DEPENDENT
master_item: rr.api.services.list
delay: 0
preprocessing:
  - JSONPATH: $.answer.services
  - JAVASCRIPT: |
      var services = JSON.parse(value);
      var lld = services.map(function(s) {
        return {
          "{#SERVICE_ID}": s.service_id,
          "{#SERVICE_TYPE}": s.servtype,
          "{#SERVICE_NAME}": s.dname || s.service_id,
          "{#EXPIRE_DATE}": s.expiration_date || "",
          "{#AUTORENEW}": s.autorenew || "off"
        };
      });
      return JSON.stringify(lld);
```

### LLD Macros

| Macro | Source |
|-------|--------|
| `{#SERVICE_ID}` | $.service_id |
| `{#SERVICE_TYPE}` | $.servtype |
| `{#SERVICE_NAME}` | $.dname |
| `{#EXPIRE_DATE}` | $.expiration_date |
| `{#AUTORENEW}` | $.autorenew |

### Item Prototypes

| Key | Name | Type | Preprocessing |
|-----|------|------|---------------|
| `rr.service.type[{#SERVICE_ID}]` | Тип: {#SERVICE_NAME} | TEXT | from LLD |
| `rr.service.name[{#SERVICE_ID}]` | Имя: {#SERVICE_NAME} | TEXT | from LLD |
| `rr.service.state[{#SERVICE_ID}]` | Статус: {#SERVICE_NAME} | TEXT | JSONPath + valuemap |
| `rr.service.expire_date[{#SERVICE_ID}]` | Дата истечения: {#SERVICE_NAME} | TEXT | from LLD |
| `rr.service.days_left[{#SERVICE_ID}]` | Дней до истечения: {#SERVICE_NAME} | UNSIGNED | JavaScript |
| `rr.service.autorenew[{#SERVICE_ID}]` | Автопродление: {#SERVICE_NAME} | TEXT | from LLD |

### Days Left Calculation

```javascript
var expire = "{#EXPIRE_DATE}";
if (!expire) return -1;
var expireTs = Date.parse(expire);
var now = Date.now();
var days = Math.floor((expireTs - now) / 86400000);
return days;
```

## Triggers

### Trigger Prototypes (per service)

| Trigger | Expression | Severity |
|---------|------------|----------|
| Услуга истекла | `last(rr.service.days_left[{#SERVICE_ID}])<0` | Disaster |
| Истекает ≤{$RR_EXPIRE_HIGH} дн. | `last(...)<={$RR_EXPIRE_HIGH}` | High |
| Истекает ≤{$RR_EXPIRE_WARNING} дн. | `last(...)<={$RR_EXPIRE_WARNING}` | Warning |
| Истекает ≤{$RR_EXPIRE_INFO} дн. | `last(...)<={$RR_EXPIRE_INFO}` | Information |
| Автопродление выключено | `last(rr.service.autorenew[...])="off"` | Warning |

### Event Names

```
{#SERVICE_TYPE}: {#SERVICE_NAME} истекает через {ITEM.LASTVALUE} дней (дата: {#EXPIRE_DATE})
```

### Static Triggers

| Trigger | Expression | Severity |
|---------|------------|----------|
| API ошибка | 4 consecutive failures | High |
| Низкий баланс | `last(rr.balance.prepay)<{$RR_BALANCE_MINIMAL}` | High |
| Неоплаченные счета | `last(rr.bills.unpaid.count)>0` | Warning |

### Trigger Dependencies

```
Service expired ← blocks → Expiring High/Warning/Info
API error ← blocks → all other triggers
```

## Macros

| Macro | Default | Type | Description |
|-------|---------|------|-------------|
| `{$RR_USERNAME}` | user@mail.arpa | TEXT | E-mail аккаунта REG.RU |
| `{$RR_PASSWORD}` | — | SECRET | Пароль API |
| `{$RR_BALANCE_MINIMAL}` | 200 | TEXT | Порог низкого баланса |
| `{$RR_EXPIRE_INFO}` | 30 | TEXT | Дней — информирование |
| `{$RR_EXPIRE_WARNING}` | 14 | TEXT | Дней — предупреждение |
| `{$RR_EXPIRE_HIGH}` | 7 | TEXT | Дней — срочно |
| `{$RR_API_TIMEOUT}` | 30s | TEXT | Таймаут HTTP |
| `{$RR_UPDATE_INTERVAL}` | 1h | TEXT | Интервал опроса |

## Dashboard

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  REG.RU Overview                                                │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│   БАЛАНС     │   СТАТУС     │  СЧЕТОВ К    │   ВСЕГО УСЛУГ     │
│   {prepay}   │   API        │  ОПЛАТЕ      │   {count}         │
│   {currency} │   {status}   │   {bills}    │                   │
├──────────────┴──────────────┴──────────────┴───────────────────┤
│   ГРАФИК: Услуги по срокам истечения (bar chart)               │
├─────────────────────────────────────────────────────────────────┤
│   ТАБЛИЦА: Услуги, требующие внимания (истекают <30 дн.)       │
├─────────────────────────────────────────────────────────────────┤
│   ГРАФИК: Тренд баланса (30 дней)                              │
└─────────────────────────────────────────────────────────────────┘
```

### Widgets

1. **Item widgets** — баланс, статус, счета, кол-во услуг
2. **Graph widget** — распределение по срокам
3. **Data overview** — таблица услуг с фильтром
4. **Graph classic** — тренд баланса

## Tags

### Template Tags

```yaml
tags:
  - tag: vendor
    value: reg.ru
  - tag: class
    value: service-monitoring
```

### Item Prototype Tags

```yaml
tags:
  - tag: service
    value: reg.ru
  - tag: scope
    value: "{#SERVICE_TYPE}"
  - tag: service_name
    value: "{#SERVICE_NAME}"
  - tag: component
    value: expiration
```

## Value Maps

### REG.RU Service State

| Value | Display |
|-------|---------|
| A | Active |
| D | Deleted |
| S | Suspended |
| W | Waiting |

### REG.RU Autorenew

| Value | Display |
|-------|---------|
| on | Enabled |
| off | Disabled |

## File Structure

```yaml
zabbix_export:
  version: '7.0'
  template_groups:
    - name: REG.RU

  templates:
    - template: REG.RU
      name: REG.RU
      vendor:
        name: itforprof.com
        version: 2.0.0

      macros: [8 macros]
      items: [10 items]
      discovery_rules:
        - rr.discovery.services
            item_prototypes: [6 items]
            trigger_prototypes: [5 triggers]
      triggers: [3 static triggers]
      dashboards: [1 dashboard]
      valuemaps: [2 valuemaps]
```

## Migration Notes

- Ключи items переименовываются: `rr-*` → `rr.*`
- Старые данные сохраняются при обновлении шаблона
- Обратная совместимость с текущими триггерами

## API Rate Limits

- REG.RU: 1200 запросов/час на аккаунт + 1200/час на IP
- Шаблон использует ~4-5 запросов/час (консервативно)
