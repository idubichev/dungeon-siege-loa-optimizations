from pathlib import Path
import json,hashlib,struct,pefile
p=Path(__file__).resolve().parent;support=Path.home()/'Library/Application Support/Dungeon Siege Optimized'
old=p.parent/'phase7/22-native-fastpath/DSLOA.exe';new=p/'05-normal-scope/DSLOA.exe'
a=pefile.PE(str(old));b=pefile.PE(str(new));ab=old.read_bytes();bb=new.read_bytes()
changed=[]
for sec in a.sections:
 for i,(x,y) in enumerate(zip(ab[sec.PointerToRawData:sec.PointerToRawData+sec.SizeOfRawData],bb[sec.PointerToRawData:sec.PointerToRawData+sec.SizeOfRawData])):
  if x!=y:changed.append(0x400000+sec.VirtualAddress+i)
assert changed and all(0x69f76f<=va<0x69f774 for va in changed),list(map(hex,changed))
patch=json.loads((support/'static-patches.json').read_text());hooks=next(f['hooks'] for f in patch['files'] if f['file'].endswith('DSLOA.exe'))
for h in hooks+json.loads((p/'05-normal-scope/manifest.json').read_text())['hooks']:
 va=int(h['entry'],16);v=b.get_data(va-0x400000,5);assert v[0]==0xe9 and va+5+struct.unpack('<i',v[1:])[0]==int(h['target'],16)
assert b.get_data(0x676a6c-0x400000,5)==a.get_data(0x676a6c-0x400000,5) and b.get_data(0x676a6c-0x400000,1)!=b'\xe9'
assert b.get_data(0x415d2d-0x400000,11)==b'\x90'*11
assert b.get_data(0x67e7aa-0x400000,5)==a.get_data(0x67e7aa-0x400000,5)
protected=json.loads((p.parent/'phase6/protected-saves.json').read_text())
for f,wanted in protected.items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==wanted
r={'existing_exe_hooks_preserved':len(hooks),'new_hooks':1,'modified_existing_code_addresses':list(map(hex,changed)),'frame_profiler_absent':True,'cursor_fix_preserved':True,'streaming_sleep_unchanged':True,'protected_saves_unchanged':len(protected),'sha256':hashlib.sha256(bb).hexdigest()}
(p/'05-normal-scope/static-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
