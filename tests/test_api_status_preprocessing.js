const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const yaml = fs.readFileSync('zabbix-reg.ru-cloud-api_template.yaml', 'utf8');
const start = yaml.indexOf("name: 'RRC: API Status'");
const end = yaml.indexOf('\n          master_item:', start);
const block = yaml.slice(start, end);
const marker = '                - |\n';
const script = block
  .slice(block.indexOf(marker) + marker.length)
  .split('\n')
  .map(line => line.startsWith('                  ') ? line.slice(18) : line)
  .join('\n');
const preprocess = vm.runInNewContext(`(function(value) { ${script} })`);

assert.equal(preprocess('{"reglets": []}'), 'success');
assert.equal(preprocess('{"error": "rate limited"}'), 'error: rate limited');
assert.equal(preprocess('<html><body>edge challenge</body></html>'), 'error: non-JSON response (HTML)');
