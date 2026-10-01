from pathlib import Path
import hashlib,json,shutil,struct
p=Path(__file__).resolve().parent;support=Path.home()/'Library/Application Support/Dungeon Siege Optimized';game=Path.home()/'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
before=p/'release-before';before.mkdir(exist_ok=True)
for f in [game/'DSLOA.exe',support/'static-manifest.json',support/'static-patches.json',support/'check-install.py',support/'README.md']:
 assert not (before/f.name).exists();shutil.copy2(f,before/f.name)
assert sha(game/'DSLOA.exe')=='8f3510621fd0e9c195ca69a140d2d4020d75f8e01e81b4ac78a45b8908513700'
source=p/'13-bounds/DSLOA.exe';shutil.copy2(source,game/'DSLOA.exe')
m=json.loads((support/'static-manifest.json').read_text());m['DSLOA.exe']=sha(source);(support/'static-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
patch=json.loads((support/'static-patches.json').read_text());f=next(f for f in patch['files'] if f['file'].endswith('DSLOA.exe'));hooks={h['entry']:h for h in f['hooks']}
for build in ['03-native-arrow','04-triangle','05-cursor-fixed','08-slerp','13-bounds']:
 for h in json.loads((p/build/'manifest.json').read_text())['hooks']:hooks[h['entry']]=h
f.update(sha256=m['DSLOA.exe'],hooks=list(hooks.values()),source_builds=['phase6/'+x for x in ['03-native-arrow','04-triangle','05-cursor-fixed','08-slerp','13-bounds']])
f['direct_patches']=json.loads((p/'05-cursor-fixed/manifest.json').read_text())['direct_patches']
patch['level']='deep-forest-native-cursor';patch['validation']={'slerp':json.loads((p/'08-slerp/validation.json').read_text()),'bounds':json.loads((p/'13-bounds/validation.json').read_text())}
(support/'static-patches.json').write_text(json.dumps(patch,indent=2)+'\n')
checker=support/'check-install.py';s=checker.read_text().replace('Validated optimized build with native arrow and triangle fast path.','Validated deep-forest optimized build and corrected native cursor.');checker.write_text(s)
for name,wanted in m.items():assert sha(game/name)==wanted
for path,wanted in json.loads((p/'protected-saves.json').read_text()).items():assert sha(Path(path))==wanted
(p/'installed-release.json').write_text(json.dumps({'sha256':m['DSLOA.exe'],'game':str(game),'jump_hooks':sum(len(f['hooks'])for f in patch['files']),'direct_patches':1,'protected_saves_unchanged':True},indent=2));print((p/'installed-release.json').read_text())
