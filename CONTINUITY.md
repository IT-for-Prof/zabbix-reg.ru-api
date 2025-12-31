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
- Done: Fixed `*UNKNOWN*` issue in `rr-api-status` and `rr-prepay` triggers.
- Now: Version 1.1.3 released.
- Next: None.

## Open questions
- None.

## Working set
- `zabbix-reg.ru-api_template.yaml`

## Changelog
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
