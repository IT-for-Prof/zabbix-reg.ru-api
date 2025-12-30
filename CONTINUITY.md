# Continuity Ledger

## Goal
Improve Zabbix template `zabbix-reg.ru-api_template.yaml` to display `error_text` from the API response in triggers when an error occurs.

## Constraints/Assumptions
- Zabbix version: 7.0 (as per template).
- API response contains `result: "error"` and `error_text` when access is denied or other errors occur.
- Master item `rr-api-user-get_blance` fetches the full JSON.
- All scripts/devs must have copyright: `itforprof.com by Konstantin Tyutyunnik`.
- Use Russian for commits.
- End of line: LF.

## Key decisions
- Added a new dependent item `rr-api-error-text` to extract `$.error_text` from the master item.
- Updated the `rr-api-status` trigger to include the value of `rr-api-error-text` in the event name using `{?last(/REG.RU/rr-api-error-text)}`.
- Used `JSONPATH` with `error_handler: CUSTOM_VALUE` to handle cases where `error_text` is missing.

## State
- Done: Added `rr-api-error-text` item, updated `rr-api-status` trigger, added copyright notice.
- Now: Completed.
- Next: None.

## Open questions
- None.

## Working set
- `zabbix-reg.ru-api_template.yaml`

## Changelog
### [1.0.1] - 2025-12-30
- Added `rr-api-error-text` item.
- Updated `rr-api-status` trigger to show error text in name and event name.
- Added copyright notice: `itforprof.com by Konstantin Tyutyunnik`.
