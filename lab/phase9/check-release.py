from pathlib import Path
import struct,json,hashlib,pefile
p=Path(__file__).resolve().parent;s=Path.home()/'Library/Application Support/Dungeon Siege Optimized';folder=p/'13-transform-cache';old=pefile.PE(str(p.parent/'phase8/05-normal-scope/DSLOA.exe'));new=pefile.PE(str(folder/'DSLOA.exe'));ib=old.OPTIONAL_HEADER.ImageBase
patches=json.loads((s/'static-patches.json').read_text());entry=next(f for f in patches['files']if f['file'].endswith('DSLOA.exe'));m=json.loads((folder/'manifest.json').read_text())
for h in entry['hooks']+m['hooks']:
 a=int(h['entry'],16);b=new.get_data(a-ib,5);assert b[0]==0xe9 and a+5+struct.unpack('<i',b[1:])[0]==int(h['target'],16),h
changed=[]
for sec in old.sections:
 if sec.Characteristics&0x20000000:
  a=sec.VirtualAddress;left=old.get_data(a,sec.Misc_VirtualSize);right=new.get_data(a,len(left));changed.extend(ib+a+i for i,(x,y)in enumerate(zip(left,right))if x!=y)
assert changed==list(range(0x67907e,0x679083)),[hex(a)for a in changed]
assert new.get_data(0x676a6c-ib,9).hex()=='558bec81eca0000000'
for f,wanted in json.loads((p.parent/'phase6/protected-saves.json').read_text()).items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==wanted
r={'existing_exe_hooks_preserved':len(entry['hooks']),'new_hooks':len(m['hooks']),'modified_existing_code_addresses':[hex(a)for a in changed],'frame_profiler_absent':True,'cursor_fix_preserved':True,'protected_saves_unchanged':3,'sha256':hashlib.sha256((folder/'DSLOA.exe').read_bytes()).hexdigest()}
(folder/'static-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
