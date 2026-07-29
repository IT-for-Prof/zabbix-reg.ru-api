#!/usr/bin/env python3
"""Проверка JS-препроцессинга размера снапшотов из zabbix-reg.ru-cloud-api_template.yaml.

Скрипт вытаскивает JavaScript прямо из шаблона и прогоняет его через node на
примере ответа API из документации (developers.cloudvps.reg.ru/snapshots/list.html).
Тестируется настоящий код шаблона, а не его копия.

Запуск: python3 test_snapshot_size.py
"""
import json
import subprocess
import sys

import yaml

TEMPLATE = "zabbix-reg.ru-cloud-api_template.yaml"
GB = 1073741824

# Пример из документации CloudVPS API: size_gigabytes — строка, не число.
API_SAMPLE = {
    "snapshots": [
        {
            "created_at": "2018-07-12 02:42:00",
            "distribution": "ubuntu-16.04",
            "id": 6893,
            "min_disk_size": "10.00",
            "name": "snapshot 1",
            "private": 1,
            "size_gigabytes": "1.05",
            "slug": None,
            "type": "snapshot",
        },
        {
            "created_at": "2019-01-02 03:04:05",
            "distribution": "centos-8",
            "id": 7001,
            "min_disk_size": "5.00",
            "name": "snapshot 2",
            "private": 1,
            "size_gigabytes": "2.40",
            "slug": None,
            "type": "snapshot",
        },
    ]
}


def run_js(code, value):
    """Прогоняет JS так, как это делает препроцессинг Zabbix: value → return."""
    wrapper = "var value = %s; console.log(String((function(){%s})()));" % (
        json.dumps(value),
        code,
    )
    out = subprocess.run(
        ["node", "-e", wrapper], capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


def load(path):
    """Достаёт JS суммирующего айтема и JS прототипа отдельного снапшота."""
    tpl = yaml.safe_load(open(path))["zabbix_export"]["templates"][0]

    total_js = None
    for item in tpl["items"]:
        if item["key"] == "rrc.snapshots.size.total":
            for step in item["preprocessing"]:
                if step["type"] == "JAVASCRIPT":
                    total_js = step["parameters"][0]

    proto_jsonpath = proto_js = None
    for rule in tpl["discovery_rules"]:
        for proto in rule.get("item_prototypes", []):
            if proto["key"].startswith("rrc.snapshot.size["):
                for step in proto["preprocessing"]:
                    if step["type"] == "JSONPATH":
                        proto_jsonpath = step["parameters"][0]
                    if step["type"] == "JAVASCRIPT":
                        proto_js = step["parameters"][0]

    assert total_js, "не найден JAVASCRIPT в rrc.snapshots.size.total"
    assert proto_js, "не найден JAVASCRIPT в прототипе rrc.snapshot.size[]"
    assert proto_jsonpath, "не найден JSONPATH в прототипе rrc.snapshot.size[]"
    return total_js, proto_jsonpath, proto_js


def main():
    total_js, proto_jsonpath, proto_js = load(TEMPLATE)
    snapshots = API_SAMPLE["snapshots"]

    # JSONPATH первым шагом уже вырезал $.snapshots, JS получает массив.
    got = run_js(total_js, json.dumps(snapshots))
    want = str(round((1.05 + 2.40) * GB))
    assert got == want, "сумма: получено %s, ожидалось %s" % (got, want)

    # Пустой список — снапшотов нет, ноль байт, а не ошибка.
    got = run_js(total_js, "[]")
    assert got == "0", "пустой список: получено %s, ожидалось 0" % got

    # Регрессия: старый код брал поле .size, которого в API нет, и молча давал 0.
    assert "size_gigabytes" in total_js, "JS снова читает несуществующее поле .size"
    assert (
        "size_gigabytes" in proto_jsonpath
    ), "JSONPath прототипа снова читает несуществующее поле .size"

    # Прототип: одна строка "1.05" → байты. Zabbix отдаёт значение строкой.
    got = run_js(proto_js, "1.05")
    want = str(round(1.05 * GB))
    assert got == want, "прототип: получено %s, ожидалось %s" % (got, want)

    # Значение по умолчанию из error_handler CUSTOM_VALUE '0'.
    got = run_js(proto_js, "0")
    assert got == "0", "прототип, значение 0: получено %s, ожидалось 0" % got

    print("OK: сумма %s B, прототип %s B, пустой список 0 B" % (
        str(round((1.05 + 2.40) * GB)), str(round(1.05 * GB))
    ))


if __name__ == "__main__":
    sys.exit(main())
