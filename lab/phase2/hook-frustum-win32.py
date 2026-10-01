from pathlib import Path
import sys,json,struct
folder=Path(__file__).parent
support=Path(r'Z:\Users\you\Library\Application Support\Dungeon Siege Optimized')
exec((support/'runtime-cache-win32.py').read_text().split('\ntry:\n')[0])
sf=folder/'frustum-state.json';entry=0x684d7f;end=0x684f54
try:
 if sys.argv[1]=='remove':
  st=json.loads(sf.read_text());assert st['pid']==pid.value
  patch(entry,bytes.fromhex(st['hook']),bytes.fromhex(st['original_prefix']));print('removed');sys.exit(0)
 original=(folder/'frustum-original.bin').read_bytes();assert get(entry,len(original))==original
 va=bind(k,'VirtualAllocEx',c.c_void_p,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD]);addr=va(hp,None,4096,0x3000,4);check(addr)
 code=bytearray.fromhex('51528d7efcff35e8a572005753e80000000083c40c83f8ff0f84000000008945105a59e9000000005a59e900000000')
 # call at 12; jz at 23; successful tail jump at 34; fallback jump at 41.
 assert code[13]==0xe8 and code[24:26]==b'\x0f\x84' and code[35]==0xe9 and code[42]==0xe9
 body=(folder/'frustum-sse.bin').read_bytes();bodyoffset=64;oldoffset=(bodyoffset+len(body)+15)//16*16
 struct.pack_into('<i',code,14,bodyoffset-18);struct.pack_into('<i',code,26,40-30)
 struct.pack_into('<i',code,36,end-(addr+40));struct.pack_into('<i',code,43,oldoffset-47)
 code.extend(b'\x90'*(bodyoffset-len(code)));code.extend(body);code.extend(b'\x90'*(oldoffset-len(code)))
 old=bytearray(original)
 for r in json.loads((folder/'frustum-original-relocations.json').read_text()):
  if 'relative_to' in r:
   target={'vec-ctor':0x47d209,'vec-sub':0x49efe8,'vec-dot':0x64af6e}[r['target']]
   struct.pack_into('<I',old,r['offset'],(target-(addr+oldoffset+r['relative_to']))&0xffffffff)
 code.extend(old);code.extend(b'\xe9'+struct.pack('<i',end-(addr+len(code)+5)))
 put(addr,bytes(code));previous=w.DWORD();check(protect(hp,addr,4096,0x20,c.byref(previous)));check(flush(hp,addr,len(code)))
 hook=b'\xe9'+struct.pack('<i',addr-(entry+5));patch(entry,original[:5],hook)
 st={'pid':pid.value,'entry':entry,'code':addr,'hook':hook.hex(),'original_prefix':original[:5].hex()};sf.write_text(json.dumps(st,indent=2));print(json.dumps(st))
finally:close(hp)
