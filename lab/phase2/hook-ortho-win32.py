from pathlib import Path
import sys,json,struct
folder=Path(__file__).parent;support=Path(r'Z:\Users\you\Library\Application Support\Dungeon Siege Optimized')
exec((support/'runtime-cache-win32.py').read_text().split('\ntry:\n')[0]);sf=folder/'ortho-state.json';entry=0x43e82d
try:
 if sys.argv[1]=='remove':
  st=json.loads(sf.read_text());assert st['pid']==pid.value
  patch(entry,bytes.fromhex(st['hook']),bytes.fromhex(st['original_prefix']));print('removed');sys.exit(0)
 original=(folder/'ortho-original.bin').read_bytes();assert get(entry,len(original))==original
 va=bind(k,'VirtualAllocEx',c.c_void_p,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD]);addr=va(hp,None,4096,0x3000,4);check(addr)
 code=bytearray((folder/'ortho-sse.bin').read_bytes());
 for r in json.loads((folder/'ortho-sse-relocations.json').read_text()):struct.pack_into('<I',code,r['offset'],addr+r['code_offset'])
 code=bytes(code);offset=(len(code)+15)//16*16;assert code.count(bytes.fromhex('55443322'))==1
 code=code.replace(bytes.fromhex('55443322'),struct.pack('<I',addr+offset));code+=b'\x90'*(offset-len(code))+original
 put(addr,code);previous=w.DWORD();check(protect(hp,addr,4096,0x20,c.byref(previous)));check(flush(hp,addr,len(code)))
 hook=b'\xe9'+struct.pack('<i',addr-(entry+5));patch(entry,original[:5],hook)
 st={'pid':pid.value,'entry':entry,'code':addr,'hook':hook.hex(),'original_prefix':original[:5].hex()};sf.write_text(json.dumps(st,indent=2));print(json.dumps(st))
finally:close(hp)
