"""Install the verified arrow/triangle build into the existing optimized wrapper."""
from pathlib import Path
import hashlib, json, os, shutil, struct, subprocess
import pefile

p = Path(__file__).resolve().parent
support = Path.home() / 'Library/Application Support/Dungeon Siege Optimized'
game = Path.home() / 'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
build = p / '08-arrow-triangle'
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
old = json.loads((support / 'static-manifest.json').read_text())
for name, wanted in old.items():
    assert digest(game / name) == wanted, name
assert old == json.loads((p / 'release-before/static-manifest.json').read_text())
latest = json.loads((build / 'manifest.json').read_text())
assert digest(build / 'DSLOA.exe') == latest['sha256']
validation = json.loads((build / 'validation.json').read_text())
assert validation['comparisons'] == 180000 and validation['exact_boolean_and_all_buffer_bytes']
patches = json.loads((support / 'static-patches.json').read_text())
patches['level'] = 'native-arrow-triangle'
exe = next(f for f in patches['files'] if Path(f['file']).name == 'DSLOA.exe')
arrow = json.loads((p / '07-native-arrow/manifest.json').read_text())
exe['layers'] = [
    'phase2/static-raybox', 'phase5/07-native-arrow', 'phase5/08-arrow-triangle'
]
exe['hooks'] += arrow['hooks'] + latest['hooks']
exe['sha256'] = latest['sha256']
exe['code_bytes'] += arrow['code_bytes'] + latest['code_bytes']
exe['cache_bytes'] += arrow['cache_bytes']
exe.pop('code_section_rva', None)
exe.pop('data_section_rva', None)
for f in patches['files']:
    f['file'] = str(game / Path(f['file']).name)
pe = pefile.PE(str(build / 'DSLOA.exe'))
for hook in exe['hooks']:
    entry, target = int(hook['entry'], 16), int(hook['target'], 16)
    data = pe.get_data(entry - pe.OPTIONAL_HEADER.ImageBase, 5)
    assert data[0] == 0xe9 and entry + 5 + struct.unpack('<i', data[1:])[0] == target, hook
assert sum(len(f['hooks']) for f in patches['files']) == 17
old['DSLOA.exe'] = latest['sha256']

def replace(path, data):
    temporary = path.with_name(path.name + '.phase5-new')
    temporary.write_bytes(data)
    if path.exists():
        shutil.copymode(path, temporary)
    os.replace(temporary, path)

replace(game / 'DSLOA.exe', (build / 'DSLOA.exe').read_bytes())
replace(support / 'static-patches.json', (json.dumps(patches, indent=2) + '\n').encode())
checker = (support / 'check-install.py').read_text().replace(
    'Validated fifteen preloaded optimizations.',
    'Validated optimized build with native arrow and triangle fast path.')
replace(support / 'check-install.py', checker.encode())
replace(support / 'static-manifest.json', (json.dumps(old, indent=2) + '\n').encode())
subprocess.run(['/usr/bin/python3', str(support / 'check-install.py')], check=True)
for record in json.loads((p / 'release-protected-files.json').read_text()):
    assert digest(Path(record['path'])) == record['sha256'], record['path']
(p / 'installed-release.json').write_text(json.dumps({
    'sha256': latest['sha256'], 'hooks': 17, 'instrumentation': False,
    'original_game_and_saves_unchanged': True,
    'backup': str(p / 'release-before'),
    'launcher': str(Path.home() / 'Applications/Dungeon Siege Optimized.app')
}, indent=2) + '\n')
print('Installed verified release; original game and saved games unchanged.')
