"""Build removable loot, merchant and attribute mods from installed content."""
from pathlib import Path
import collections, hashlib, json, re, sys
sys.path.insert(0, str(Path(__file__).parent / 'tools'))
from gas import blocks, fields, ancestors, edit
from tank import write_tank

p = Path(__file__).resolve().parent
game = Path.home() / 'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
effective = json.loads((p / 'analysis.json').read_text())['effective']
packages = {name: {} for name in ('Attributes', 'RareLoot', 'Vendors')}
changes, skipped = [], []

def record(kind, path, block, before, after):
    template = next((b.name for b in [block, *ancestors(block)] if 't:template' in b.name), '')
    changes.append(dict(kind=kind, file=path, template=template, before=before, after=after))

formula = 'world/global/formula/formulas.gas'
text = (p / effective[formula]).read_text(encoding='cp1252')
root, nodes = blocks(text)
replacements = []
for block in nodes:
    fs = list(fields(text, block))
    values = {k: v.strip('"') for k, v, *_ in fs}
    school = values.get('name')
    if school not in ('Melee', 'Ranged', 'Nature Magic', 'Combat Magic'):
        continue
    major = {'Melee': 'str_influence', 'Ranged': 'dex_influence', 'Nature Magic': 'int_influence', 'Combat Magic': 'int_influence'}[school]
    for key, value, start, end in fs:
        if key in ('str_influence', 'dex_influence', 'int_influence'):
            new = '1.35' if key == major else '1.0'
            replacements.append((start, end, new))
            record('attribute', formula, block, school + ':' + key + '=' + value, new)
assert len(replacements) == 12
packages['Attributes'][formula] = edit(text, replacements).encode('cp1252')

for path, source in effective.items():
    if not path.startswith('world/contentdb/templates/'):
        continue
    text = (p / source).read_text(encoding='cp1252')
    try:
        root, nodes = blocks(text, tolerant=True)
    except (AssertionError, ValueError) as error:
        skipped.append(dict(file=path, reason=str(error)))
        continue
    fs = {id(b): list(fields(text, b)) for b in nodes}
    loot = {}
    for b in nodes:
        entries = fs[id(b)]
        query = ' '.join(v for k, v, *_ in entries if k == 'il_main')
        multiplier = 5 if '-unique(' in query else 10 if '-rare(' in query else 0
        chance = next((f for f in entries if f[0] == 'chance'), None)
        if multiplier and chance and re.fullmatch(r'[\d.]+', chance[1]) and any(a.name in ('pcontent', 'delayed_pcontent') for a in ancestors(b)):
            old = float(chance[1])
            loot[id(b)] = [b, chance, min(1.0, old * multiplier)]
    # Chances compete only when their immediate parent is a oneof group.
    for parent in [root, *nodes]:
        if not parent.name.startswith('oneof'):
            continue
        targets = [loot[id(b)] for b in parent.children if id(b) in loot]
        if not targets:
            continue
        fixed = sum(float(re.match(r'[\d.]+', v)[0]) for b in parent.children if id(b) not in loot for k, v, *_ in fs[id(b)] if k == 'chance' and re.match(r'[\d.]+', v))
        wanted = sum(x[2] for x in targets)
        room = max(0, 1.0 - fixed)
        if wanted > room:
            for target in targets:
                target[2] = max(float(target[1][1]), target[2] * room / wanted)
    edits = []
    for b, chance, value in loot.values():
        if value > float(chance[1]):
            new = format(value, '.8g')
            if float(new) <= float(chance[1]):
                continue
            edits.append((chance[2], chance[3], new))
            record('rare_drop' if any('-rare(' in v for k, v, *_ in fs[id(b)]) else 'unique_drop', path, b, chance[1], new)
    if edits:
        packages['RareLoot'][path] = edit(text, edits).encode('cp1252')

    loot_edits = edits[:]
    edits = []
    for store in [b for b in nodes if b.name == 'store_pcontent']:
        stock_max = 0
        for b in nodes:
            if any(a is store for a in ancestors(b)):
                stock_max += sum(float(re.match(r'[\d.]+', v)[0]) for k, v, *_ in fs[id(b)] if k == 'max' and re.match(r'[\d.]+', v))
        for tab in store.children:
            candidates = []
            for b in tab.children:
                values = {k: (v, start, end) for k, v, start, end in fs[id(b)]}
                query = values.get('il_main', ('', 0, 0))[0]
                match = re.fullmatch(r'#(weapon|armor|body|helm|boots|gloves|shield|sword|axe|mace|hammer|staff|bow|crossbow|ring|amulet|spellbook)(?:,[^/]*)?/(?:-[^/]+/)?(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)', query)
                if match and all(k in values and re.fullmatch(r'\d+', values[k][0]) for k in ('min', 'max')) and '-rare(' not in query and '-unique(' not in query:
                    minimum, maximum = int(values['min'][0]), int(values['max'][0])
                    if minimum >= 1 and maximum >= 2:
                        candidates.append((float(match[3]), minimum, b, values, match))
            if not candidates:
                continue
            _, minimum, b, values, match = max(candidates, key=lambda x: (x[0], x[1]))
            count = min(3, minimum, int(values['max'][0]) - 1)
            for key in ('min', 'max'):
                old, start, end = values[key]
                edits.append((start, end, str(int(old) - count)))
            rare_count, unique_count = (count - 1, 1) if count >= 2 else (1, 0)
            extra = ''
            for rarity, quantity in [('rare(1)', rare_count), ('unique(2)', unique_count)]:
                if quantity:
                    query = '#' + match[1] + '/-' + rarity + '/' + match[2] + '-' + match[3]
                    extra += '\n\t\t\t[all*] { il_main = ' + query + '; min = ' + str(quantity) + '; max = ' + str(quantity) + '; }'
                    record('vendor_selection', path, b, values['il_main'][0], query + ' x' + str(quantity))
            edits.append((b.end + 1, b.end + 1, extra))
        # More replenishing supplies, within the existing 255-item store ceiling.
        budget = max(0, int(250 - stock_max))
        template = next((a for a in ancestors(store) if 't:template' in a.name), None)
        if template is not None:
            for restock in [b for b in nodes if b.name == 'item_restock' and any(a is template for a in ancestors(b))]:
                for key, value, start, end in fs[id(restock)]:
                    if (key.startswith(('potion_health', 'potion_mana')) or key == 'scroll_resurrect') and re.fullmatch(r'\d+', value):
                        old = int(value)
                        addition = min(budget, max(0, min(20, max(5, old * 2)) - old))
                        if addition:
                            edits.append((start, end, str(old + addition)))
                            budget -= addition
                            record('supply_restock', path, restock, key + '=' + value, str(old + addition))
    if edits:
        packages['Vendors'][path] = edit(text, loot_edits + edits).encode('cp1252')

# One content package prevents full-file overrides between loot and shops.
packages['LootVendors'] = {**packages.pop('RareLoot'), **packages.pop('Vendors')}
out = p / 'build'
out.mkdir(exist_ok=True)
manifest = {'school_xp': 'Used school only; unchanged from original', 'attributes': {'main': 1.35, 'other': 1.0}, 'rare_multiplier': 10, 'unique_multiplier': 5, 'counts': dict(collections.Counter(x['kind'] for x in changes)), 'changes': changes, 'skipped_source_anomalies': skipped, 'packages': []}
for kind, files in packages.items():
    assert files
    for path, raw in files.items():
        target = p / 'source' / kind / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    destination = out / ('DS_OP_' + kind + '_v1.dsres')
    write_tank(destination, files, game / 'DSLOA/Expansion.dsres', 'OP ' + kind + ' v1')
    manifest['packages'].append({'file': destination.name, 'resources': len(files), 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()})
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({k: v for k, v in manifest.items() if k != 'changes'}, indent=2))
