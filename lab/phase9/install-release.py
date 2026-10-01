"""Install the validated phase9 transform optimization, preserving phase8 for rollback."""
from pathlib import Path
import hashlib,json,shutil,pefile,struct
p=Path(__file__).resolve().parent;support=Path.home()/'Library/Application Support/Dungeon Siege Optimized';game=Path.home()/'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege';private=Path.home()/'Applications/Dungeon Siege Profile Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
folder=p/'13-transform-cache';source=folder/'DSLOA.exe';expected='9c00538f1bea22d9a70d5806d2025d409e3919c087c6ff94e245084a811e9545'
assert sha(source)==expected and sha(game/'DSLOA.exe')=='0e33eaf33112467da7cafc26cb33600c0526f8b56f65fd5312c3f29433a49f3c'
static=json.loads((folder/'static-validation.json').read_text());assert static['frame_profiler_absent'] and static['existing_exe_hooks_preserved']==18
cache=json.loads((folder/'cache-validation.json').read_text());assert cache['exact_comparisons']==8004 and cache['cache_hits']==4000
kernel=json.loads((folder/'kernel-validation.json').read_text());assert kernel['comparisons']==36000 and kernel['exact_output_bits']
timing={}
for n in ['01-capped-baseline','19-baseline-repeat','15-cache-benchmark','20-cache-repeat','21-walk-baseline','22-walk-cache']:
 d=json.loads((p/n/'frame-clock.json').read_text());assert d['frames']>1000
 timing[n]={k:d[k]for k in ['mean_fps','p95_ms','p99_ms','worst_ms']};timing[n]['over_80ms']=sum(v>80 for v in d['frame_ms'])
base=(timing['01-capped-baseline']['mean_fps']+timing['19-baseline-repeat']['mean_fps'])/2
candidate=(timing['15-cache-benchmark']['mean_fps']+timing['20-cache-repeat']['mean_fps'])/2
assert candidate>base*1.02
assert timing['22-walk-cache']['mean_fps']>timing['21-walk-baseline']['mean_fps']*.95
for record in json.loads((p.parent/'phase5/release-protected-files.json').read_text()):assert sha(Path(record['path']))==record['sha256']
for f,wanted in json.loads((p.parent/'phase6/protected-saves.json').read_text()).items():assert sha(Path(f))==wanted
pins=json.loads((support/'static-manifest.json').read_text())
for name,wanted in pins.items():assert sha(game/name)==wanted
mods=p.parents[2]/'mods/2026-09-06/build'
for name in ['DS_OP_Attributes_v1.dsres','DS_OP_LootVendors_v1.dsres']:assert sha(game/'DSLOA'/name)==sha(mods/name)
for g in [game,private]:assert 'dxgi.maxFrameRate = 120' in (g/'dxvk.conf').read_text()
backup=p/'release-before';backup.mkdir(exist_ok=True)
for f in [game/'DSLOA.exe',support/'static-manifest.json',support/'static-patches.json',support/'check-install.py',support/'README.md',p.parent/'STATUS.md']:
 target=backup/f.name;assert not target.exists();shutil.copy2(f,target)
shutil.copy2(source,game/'DSLOA.exe');shutil.copy2(source,private/'DSLOA.exe')
pins['DSLOA.exe']=expected;(support/'static-manifest.json').write_text(json.dumps(pins,indent=2)+'\n')
patch=json.loads((support/'static-patches.json').read_text());entry=next(f for f in patch['files']if f['file'].endswith('DSLOA.exe'));entry['sha256']=expected;entry['hooks']+=json.loads((folder/'manifest.json').read_text())['hooks'];entry['source_builds'].append('phase9/13-transform-cache')
patch['level']='native-cursor-scoped-normals-and-batched-object-transforms';patch['validation']['object_transform_cache']=cache;patch['validation']['object_transform_kernel']=kernel;patch['validation']['object_transform_timing']=timing
(support/'static-patches.json').write_text(json.dumps(patch,indent=2)+'\n')
f=support/'check-install.py';f.write_text(f.read_text().replace('Validated optimized build with native cursor and scoped normal transforms.','Validated optimized build with native cursor, scoped normals and batched object transforms.'))
for name,wanted in pins.items():assert sha(game/name)==wanted
result={'sha256':expected,'game':str(game),'jump_hooks':sum(len(f['hooks'])for f in patch['files']),'direct_patches':sum(len(f.get('direct_patches',[]))for f in patch['files']),'protected_files_unchanged':True,'mods_unchanged':True,'profiler_installed':False,'fps_cap':120,'object_detail_percent':100,'steady_baseline_mean_fps':base,'steady_candidate_mean_fps':candidate,'steady_improvement_percent':(candidate/base-1)*100,'timing':timing}
(p/'installed-release.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
