from pathlib import Path
import hashlib,json,shutil
p=Path(__file__).resolve().parent;support=Path.home()/'Library/Application Support/Dungeon Siege Optimized';game=Path.home()/'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
source=p/'22-native-fastpath/DSLOA.exe';assert sha(source)=='3b222ce4f8214a182112ef65db869cfe1132f4b3b4ff80999eaefabeb704c919'
assert json.loads((p/'28-cursor-validation/validation.json').read_text())['passed']
assert sha(game/'DSLOA.exe')=='1cb4b77d520dea33f14919129fd5bbf9f2cdb94d38cbb96bbd288ccdaa5f2d24'
for path,wanted in json.loads((p.parent/'phase6/protected-saves.json').read_text()).items():assert sha(Path(path))==wanted
before=p/'release-before';before.mkdir(exist_ok=True)
for f in [game/'DSLOA.exe',support/'static-manifest.json',support/'static-patches.json',support/'check-install.py',support/'README.md',p.parent/'STATUS.md']:
 target=before/('STATUS.md'if f.name=='STATUS.md'else f.name);assert not target.exists();shutil.copy2(f,target)
shutil.copy2(source,game/'DSLOA.exe')
m=json.loads((support/'static-manifest.json').read_text());m['DSLOA.exe']=sha(source);(support/'static-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
patch=json.loads((support/'static-patches.json').read_text());entry=next(f for f in patch['files']if f['file'].endswith('DSLOA.exe'));entry['sha256']=m['DSLOA.exe'];entry['hooks']+=json.loads((p/'22-native-fastpath/manifest.json').read_text())['hooks'];entry['source_builds'].append('phase7/22-native-fastpath')
patch['level']='native-cursor-without-software-surface-copies';patch['validation']['cursor_frame_timing']={}
for run in ['25-walk-baseline','26-walk-fastpath','27-walk-fastpath-repeat']:
 d=json.loads((p/run/'frame-clock.json').read_text());patch['validation']['cursor_frame_timing'][run]={k:d[k]for k in ['mean_fps','p95_ms','p99_ms','worst_ms']};patch['validation']['cursor_frame_timing'][run]['over_80ms']=sum(v>80 for v in d['frame_ms'])
patch['validation']['cursor_input']=json.loads((p/'28-cursor-validation/validation.json').read_text())
(support/'static-patches.json').write_text(json.dumps(patch,indent=2)+'\n')
f=support/'check-install.py';f.write_text(f.read_text().replace('Validated deep-forest optimized build and corrected native cursor.','Validated optimized build with native-cursor surface-copy bypass.'))
for name,wanted in m.items():assert sha(game/name)==wanted
result={'sha256':m['DSLOA.exe'],'game':str(game),'jump_hooks':sum(len(f['hooks'])for f in patch['files']),'direct_patches':sum(len(f.get('direct_patches',[]))for f in patch['files']),'protected_saves_unchanged':True,'profiler_installed':False}
(p/'installed-release.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
