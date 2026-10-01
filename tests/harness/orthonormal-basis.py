import ctypes as c,struct,random,json
from pathlib import Path
p=Path(__file__).parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(b,size=4096):
 a=k.VirtualAlloc(None,size,0x3000,0x40);assert a;c.memmove(a,bytes(b),len(b));return a
b=bytearray((p/'ortho-original.bin').read_bytes());zero=alloc(b'\0'*4)
for offset in json.loads((p/'ortho-original-relocations.json').read_text()):struct.pack_into('<I',b,offset,zero)
oa=alloc(b);b=bytearray((p/'ortho-sse.bin').read_bytes());na=alloc(b)
for r in json.loads((p/'ortho-sse-relocations.json').read_text()):struct.pack_into('<I',b,r['offset'],na+r['code_offset'])
b=bytes(b).replace(bytes.fromhex('55443322'),struct.pack('<I',oa));c.memmove(na,b,len(b))

def wrap(a):return c.WINFUNCTYPE(c.c_uint,c.c_void_p,c.c_void_p)(alloc(bytes.fromhex('8b4c2404ff742408b8')+struct.pack('<I',a)+bytes.fromhex('ffd0c20800')))
old,new=wrap(oa),wrap(na);setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')));getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
saved=getcw();rng=random.Random(41);F=c.c_float*32;checks=0
try:
 for mode in [0x27f,0x67f,0xa7f,0xe7f,0x7f,0xc7f,0x37f,0xf7f]:
  setcw(mode)
  for i in range(6000):
   sc=[1,1e-6,1e6][i%3];v=[rng.uniform(-1,1)*sc for _ in range(32)];io=16
   if i%7==0:io=0
   elif i%11==0:io=1
   elif i%13==0:io=2
   if i%17==0:v[:6]=[0.0]*6
   for repeat in range(3):
    a,b=F(*v),F(*v);r1=old(a,c.addressof(a)+io*4);r2=new(b,c.addressof(b)+io*4)
    assert bytes(a)==bytes(b),(hex(mode),i,repeat,list(a),list(b));checks+=1
  print(hex(mode),'passed',checks,flush=True)
finally:setcw(saved)
r={'comparisons':checks,'exact_output_matches':checks,'aliases':True,'rounding_precision_modes':8,'zero_vector':True};(p/'ortho-validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
