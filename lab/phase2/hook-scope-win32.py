from pathlib import Path
import sys,json,struct
folder=Path(__file__).parent;support=Path(r'Z:\Users\you\Library\Application Support\Dungeon Siege Optimized')
exec((support/'runtime-cache-win32.py').read_text().split('\ntry:\n')[0]);sf=folder/'scope-state.json';entry=0x69f2ff;end=0x69f3a6
try:
 if sys.argv[1]=='remove':
  st=json.loads(sf.read_text());assert st['pid']==pid.value;patch(entry,bytes.fromhex(st['hook']),bytes.fromhex(st['original_prefix']));print('removed');sys.exit(0)
 original=(folder/'scope-loop-original.bin').read_bytes();expected=bytearray(original);base=json.loads((support/'runtime-cache-state.json').read_text());assert base['pid']==pid.value
 expected[38:43]=bytes.fromhex(base['blend']['hook']);assert get(entry,len(original))==bytes(expected)
 va=bind(k,'VirtualAllocEx',c.c_void_p,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD]);addr=va(hp,None,4096,0x3000,4);check(addr)
 prefix=(folder/'scope-prefix.bin').read_bytes();quat=(folder/'quat-scoped.bin').read_bytes();blend=(folder/'blend-scoped.bin').read_bytes();oldblend=(support/'blend-original.bin').read_bytes()
 inner=len(prefix);tail=inner+len(original);qoff=(tail+16+15)//16*16;boff=(qoff+len(quat)+15)//16*16;oldoff=(boff+len(blend)+15)//16*16
 loop=bytearray(original);assert loop[33]==0xe8 and loop[147]==0xe8
 struct.pack_into('<i',loop,34,qoff-(inner+38))
 loop[38:114]=b'\xe8'+struct.pack('<i',boff-(inner+43))+b'\xe9'+struct.pack('<i',114-48)+b'\x90'*66
 struct.pack_into('<i',loop,148,0x69fa05-(addr+inner+152))
 assert quat[-4:]==bytes.fromhex('44332211');quat=quat[:-4]+struct.pack('<i',0x535f3b+7-(addr+qoff+len(quat)))
 assert blend.count(bytes.fromhex('55443322'))==1;blend=blend.replace(bytes.fromhex('55443322'),struct.pack('<I',addr+oldoff))
 code=prefix+bytes(loop)+bytes.fromhex('0fae54240483c408')+b'\xe9'+struct.pack('<i',end-(addr+tail+13))
 code+=b'\x90'*(qoff-len(code))+quat;code+=b'\x90'*(boff-len(code))+blend;code+=b'\x90'*(oldoff-len(code))+oldblend
 assert len(code)<4096;put(addr,code);previous=w.DWORD();check(protect(hp,addr,4096,0x20,c.byref(previous)));check(flush(hp,addr,len(code)))
 hook=b'\xe9'+struct.pack('<i',addr-(entry+5));patch(entry,original[:5],hook)
 st={'pid':pid.value,'entry':entry,'code':addr,'hook':hook.hex(),'original_prefix':original[:5].hex(),'inner_offset':inner,'quat_offset':qoff,'blend_offset':boff};sf.write_text(json.dumps(st,indent=2));print(json.dumps(st))
finally:close(hp)
