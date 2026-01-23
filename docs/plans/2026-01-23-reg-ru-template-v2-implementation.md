# REG.RU Zabbix Template v2.0.0 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Расширить шаблон мониторинга REG.RU с автообнаружением услуг, контролем сроков истечения и финансовым мониторингом.

**Architecture:** Единый шаблон с 3 master HTTP items, LLD для автообнаружения услуг, многоуровневыми триггерами по срокам истечения и информативным дашбордом.

**Tech Stack:** Zabbix 7.0, YAML, JSONPath, JavaScript preprocessing

**Design Document:** `docs/plans/2026-01-23-reg-ru-zabbix-template-v2-design.md`

---

## Task 1: Добавить новые макросы

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml:154-166`

**Step 1: Добавить макросы для порогов истечения и настроек**

Найти секцию `macros:` и добавить после существующих макросов:

```yaml
        - macro: '{$RR_EXPIRE_INFO}'
          value: '30'
          description: 'Дней до истечения — уровень Information'
        - macro: '{$RR_EXPIRE_WARNING}'
          value: '14'
          description: 'Дней до истечения — уровень Warning'
        - macro: '{$RR_EXPIRE_HIGH}'
          value: '7'
          description: 'Дней до истечения — уровень High'
        - macro: '{$RR_API_TIMEOUT}'
          value: '30s'
          description: 'Таймаут HTTP запросов к API'
        - macro: '{$RR_UPDATE_INTERVAL}'
          value: '1h'
          description: 'Интервал опроса API'
```

**Step 2: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml
git commit -m "feat: добавлены макросы для порогов истечения услуг

- {$RR_EXPIRE_INFO} = 30 дней
- {$RR_EXPIRE_WARNING} = 14 дней
- {$RR_EXPIRE_HIGH} = 7 дней
- {$RR_API_TIMEOUT} = 30s
- {$RR_UPDATE_INTERVAL} = 1h"
```

---

## Task 2: Добавить Value Maps

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml` (после секции `graphs:`)

**Step 1: Добавить секцию valuemaps в конец файла**

После секции `graphs:` добавить:

```yaml
  valuemaps:
    - uuid: a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4
      name: 'REG.RU Service State'
      mappings:
        - value: A
          newvalue: Active
        - value: D
          newvalue: Deleted
        - value: S
          newvalue: Suspended
        - value: W
          newvalue: Waiting
    - uuid: b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5
      name: 'REG.RU Autorenew'
      mappings:
        - value: 'on'
          newvalue: Enabled
        - value: 'off'
          newvalue: Disabled
```

**Step 2: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml
git commit -m "feat: добавлены value maps для статуса услуг и автопродления"
```

---

## Task 3: Добавить Master Item для списка услуг

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml:17` (секция items)

**Step 1: Добавить HTTP Agent item для service/get_list**

В секцию `items:` добавить новый master item:

```yaml
        - uuid: a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1
          name: 'REG.RU: Services List Raw'
          type: HTTP_AGENT
          key: rr.api.services.list
          delay: '{$RR_UPDATE_INTERVAL}'
          history: 1d
          value_type: TEXT
          trends: '0'
          status_codes: '200,400,401,403,404,500'
          timeout: '{$RR_API_TIMEOUT}'
          url: 'https://api.reg.ru/api/regru2/service/get_list'
          posts: 'username={$RR_USERNAME}&password={$RR_PASSWORD}&output_format=json'
          request_method: POST
          description: 'Raw JSON response from service/get_list API'
          tags:
            - tag: scope
              value: raw
            - tag: component
              value: services
```

**Step 2: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml
git commit -m "feat: добавлен master item для получения списка услуг (service/get_list)"
```

---

## Task 4: Добавить Master Item для неоплаченных счетов

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml` (секция items)

**Step 1: Добавить HTTP Agent item для bill/get_not_payed**

В секцию `items:` добавить:

```yaml
        - uuid: b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2
          name: 'REG.RU: Unpaid Bills Raw'
          type: HTTP_AGENT
          key: rr.api.bills.unpaid
          delay: '{$RR_UPDATE_INTERVAL}'
          history: 1d
          value_type: TEXT
          trends: '0'
          status_codes: '200,400,401,403,404,500'
          timeout: '{$RR_API_TIMEOUT}'
          url: 'https://api.reg.ru/api/regru2/bill/get_not_payed'
          posts: 'username={$RR_USERNAME}&password={$RR_PASSWORD}&output_format=json'
          request_method: POST
          description: 'Raw JSON response from bill/get_not_payed API'
          tags:
            - tag: scope
              value: raw
            - tag: component
              value: billing
```

**Step 2: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml
git commit -m "feat: добавлен master item для неоплаченных счетов (bill/get_not_payed)"
```

---

## Task 5: Добавить Dependent Items для счетов

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml` (секция items)

**Step 1: Добавить dependent items для подсчёта счетов**

```yaml
        - uuid: c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3
          name: 'REG.RU: Unpaid Bills Count'
          type: DEPENDENT
          key: rr.bills.unpaid.count
          delay: '0'
          history: 90d
          value_type: UNSIGNED
          preprocessing:
            - type: JSONPATH
              parameters:
                - '$.answer.bills'
              error_handler: CUSTOM_VALUE
              error_handler_params: '[]'
            - type: JSONPATH
              parameters:
                - '$.length()'
          master_item:
            key: rr.api.bills.unpaid
          description: 'Количество неоплаченных счетов'
          tags:
            - tag: scope
              value: billing
          triggers:
            - uuid: c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c4
              expression: 'last(/REG.RU/rr.bills.unpaid.count)>0'
              name: 'REG.RU: Unpaid bills'
              event_name: 'REG.RU: {ITEM.LASTVALUE} неоплаченных счетов'
              priority: WARNING
              description: 'Есть неоплаченные счета в аккаунте REG.RU'
        - uuid: c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4c4
          name: 'REG.RU: Unpaid Bills Sum'
          type: DEPENDENT
          key: rr.bills.unpaid.sum
          delay: '0'
          history: 90d
          value_type: FLOAT
          units: 'RUB'
          preprocessing:
            - type: JSONPATH
              parameters:
                - '$.answer.bills[*].total_sum'
              error_handler: CUSTOM_VALUE
              error_handler_params: '[0]'
            - type: JAVASCRIPT
              parameters:
                - |
                  var arr = JSON.parse(value);
                  var sum = 0;
                  for (var i = 0; i < arr.length; i++) {
                    sum += parseFloat(arr[i]) || 0;
                  }
                  return sum;
          master_item:
            key: rr.api.bills.unpaid
          description: 'Сумма неоплаченных счетов'
          tags:
            - tag: scope
              value: billing
```

**Step 2: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml
git commit -m "feat: добавлены dependent items для подсчёта неоплаченных счетов"
```

---

## Task 6: Добавить Dependent Item для общего количества услуг

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml` (секция items)

**Step 1: Добавить item для подсчёта услуг**

```yaml
        - uuid: d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4
          name: 'REG.RU: Services Total Count'
          type: DEPENDENT
          key: rr.services.total
          delay: '0'
          history: 90d
          value_type: UNSIGNED
          preprocessing:
            - type: JSONPATH
              parameters:
                - '$.answer.services'
              error_handler: CUSTOM_VALUE
              error_handler_params: '[]'
            - type: JSONPATH
              parameters:
                - '$.length()'
          master_item:
            key: rr.api.services.list
          description: 'Общее количество услуг в аккаунте'
          tags:
            - tag: scope
              value: inventory
```

**Step 2: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml
git commit -m "feat: добавлен item для подсчёта общего количества услуг"
```

---

## Task 7: Добавить LLD Rule для автообнаружения услуг

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml` (после секции items, перед macros)

**Step 1: Добавить секцию discovery_rules**

После закрытия секции `items:` и перед `macros:` добавить:

```yaml
      discovery_rules:
        - uuid: e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5
          name: 'REG.RU: Services Discovery'
          type: DEPENDENT
          key: rr.discovery.services
          delay: '0'
          lifetime: 7d
          description: 'Автообнаружение всех услуг REG.RU (домены, хостинг, VPS, SSL и др.)'
          master_item:
            key: rr.api.services.list
          preprocessing:
            - type: JSONPATH
              parameters:
                - '$.answer.services'
              error_handler: CUSTOM_VALUE
              error_handler_params: '[]'
            - type: JAVASCRIPT
              parameters:
                - |
                  var services = JSON.parse(value);
                  var lld = [];
                  for (var i = 0; i < services.length; i++) {
                    var s = services[i];
                    lld.push({
                      "{#SERVICE_ID}": String(s.service_id || ""),
                      "{#SERVICE_TYPE}": String(s.servtype || "unknown"),
                      "{#SERVICE_NAME}": String(s.dname || s.subtype || s.service_id || ""),
                      "{#EXPIRE_DATE}": String(s.expiration_date || ""),
                      "{#AUTORENEW}": String(s.autorenew_flag || s.autorenew || "off"),
                      "{#STATE}": String(s.state || "")
                    });
                  }
                  return JSON.stringify(lld);
          lld_macro_paths:
            - lld_macro: '{#SERVICE_ID}'
              path: '$.["{#SERVICE_ID}"]'
            - lld_macro: '{#SERVICE_TYPE}'
              path: '$.["{#SERVICE_TYPE}"]'
            - lld_macro: '{#SERVICE_NAME}'
              path: '$.["{#SERVICE_NAME}"]'
            - lld_macro: '{#EXPIRE_DATE}'
              path: '$.["{#EXPIRE_DATE}"]'
            - lld_macro: '{#AUTORENEW}'
              path: '$.["{#AUTORENEW}"]'
            - lld_macro: '{#STATE}'
              path: '$.["{#STATE}"]'
```

**Step 2: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml
git commit -m "feat: добавлен LLD rule для автообнаружения услуг REG.RU"
```

---

## Task 8: Добавить Item Prototypes для LLD

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml` (внутри discovery_rules)

**Step 1: Добавить item_prototypes в LLD rule**

Внутри discovery rule добавить после `lld_macro_paths:`:

```yaml
          item_prototypes:
            - uuid: f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f1
              name: 'Service [{#SERVICE_NAME}]: Type'
              type: DEPENDENT
              key: 'rr.service.type[{#SERVICE_ID}]'
              delay: '0'
              history: 7d
              value_type: TEXT
              trends: '0'
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - '$.answer.services[?(@.service_id=="{#SERVICE_ID}")].servtype.first()'
                  error_handler: CUSTOM_VALUE
                  error_handler_params: 'unknown'
              master_item:
                key: rr.api.services.list
              tags:
                - tag: service
                  value: reg.ru
                - tag: scope
                  value: '{#SERVICE_TYPE}'
                - tag: service_name
                  value: '{#SERVICE_NAME}'
                - tag: component
                  value: type
            - uuid: f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f2
              name: 'Service [{#SERVICE_NAME}]: State'
              type: DEPENDENT
              key: 'rr.service.state[{#SERVICE_ID}]'
              delay: '0'
              history: 7d
              value_type: TEXT
              trends: '0'
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - '$.answer.services[?(@.service_id=="{#SERVICE_ID}")].state.first()'
                  error_handler: CUSTOM_VALUE
                  error_handler_params: 'unknown'
              master_item:
                key: rr.api.services.list
              valuemap:
                name: 'REG.RU Service State'
              tags:
                - tag: service
                  value: reg.ru
                - tag: scope
                  value: '{#SERVICE_TYPE}'
                - tag: service_name
                  value: '{#SERVICE_NAME}'
                - tag: component
                  value: state
            - uuid: f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f3
              name: 'Service [{#SERVICE_NAME}]: Expiration Date'
              type: DEPENDENT
              key: 'rr.service.expire_date[{#SERVICE_ID}]'
              delay: '0'
              history: 90d
              value_type: TEXT
              trends: '0'
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - '$.answer.services[?(@.service_id=="{#SERVICE_ID}")].expiration_date.first()'
                  error_handler: CUSTOM_VALUE
                  error_handler_params: ''
              master_item:
                key: rr.api.services.list
              tags:
                - tag: service
                  value: reg.ru
                - tag: scope
                  value: '{#SERVICE_TYPE}'
                - tag: service_name
                  value: '{#SERVICE_NAME}'
                - tag: component
                  value: expiration
            - uuid: f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f4
              name: 'Service [{#SERVICE_NAME}]: Days Until Expiration'
              type: DEPENDENT
              key: 'rr.service.days_left[{#SERVICE_ID}]'
              delay: '0'
              history: 90d
              value_type: SIGNED
              units: 'days'
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - '$.answer.services[?(@.service_id=="{#SERVICE_ID}")].expiration_date.first()'
                  error_handler: CUSTOM_VALUE
                  error_handler_params: ''
                - type: JAVASCRIPT
                  parameters:
                    - |
                      if (!value || value === '') return -9999;
                      var expireTs = Date.parse(value);
                      if (isNaN(expireTs)) return -9999;
                      var now = Date.now();
                      var days = Math.floor((expireTs - now) / 86400000);
                      return days;
              master_item:
                key: rr.api.services.list
              tags:
                - tag: service
                  value: reg.ru
                - tag: scope
                  value: '{#SERVICE_TYPE}'
                - tag: service_name
                  value: '{#SERVICE_NAME}'
                - tag: component
                  value: expiration
            - uuid: f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f5
              name: 'Service [{#SERVICE_NAME}]: Autorenew'
              type: DEPENDENT
              key: 'rr.service.autorenew[{#SERVICE_ID}]'
              delay: '0'
              history: 7d
              value_type: TEXT
              trends: '0'
              preprocessing:
                - type: JSONPATH
                  parameters:
                    - '$.answer.services[?(@.service_id=="{#SERVICE_ID}")].autorenew_flag.first()'
                  error_handler: CUSTOM_VALUE
                  error_handler_params: 'off'
              master_item:
                key: rr.api.services.list
              valuemap:
                name: 'REG.RU Autorenew'
              tags:
                - tag: service
                  value: reg.ru
                - tag: scope
                  value: '{#SERVICE_TYPE}'
                - tag: service_name
                  value: '{#SERVICE_NAME}'
                - tag: component
                  value: autorenew
```

**Step 2: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml
git commit -m "feat: добавлены item prototypes для LLD услуг

- type, state, expire_date, days_left, autorenew
- value maps для state и autorenew
- теги для фильтрации"
```

---

## Task 9: Добавить Trigger Prototypes для LLD

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml` (внутри discovery_rules)

**Step 1: Добавить trigger_prototypes в LLD rule**

После `item_prototypes:` добавить:

```yaml
          trigger_prototypes:
            - uuid: g7g7g7g7g7g7g7g7g7g7g7g7g7g7g7g1
              expression: 'last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])<0'
              name: 'Service [{#SERVICE_NAME}]: EXPIRED'
              event_name: '{#SERVICE_TYPE}: {#SERVICE_NAME} ИСТЕКЛА (дата: {#EXPIRE_DATE})'
              priority: DISASTER
              description: 'Услуга {#SERVICE_NAME} ({#SERVICE_TYPE}) истекла {#EXPIRE_DATE}'
              tags:
                - tag: scope
                  value: expiration
            - uuid: g7g7g7g7g7g7g7g7g7g7g7g7g7g7g7g2
              expression: 'last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])>=0 and last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])<={$RR_EXPIRE_HIGH}'
              name: 'Service [{#SERVICE_NAME}]: Expires in {ITEM.LASTVALUE} days'
              event_name: '{#SERVICE_TYPE}: {#SERVICE_NAME} истекает через {ITEM.LASTVALUE} дней (дата: {#EXPIRE_DATE})'
              priority: HIGH
              description: 'Услуга {#SERVICE_NAME} ({#SERVICE_TYPE}) истекает менее чем через {$RR_EXPIRE_HIGH} дней'
              dependencies:
                - name: 'Service [{#SERVICE_NAME}]: EXPIRED'
                  expression: 'last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])<0'
              tags:
                - tag: scope
                  value: expiration
            - uuid: g7g7g7g7g7g7g7g7g7g7g7g7g7g7g7g3
              expression: 'last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])>{$RR_EXPIRE_HIGH} and last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])<={$RR_EXPIRE_WARNING}'
              name: 'Service [{#SERVICE_NAME}]: Expires in {ITEM.LASTVALUE} days'
              event_name: '{#SERVICE_TYPE}: {#SERVICE_NAME} истекает через {ITEM.LASTVALUE} дней (дата: {#EXPIRE_DATE})'
              priority: WARNING
              description: 'Услуга {#SERVICE_NAME} ({#SERVICE_TYPE}) истекает менее чем через {$RR_EXPIRE_WARNING} дней'
              dependencies:
                - name: 'Service [{#SERVICE_NAME}]: Expires in {ITEM.LASTVALUE} days'
                  expression: 'last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])>=0 and last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])<={$RR_EXPIRE_HIGH}'
              tags:
                - tag: scope
                  value: expiration
            - uuid: g7g7g7g7g7g7g7g7g7g7g7g7g7g7g7g4
              expression: 'last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])>{$RR_EXPIRE_WARNING} and last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])<={$RR_EXPIRE_INFO}'
              name: 'Service [{#SERVICE_NAME}]: Expires in {ITEM.LASTVALUE} days'
              event_name: '{#SERVICE_TYPE}: {#SERVICE_NAME} истекает через {ITEM.LASTVALUE} дней (дата: {#EXPIRE_DATE})'
              priority: INFO
              description: 'Услуга {#SERVICE_NAME} ({#SERVICE_TYPE}) истекает менее чем через {$RR_EXPIRE_INFO} дней'
              dependencies:
                - name: 'Service [{#SERVICE_NAME}]: Expires in {ITEM.LASTVALUE} days'
                  expression: 'last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])>{$RR_EXPIRE_HIGH} and last(/REG.RU/rr.service.days_left[{#SERVICE_ID}])<={$RR_EXPIRE_WARNING}'
              tags:
                - tag: scope
                  value: expiration
            - uuid: g7g7g7g7g7g7g7g7g7g7g7g7g7g7g7g5
              expression: 'last(/REG.RU/rr.service.autorenew[{#SERVICE_ID}])="off"'
              name: 'Service [{#SERVICE_NAME}]: Autorenew DISABLED'
              event_name: '{#SERVICE_TYPE}: {#SERVICE_NAME} — автопродление ВЫКЛЮЧЕНО'
              priority: WARNING
              description: 'Автопродление отключено для услуги {#SERVICE_NAME} ({#SERVICE_TYPE}). Требуется ручное продление.'
              tags:
                - tag: scope
                  value: autorenew
```

**Step 2: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml
git commit -m "feat: добавлены trigger prototypes для LLD услуг

- DISASTER: услуга истекла
- HIGH: истекает <= 7 дней
- WARNING: истекает <= 14 дней
- INFO: истекает <= 30 дней
- WARNING: автопродление отключено
- зависимости между триггерами"
```

---

## Task 10: Обновить Dashboard

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml` (секция dashboards)

**Step 1: Заменить секцию dashboards на расширенную версию**

Заменить существующую секцию `dashboards:` на:

```yaml
      dashboards:
        - uuid: a6258dacfb694080bb8d41b5ca1540dd
          name: 'REG.RU Overview'
          pages:
            - name: 'Overview'
              widgets:
                - type: item
                  name: 'Баланс'
                  width: '6'
                  height: '3'
                  fields:
                    - type: ITEM
                      name: itemid
                      value:
                        host: REG.RU
                        key: rr-prepay
                    - type: INTEGER
                      name: show
                      value: '1'
                    - type: INTEGER
                      name: show
                      value: '2'
                    - type: INTEGER
                      name: show
                      value: '4'
                - type: item
                  name: 'API Статус'
                  x: '6'
                  width: '6'
                  height: '3'
                  fields:
                    - type: ITEM
                      name: itemid
                      value:
                        host: REG.RU
                        key: rr-api-status
                - type: item
                  name: 'Неоплаченных счетов'
                  'y': '3'
                  width: '6'
                  height: '3'
                  fields:
                    - type: ITEM
                      name: itemid
                      value:
                        host: REG.RU
                        key: rr.bills.unpaid.count
                - type: item
                  name: 'Всего услуг'
                  x: '6'
                  'y': '3'
                  width: '6'
                  height: '3'
                  fields:
                    - type: ITEM
                      name: itemid
                      value:
                        host: REG.RU
                        key: rr.services.total
                - type: graphprototype
                  name: 'Дней до истечения услуг'
                  'y': '6'
                  width: '24'
                  height: '5'
                  fields:
                    - type: GRAPH_PROTOTYPE
                      name: graphid
                      value:
                        host: REG.RU
                        name: 'Service [{#SERVICE_NAME}]: Days until expiration'
                - type: graph
                  name: 'Тренд баланса'
                  'y': '11'
                  width: '24'
                  height: '5'
                  fields:
                    - type: GRAPH
                      name: graphid
                      value:
                        host: REG.RU
                        name: 'REG.RU: Funds'
```

**Step 2: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml
git commit -m "feat: обновлён dashboard с новыми виджетами

- виджеты: баланс, статус, счета, кол-во услуг
- график дней до истечения (prototype)
- тренд баланса"
```

---

## Task 11: Добавить Graph Prototype для LLD

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml` (внутри discovery_rules)

**Step 1: Добавить graph_prototypes в LLD rule**

После `trigger_prototypes:` добавить:

```yaml
          graph_prototypes:
            - uuid: h8h8h8h8h8h8h8h8h8h8h8h8h8h8h8h8
              name: 'Service [{#SERVICE_NAME}]: Days until expiration'
              graph_items:
                - color: 1A7C11
                  item:
                    host: REG.RU
                    key: 'rr.service.days_left[{#SERVICE_ID}]'
```

**Step 2: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml
git commit -m "feat: добавлен graph prototype для дней до истечения услуг"
```

---

## Task 12: Обновить версию и метаданные шаблона

**Files:**
- Modify: `/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml:11-14`
- Modify: `/opt/zabbix-reg.ru-api/CONTINUITY.md`

**Step 1: Обновить версию в шаблоне**

Изменить:
```yaml
      vendor:
        name: itforprof.com
        version: 2.0.0
```

И обновить description:
```yaml
      description: 'Template for monitoring REG.RU API: services expiration, balance, unpaid bills. Auto-discovery of all service types. itforprof.com by Konstantin Tyutyunnik'
```

**Step 2: Обновить CONTINUITY.md**

Добавить в начало секции Changelog:

```markdown
### [2.0.0] - 2026-01-23
- Major: Добавлен LLD для автообнаружения всех типов услуг REG.RU
- Добавлены item prototypes: type, state, expire_date, days_left, autorenew
- Добавлены trigger prototypes для контроля сроков истечения (4 уровня)
- Добавлен master item для service/get_list
- Добавлен master item для bill/get_not_payed
- Добавлены items для подсчёта неоплаченных счетов
- Добавлены макросы для порогов: RR_EXPIRE_INFO/WARNING/HIGH
- Добавлены value maps для статуса услуг и автопродления
- Обновлён dashboard с новыми виджетами
- Добавлен graph prototype для дней до истечения
```

**Step 3: Валидация YAML**

Run: `python3 -c "import yaml; yaml.safe_load(open('/opt/zabbix-reg.ru-api/zabbix-reg.ru-api_template.yaml'))"`
Expected: No output (valid YAML)

**Step 4: Commit**

```bash
git add zabbix-reg.ru-api_template.yaml CONTINUITY.md
git commit -m "release: версия 2.0.0 — LLD автообнаружение услуг

Major release:
- LLD для всех типов услуг REG.RU
- Контроль сроков истечения (4 уровня триггеров)
- Мониторинг неоплаченных счетов
- Расширенный dashboard"
```

---

## Task 13: Тестирование в Zabbix

**Files:**
- Run: `/opt/zabbix-reg.ru-api/import_template.py`

**Step 1: Обновить import_template.py для новых правил импорта**

Добавить в rules:
```python
"discoveryRules": {"createMissing": True, "updateExisting": True, "deleteMissing": False},
"valueMaps": {"createMissing": True, "updateExisting": True},
```

**Step 2: Импортировать шаблон**

Run: `python3 /opt/zabbix-reg.ru-api/import_template.py`
Expected: `{"jsonrpc":"2.0","result":true,"id":1}`

**Step 3: Проверить в Zabbix UI**

1. Открыть Data collection → Templates → REG.RU
2. Проверить: Items (10), Discovery rules (1), Triggers, Macros (9), Value maps (2)
3. Привязать шаблон к хосту с настроенными макросами
4. Дождаться выполнения LLD (или запустить вручную)
5. Проверить автообнаруженные услуги в Latest data

**Step 4: Commit скрипт импорта**

```bash
git add import_template.py
git commit -m "chore: обновлён скрипт импорта для LLD и valuemaps"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Новые макросы | template.yaml |
| 2 | Value Maps | template.yaml |
| 3 | Master Item services | template.yaml |
| 4 | Master Item bills | template.yaml |
| 5 | Dependent Items bills | template.yaml |
| 6 | Services count item | template.yaml |
| 7 | LLD Rule | template.yaml |
| 8 | Item Prototypes | template.yaml |
| 9 | Trigger Prototypes | template.yaml |
| 10 | Dashboard update | template.yaml |
| 11 | Graph Prototype | template.yaml |
| 12 | Version & docs | template.yaml, CONTINUITY.md |
| 13 | Test import | import_template.py |

**Total commits:** 13
**Estimated API calls after implementation:** ~4/hour
