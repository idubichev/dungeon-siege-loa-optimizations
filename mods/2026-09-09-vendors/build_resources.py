"""Rebuild vendor rolls from pre-v1 stock while preserving installed loot edits."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / '2026-09-06'
GAME = Path.home() / 'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
sys.path.insert(0, str(OLD / 'tools'))
from gas import blocks, fields, ancestors, edit
from tank import Tank, write_tank

old = Tank(GAME / 'DSLOA/DS_OP_LootVendors_v1.dsres')
files = {p: old.read(p) for p in old.files}
tanks = sorted([Tank(f) for d in ['Resources', 'DSLOA'] for f in (GAME / d).glob('*.dsres')], key=lambda t: t.priority)
effective = {p: t for t in tanks for p in t.files}
baseline_sources = json.loads((OLD / 'analysis.json').read_text())['effective']
category = r'(weapon|melee|ranged|armor|body|helm|boots|gloves|shield|sword|axe|mace|hammer|staff|bow|crossbow|ring|amulet|spellbook)'
pattern = re.compile(r'(#' + category + r'(?:,[^/]*)?)/(\d+(?:\.\d+)?-\d+(?:\.\d+)?)')
changes = []

def stock_blocks(text):
    _, nodes = blocks(text, tolerant=True)
    return {next(a.name for a in ancestors(b) if 't:template' in a.name): b
            for b in nodes if b.name == 'store_pcontent'}

for path, tank in effective.items():
    if not path.startswith('world/contentdb/templates/') or not path.endswith('.gas'):
        continue
    current = tank.read(path).decode('cp1252')
    if '[store_pcontent]' not in current:
        continue
    source = (OLD / baseline_sources[path]).read_text(encoding='cp1252') if tank.path == old.path else current
    current_stores = stock_blocks(current)
    originals = stock_blocks(source)
    replacements = []
    for template, store in originals.items():
        chunk = source[store.start:store.end + 1]
        _, nodes = blocks(chunk)
        edits = []
        details = []
        for block in nodes:
            fs = {k: (v, start, end) for k, v, start, end in fields(chunk, block)}
            query = fs.get('il_main', ('',))[0]
            match = pattern.fullmatch(query)
            if not match or 'chance' in fs or any(k not in fs or not fs[k][0].isdigit() for k in ['min', 'max']):
                continue
            minimum, maximum = [int(fs[k][0]) for k in ['min', 'max']]
            if minimum < 2:
                continue
            rare = minimum // 2
            unique = minimum // 4
            converted = rare + unique
            for key in ['min', 'max']:
                value, start, end = fs[key]
                edits.append((start, end, str(int(value) - converted)))
            extra = ''
            for rarity, count in [('rare(1)', rare), ('unique(2)', unique)]:
                if count:
                    q = f'{match[1]}/-{rarity}/{match[3]}'
                    extra += f'\n\t\t\t[all*] {{ il_main = {q}; min = {count}; max = {count}; }}'
            edits.append((block.end + 1, block.end + 1, extra))
            details.append(dict(query=query, category=match[2], minimum=minimum, maximum=maximum,
                                normal_min=minimum-converted, rare=rare, unique=unique))
        if edits:
            new = edit(chunk, edits)
            blocks(new)
            target = current_stores[template]
            replacements.append((target.start, target.end + 1, new))
            changes.append(dict(path=path, template=template, rolls=details))
    if replacements:
        result = edit(current, replacements).encode('cp1252')
        files[path] = result
        for folder, data in [('before', current.encode('cp1252')), ('source', result)]:
            dest = ROOT / folder / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)

assert any(row['template'] == 't:template,n:jonn' and any(x['category'] == 'melee' for x in row['rolls']) for row in changes)
out = ROOT / 'DS_OP_LootVendors_v2.dsres'
write_tank(out, files, GAME / 'DSLOA/Expansion.dsres', 'OP Loot and Vendors v2: all equipment categories')
meta = dict(archive_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
            previous_archive_sha256=hashlib.sha256(old.path.read_bytes()).hexdigest(),
            files=len(files), stores=len(changes), changes=changes,
            rare_loot_preserved=True, inventory_quantities_preserved=True)
(ROOT / 'resources.json').write_text(json.dumps(meta, indent=2) + '\n')
print(f'Built {len(changes)} vendor definitions; {len(files)} resources with existing loot edits retained.')
for row in changes:
    if row['template'] == 't:template,n:jonn':
        print('Jonn:', {key: sum(r[key] for r in row['rolls']) for key in ['minimum', 'normal_min', 'rare', 'unique']})
