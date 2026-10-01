"""Promote the numerically checked normal-loop optimization after gameplay tests."""
from pathlib import Path
import hashlib,json,shutil
p=Path(__file__).resolve().parent;support=Path.home()/'Library/Application Support/Dungeon Siege Optimized';game=Path.home()/'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
source=p/'05-normal-scope/DSLOA.exe';expected='0e33eaf33112467da7cafc26cb33600c0526f8b56f65fd5312c3f29433a49f3c'
assert sha(source)==expected and sha(game/'DSLOA.exe')=='3b222ce4f8214a182112ef65db869cfe1132f4b3b4ff80999eaefabeb704c919'
validation=json.loads((p/'05-normal-scope/validation.json').read_text());assert validation['all_output_bits_match'] and validation['complete_loop_comparisons']==14400
assert json.loads((p/'05-normal-scope/static-validation.json').read_text())['frame_profiler_absent']
runs=['08-steady-base','09-steady-scope','10-steady-scope-repeat','11-steady-base-repeat','12-walk-base','13-walk-scope','15-walk-scope-repeat']
timing={}
for n in runs:
 d=json.loads((p/n/'frame-clock.json').read_text());assert d['frames']>1000
 timing[n]={k:d[k] for k in ['mean_fps','p95_ms','p99_ms','worst_ms']};timing[n]['over_80ms']=sum(v>80 for v in d['frame_ms'])
base=(timing[runs[0]]['mean_fps']+timing[runs[3]]['mean_fps'])/2
candidate=(timing[runs[1]]['mean_fps']+timing[runs[2]]['mean_fps'])/2
assert candidate>base
protected=json.loads((p.parent/'phase6/protected-saves.json').read_text())
for f,wanted in protected.items():assert sha(Path(f))==wanted
pins=json.loads((support/'static-manifest.json').read_text())
for name,wanted in pins.items():assert sha(game/name)==wanted
before=p/'release-before';before.mkdir(exist_ok=True)
for f in [game/'DSLOA.exe',support/'static-manifest.json',support/'static-patches.json',support/'check-install.py',support/'README.md',p.parent/'STATUS.md']:
 target=before/f.name;assert not target.exists();shutil.copy2(f,target)
shutil.copy2(source,game/'DSLOA.exe')
pins['DSLOA.exe']=expected;(support/'static-manifest.json').write_text(json.dumps(pins,indent=2)+'\n')
patch=json.loads((support/'static-patches.json').read_text());entry=next(f for f in patch['files'] if f['file'].endswith('DSLOA.exe'))
entry['sha256']=expected;entry['hooks']+=json.loads((p/'05-normal-scope/manifest.json').read_text())['hooks'];entry['source_builds'].append('phase8/05-normal-scope')
patch['level']='native-cursor-and-scoped-normal-transforms';patch['validation']['normal_loop']=validation;patch['validation']['normal_loop_timing']=timing
(support/'static-patches.json').write_text(json.dumps(patch,indent=2)+'\n')
f=support/'check-install.py';f.write_text(f.read_text().replace('Validated optimized build with native-cursor surface-copy bypass.','Validated optimized build with native cursor and scoped normal transforms.'))
for name,wanted in pins.items():assert sha(game/name)==wanted
result={'sha256':expected,'game':str(game),'jump_hooks':sum(len(f['hooks']) for f in patch['files']),'direct_patches':sum(len(f.get('direct_patches',[])) for f in patch['files']),'protected_saves_unchanged':True,'profiler_installed':False,'steady_baseline_mean_fps':base,'steady_candidate_mean_fps':candidate,'steady_improvement_percent':(candidate/base-1)*100}
(p/'installed-release.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
