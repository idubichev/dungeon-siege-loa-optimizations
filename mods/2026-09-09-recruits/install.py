"""Install the paired recruitment resources and native helper while DS1 is closed."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

root = Path(__file__).resolve().parent
support = Path.home() / 'Library/Application Support/Dungeon Siege Optimized'
game = Path.home() / 'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
digest = lambda data: hashlib.sha256(data).hexdigest()
meta = json.loads((root / 'patch.json').read_text())
assert json.loads((root / 'validation.json').read_text())['status'] == 'passed'
running = subprocess.run(['pgrep', '-fl', r'DSLOA[.]exe|DungeonSiege[.]exe'], capture_output=True, text=True)
assert running.returncode == 1, 'Close Dungeon Siege before installing the paired patch.'
manifest = json.loads((support / 'static-manifest.json').read_text())
for name, wanted in manifest.items():
    assert digest((game / name).read_bytes()) == wanted, name
assert manifest['DSLOA.exe'] == meta['baseline_sha256']
candidate = (root / 'DSLOA-recruits.exe').read_bytes()
archive = (root / 'DS_Companion_Bonus.dsres').read_bytes()
assert digest(candidate) == meta['candidate_sha256']
assert digest(archive) == meta['archive_sha256']
archive_name = 'DSLOA/DS_Companion_Bonus.dsres'
assert not (game / archive_name).exists()

backup = root / 'backup'
backup.mkdir(exist_ok=False)
originals = [game / 'DSLOA.exe', support / 'static-manifest.json', support / 'static-patches.json']
for path in originals:
    shutil.copy2(path, backup / path.name)

manifest['DSLOA.exe'] = meta['candidate_sha256']
manifest[archive_name] = meta['archive_sha256']
patches = json.loads((support / 'static-patches.json').read_text())
entry = next(row for row in patches['files'] if Path(row['file']) == game / 'DSLOA.exe')
entry['sha256'] = meta['candidate_sha256']
entry['code_bytes'] += len(bytes.fromhex(meta['code']))
entry['hooks'].append(dict(name='recruit-natural-attributes-plus-two', kind='call',
                           entry=meta['entry'], target=meta['target'], original_prefix=meta['original_prefix']))
patches['recruitment_bonus'] = dict(attributes=2, campaign='Ehb', once_per_companion=True,
                                   patch=str(root / 'patch.json'), in_game_test=False)

def atomic_write(path, data):
    temporary = path.with_name(path.name + '.recruits-new')
    assert not temporary.exists()
    temporary.write_bytes(data)
    if path.exists():
        shutil.copystat(path, temporary)
    os.replace(temporary, path)

try:
    atomic_write(game / 'DSLOA.exe', candidate)
    atomic_write(game / archive_name, archive)
    atomic_write(support / 'static-manifest.json', (json.dumps(manifest, indent=2) + '\n').encode())
    atomic_write(support / 'static-patches.json', (json.dumps(patches, indent=2) + '\n').encode())
    subprocess.run(['/usr/bin/python3', str(support / 'check-install.py')], check=True)
except BaseException:
    for path in originals:
        atomic_write(path, (backup / path.name).read_bytes())
    (game / archive_name).unlink(missing_ok=True)
    raise

(root / 'installed.json').write_text(json.dumps(dict(status='installed_for_next_launch',
    executable_sha256=meta['candidate_sha256'], archive_sha256=meta['archive_sha256'],
    backup=str(backup), game_was_closed=True, save_files_modified=False, in_game_test=False), indent=2) + '\n')
print('Installed Ehb recruitment bonus; existing saves untouched; no game launched.')
