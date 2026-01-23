# Continuity Ledger

## Goal
Fix `*UNKNOWN*` in trigger name/event name in `zabbix-reg.ru-api_template.yaml` when REG.RU API returns an error.

## Constraints/Assumptions
- Zabbix version: 7.0.
- All scripts/devs must have copyright: `itforprof.com by Konstantin Tyutyunnik`.
- Use Russian for commits.
- End of line: LF.
- API response contains `error_text` and `result: "error"`.

## Key decisions
- Use `{ITEM.VALUE<N>}` for trigger/event names by adding the target items to the trigger expression via `length(...)>=0`.
- This ensures the items are always evaluated and available to the trigger notification system.
- Fixed trigger expression to correctly check 4 distinct consecutive values (`last`, `#2`, `#3`, `#4`).

## State
- Done: Version 2.0.0 released with LLD auto-discovery.
- Now: None.
- Next: None.

## Open questions
- None.

## Working set
- `zabbix-reg.ru-api_template.yaml`

## Changelog
### [2.1.0] - 2026-01-23
- REMOVED: Autorenew item and trigger (API service/get_list не возвращает эти данные)
- REMOVED: REG.RU Autorenew value map
- IMPROVED: Dashboard — добавлены виджеты "Проблемы" и "Услуги: сроки истечения"
- IMPROVED: Dashboard layout — более компактное размещение

### [2.0.5] - 2026-01-23
- Made LLD filter configurable via macro {$RR_EXCLUDE_TYPES}
- Default value: ^(srv_parking)$ — excludes free parking pages
- Examples: ^(srv_parking|srv_hosting)$ to exclude multiple types

### [2.0.4] - 2026-01-23
- Added LLD filter to exclude srv_parking (free parking pages) from discovery
- These services have no practical expiration dates and don't need monitoring

### [2.0.3] - 2026-01-23
- Fixed "Autorenew DISABLED" trigger to not fire for expired services (days_left < 0)

### [2.0.2] - 2026-01-23
- Fixed VPS and pay-as-you-go services: days_left=99999 for services without expiration date
- Fixed EXPIRED trigger to exclude services without expiration (days_left > -99998)
- Fixed "Autorenew DISABLED" trigger to exclude VPS services (days_left < 99990)
- Removed duplicate "days" from trigger names (item already has units)

### [2.0.1] - 2026-01-23
- Fixed duplicate names error when same domain has multiple service types (domain + srv_parking, dom_pp)
- Added {#SERVICE_TYPE} to all item prototype, trigger prototype, and graph prototype names
- Format: `Service [{#SERVICE_TYPE}] {#SERVICE_NAME}: <metric>`
- Fixed trigger dependency names to match updated trigger names

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

### [1.1.3] - 2025-12-31
- Fixed `*UNKNOWN*` in trigger name and event name by adding `rr-api-error-text` and `rr-currency` to trigger expressions and using `{ITEM.VALUE<N>}`.
- Fixed trigger expression for `rr-api-status` to correctly check 4 consecutive failures (changed `#1` to `#4`).
- Updated `rr-prepay` trigger event name to use `{ITEM.VALUE1}` and `{ITEM.VALUE2}`.
- Incremented template version to 1.1.3.

### [1.1.2] - 2025-12-30
- Added HTTP status code handling (200, 400-500) to master item `rr-api-user-get_balance`.
- Added `error_handler: CUSTOM_VALUE` (unknown) to `rr-api-status` to handle missing `$.result`.
- Incremented template version to 1.1.2.

### [1.1.1] - 2025-12-30
- Added `error_handler: DISCARD_VALUE` to dependent items parsing `$.answer` to handle API errors (like IP restriction) gracefully.

### [1.1.0] - 2025-12-30
- Fixed typo `get_blance` -> `get_balance`.
- Added `rr-credit`, `rr-currency`, `rr-error-code` items.
- Added "Discard unchanged with heartbeat (6h)" for `rr-api-status`.
- Added Graph "REG.RU: Funds" and Dashboard "REG.RU API Overview".
- Added tags to template and items (`scope`, `service`, `vendor`).
- Improved trigger names and event names with `{ITEM.VALUE}` and `{?last()}`.
