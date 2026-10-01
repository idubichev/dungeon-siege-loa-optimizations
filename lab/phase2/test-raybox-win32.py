import ctypes as c,struct,random,json,math
from pathlib import Path
p=Path(__file__).parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(b):
 a=k.VirtualAlloc(None,4096,0x3000,0x40);assert a;c.memmove(a,b,len(b));return a
ob=bytearray((p/'raybox-original.bin').read_bytes());constants=[]
for r in json.loads((p/'raybox-original-relocations.json').read_text()):
 v=c.create_string_buffer(bytes.fromhex(r['bytes']));constants.append(v);struct.pack_into('<I',ob,r['offset'],c.addressof(v))
oa=alloc(bytes(ob));body=bytearray((p/'raybox-sse.bin').read_bytes());addr=alloc(bytes(body))
for r in json.loads((p/'raybox-sse-relocations.json').read_text()):struct.pack_into('<I',body,r['offset'],(addr if r['target']=='code' else oa)+r['value'])
c.memmove(addr,bytes(body),len(body));fn=c.CFUNCTYPE(c.c_ubyte,*([c.c_void_p]*5));old,new=fn(oa),fn(addr)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')));getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')));getcsr=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec040fae1c248b042483c404c3')));saved=getcw();rng=random.Random(6477);checks=0
try:
 for mode in [0x7f,0x47f,0x87f,0xc7f,0x27f,0x67f,0xa7f,0xe7f,0x37f]:
  setcw(mode)
  for i in range(10000):
   scale=[1.0,1000.0,1e-20,1e20][i%4];lo=[rng.uniform(-5,-1)*scale for _ in range(3)];hi=[rng.uniform(1,5)*scale for _ in range(3)];origin=[rng.uniform(-10,10)*scale for _ in range(3)];direction=[rng.uniform(-1,1)*scale for _ in range(3)]
   if i%7==0:direction[i%3]=0
   if i%11==0:origin[i%3]=lo[i%3]
   data=struct.pack('<15f',*(lo+hi+origin+direction+[31,32,33]));bufs=[c.create_string_buffer(data),c.create_string_buffer(data)];dst=[48,0,12,24,36][(i//10)%5] if i%10==0 else 48
   if i%17==0:
    for b in bufs:struct.pack_into('<I',b,(i%12)*4,0x7f800001)
   results=[];csr=getcsr()
   for f,b in zip([old,new],bufs):a=c.addressof(b);results.append(f(a,a+12,a+24,a+36,a+dst))
   assert getcsr()==csr,(hex(mode),'MXCSR');assert results[0]==results[1] and bufs[0].raw==bufs[1].raw,(hex(mode),i,results,bufs[0].raw.hex(),bufs[1].raw.hex());checks+=1
  print(hex(mode),checks,flush=True)
finally:setcw(saved)
r={'comparisons':checks,'exact_boolean_and_output_bits':True,'control_modes':9,'aliases_and_nan_fallback':True,'ranges':[1,1000,1e-20,1e20],'MXCSR_restored':True};(p/'raybox-validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
