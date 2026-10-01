"""Back up and atomically replace the on-disk build; never attach to the game."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

root = Path(__file__).resolve().parent
support = Path.home() / 'Library/Application Support/Dungeon Siege Optimized'
game = Path.home() / 'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
meta = json.loads((root / 'patch.json').read_text())
assert json.loads((root / 'validation.json').read_text())['status'] == 'passed'
digest = lambda data: hashlib.sha256(data).hexdigest()
manifest = json.loads((support / 'static-manifest.json').read_text())
for name, wanted in manifest.items():
    assert digest((game / name).read_bytes()) == wanted, name
assert manifest['DSLOA.exe'] == meta['baseline_sha256']
candidate = (root / 'DSLOA-xp135.exe').read_bytes()
assert digest(candidate) == meta['candidate_sha256']
backup = root / 'backup'
backup.mkdir(exist_ok=False)
for src in [game / 'DSLOA.exe', support / 'static-manifest.json', support / 'static-patches.json']:
    shutil.copy2(src, backup / src.name)
assert digest((backup / 'DSLOA.exe').read_bytes()) == meta['baseline_sha256']

def atomic_bytes(path, data):
    temporary = path.with_name(path.name + '.xp135-new')
    assert not temporary.exists()
    shutil.copy2(path, temporary)
    temporary.write_bytes(data)
    os.replace(temporary, path)

# Atomic inode replacement leaves the running process's mapped image intact.
atomic_bytes(game / 'DSLOA.exe', candidate)
manifest['DSLOA.exe'] = meta['candidate_sha256']
atomic_bytes(support / 'static-manifest.json', (json.dumps(manifest, indent=2) + '\n').encode())
patches = json.loads((support / 'static-patches.json').read_text())
entry = next(f for f in patches['files'] if Path(f['file']) == game / 'DSLOA.exe')
entry['sha256'] = meta['candidate_sha256']
entry['code_bytes'] += len(bytes.fromhex(meta['code']))
entry['hooks'].append(dict(name='combat-xp-135-percent', entry=meta['entry'], target=meta['target'],
                           original_prefix=meta['original_prefix']))
patches['combat_xp_multiplier'] = 1.35
patches['combat_xp_patch'] = str(root / 'patch.json')
atomic_bytes(support / 'static-patches.json', (json.dumps(patches, indent=2) + '\n').encode())
subprocess.run(['python3', str(support / 'check-install.py')], check=True)
(root / 'installed.json').write_text(json.dumps(dict(status='installed_for_next_launch',
    executable=str(game / 'DSLOA.exe'), sha256=meta['candidate_sha256'], backup=str(backup),
    running_session_modified=False, save_files_modified=False, in_game_test=False), indent=2) + '\n')
print('Installed 1.35x combat XP for next launch; current session and saves untouched.')
