"""Install both vendor changes atomically per file, with complete rollback on failure."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

root=Path(__file__).resolve().parent
support=Path.home()/'Library/Application Support/Dungeon Siege Optimized'
game=Path.home()/'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
digest=lambda b:hashlib.sha256(b).hexdigest()
meta=json.loads((root/'patch.json').read_text())
resources=json.loads((root/'resources.json').read_text())
assert json.loads((root/'validation.json').read_text())['status']=='passed'
running=subprocess.run(['pgrep','-fl',r'DSLOA[.]exe|DungeonSiege[.]exe'],capture_output=True,text=True)
assert running.returncode==1,'Save and close Dungeon Siege first.'
manifest=json.loads((support/'static-manifest.json').read_text())
for name,wanted in manifest.items():assert digest((game/name).read_bytes())==wanted,name
assert manifest['DSLOA.exe']==meta['baseline_sha256']
archive_name='DSLOA/DS_OP_LootVendors_v1.dsres'
assert digest((game/archive_name).read_bytes())==resources['previous_archive_sha256']
exe=(root/'DSLOA-vendors.exe').read_bytes()
archive=(root/'DS_OP_LootVendors_v2.dsres').read_bytes()
assert digest(exe)==meta['candidate_sha256']
assert digest(archive)==resources['archive_sha256']
originals=[game/'DSLOA.exe',game/archive_name,support/'static-manifest.json',support/'static-patches.json']
backup=root/'backup';backup.mkdir(exist_ok=False)
for path in originals:shutil.copy2(path,backup/path.name)

def atomic(path,data):
    temporary=path.with_name(path.name+'.vendors-new')
    assert not temporary.exists()
    temporary.write_bytes(data)
    shutil.copystat(path,temporary)
    os.replace(temporary,path)

manifest['DSLOA.exe']=meta['candidate_sha256']
manifest[archive_name]=resources['archive_sha256']
patches=json.loads((support/'static-patches.json').read_text())
row=next(r for r in patches['files'] if Path(r['file'])==game/'DSLOA.exe')
row['sha256']=meta['candidate_sha256'];row['code_bytes']+=len(bytes.fromhex(meta['code']))-322
row['hooks']=[h for h in row['hooks'] if h['name']!='vendor-reroll-after-last-shopper']
row['hooks'].append(dict(name='vendor-reroll-after-last-shopper',kind='call',entry=meta['entry'],target=meta['target'],original_prefix=meta['original_prefix']))
patches['vendors']=dict(version=3,reroll='last shopper exits',buyback_items_preserved=True,
                       magic_rolls=True,generate_before_remove=True,live_clone_path=True,report=str(root/'resources.json'),patch=str(root/'patch.json'),in_game_test=False)
try:
    atomic(game/'DSLOA.exe',exe)
    atomic(game/archive_name,archive)
    atomic(support/'static-manifest.json',(json.dumps(manifest,indent=2)+'\n').encode())
    atomic(support/'static-patches.json',(json.dumps(patches,indent=2)+'\n').encode())
    subprocess.run(['/usr/bin/python3',str(support/'check-install.py')],check=True)
except BaseException:
    for path in originals:atomic(path,(backup/path.name).read_bytes())
    raise
(root/'installed.json').write_text(json.dumps(dict(status='installed_for_next_launch',
    executable_sha256=meta['candidate_sha256'],archive_sha256=resources['archive_sha256'],
    game_was_closed=True,save_files_modified=False,in_game_test=False),indent=2)+'\n')
print('Installed guarded live-generation repair and explicit magic/rare/unique vendor rolls. In-game validation pending.')
