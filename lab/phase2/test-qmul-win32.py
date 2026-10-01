import ctypes as c,struct,random,json
from pathlib import Path
p=Path(__file__).parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(b):
 a=k.VirtualAlloc(None,4096,0x3000,0x40);assert a;c.memmove(a,b,len(b));return a
oa=alloc((p/'qmul-original.bin').read_bytes());b=(p/'qmul-sse.bin').read_bytes();assert b.count(bytes.fromhex('55443322'))==1;na=alloc(b.replace(bytes.fromhex('55443322'),struct.pack('<I',oa)))
def wrap(a):
 b=bytes.fromhex('8b4c2404ff74240cff74240cb8')+struct.pack('<I',a)+bytes.fromhex('ffd0c20c00')
 return c.WINFUNCTYPE(c.c_uint,c.c_void_p,c.c_void_p,c.c_void_p)(alloc(b))
old,new=wrap(oa),wrap(na)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')));getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
saved=getcw();rng=random.Random(5361);F=c.c_float*32;checks=0
try:
 for mode in [0x27f,0x67f,0xa7f,0xe7f,0x7f,0xc7f,0x37f,0xf7f]:
  setcw(mode)
  for i in range(10000):
   sc=[1,1e-12,1e12][i%3];v=[rng.uniform(-1,1)*sc for _ in range(32)];a,b=F(*v),F(*v)
   ia,ib,io=0,8,16
   if i%5==0:io=ia
   elif i%7==0:io=ib
   elif i%11==0:io=ia+1
   elif i%13==0:ib=ia
   r1=old(c.addressof(a)+ia*4,c.addressof(a)+io*4,c.addressof(a)+ib*4);r2=new(c.addressof(b)+ia*4,c.addressof(b)+io*4,c.addressof(b)+ib*4)
   assert r1==c.addressof(a)+io*4 and r2==c.addressof(b)+io*4
   assert bytes(a)==bytes(b),(hex(mode),i,list(a),list(b));checks+=1
  print(hex(mode),'passed',checks,flush=True)
finally:setcw(saved)
r={'comparisons':checks,'exact_output_matches':checks,'aliases':True,'PC53_rounding_modes':4,'fallback_modes':4};(p/'qmul-validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
