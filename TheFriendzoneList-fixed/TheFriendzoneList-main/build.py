#!/usr/bin/env python3
"""
Rebuilds the two files that let index.html work when opened directly from disk:

  data/data.js   - all JSON in data/ embedded as window.__DATA__
  js/bundle.js   - the ES modules in js/ combined into one classic script

Run `python build.py` after editing anything in data/ or js/.
"""
import json, re
from pathlib import Path

root = Path(__file__).parent

# ---- data/data.js ----------------------------------------------------------
data = {f.stem: json.loads(f.read_text(encoding='utf-8'))
        for f in sorted((root / 'data').glob('*.json'))}
(root / 'data' / 'data.js').write_text(
    'window.__DATA__ = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n',
    encoding='utf-8')

# ---- js/bundle.js ----------------------------------------------------------
# (file, name given to its default export). Dependency order matters.
order = [
    ('util.js', None), ('score.js', None), ('content.js', None),
    ('store.js', None),
    ('components/Spinner.js', 'Spinner'), ('components/Btn.js', 'Btn'),
    ('components/List/LevelAuthors.js', 'LevelAuthors'),
    ('pages/List.js', 'List'), ('pages/Leaderboard.js', 'Leaderboard'),
    ('pages/Roulette.js', 'Roulette'),
    ('routes.js', 'routes'), ('main.js', None),
]
out = ['(function () {\n"use strict";\n']
for name, default in order:
    src = (root / 'js' / name).read_text(encoding='utf-8')
    src = re.sub(r'^import\s[^;]*?;\s*$', '', src, flags=re.M | re.S)
    if default:
        src = src.replace('export default', f'const {default} =', 1)
    src = re.sub(r'^export\s+', '', src, flags=re.M)
    out.append(f'// ---- {name} ----\n{src}\n')
out.append('})();\n')
(root / 'js' / 'bundle.js').write_text(''.join(out), encoding='utf-8')
print('Built data/data.js and js/bundle.js')
