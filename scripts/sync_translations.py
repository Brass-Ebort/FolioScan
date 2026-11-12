"""Validate and copy the canonical UTF-8 catalogue without modifying source code."""
import csv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / 'shared/translations.tsv'
with source.open(encoding='utf-8', newline='') as stream:
    rows = list(csv.reader(stream, delimiter='\t'))
assert rows[0] == ['es','en','fr','it','pt','nl','uk','ru','sv','pl','cs']
assert all(len(row) == 11 and all(row) for row in rows)
assert len({row[0] for row in rows}) == len(rows), 'Duplicate translation key'
for target in ['desktop/translations.tsv','app/src/main/assets/translations.tsv']:
    (root / target).write_bytes(source.read_bytes())
print(f'{len(rows)-1} strings synchronized')
