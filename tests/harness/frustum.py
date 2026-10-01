import ctypes as c,struct,random,json
from pathlib import Path
p=Path(__file__).parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(code):
 a=k.VirtualAlloc(None,4096,0x3000,0x40);assert a;c.memmove(a,bytes(code),len(code));return a
helpers={name:alloc((p/(name+'.bin')).read_bytes()) for name in ['vec-ctor','vec-sub','vec-dot']}
helpers['threshold']=alloc((p/'frustum-threshold.bin').read_bytes())
b=bytearray((p/'frustum-original.bin').read_bytes()+bytes.fromhex('8b4510c3'));oa=alloc(b)
for r in json.loads((p/'frustum-original-relocations.json').read_text()):
 v=helpers[r['target']]
 if 'relative_to' in r:v-=oa+r['relative_to']
 struct.pack_into('<I',b,r['offset'],v&0xffffffff)
c.memmove(oa,bytes(b),len(b))
# Save four registers; load original register inputs and use a separate frame buffer.
wrap=bytes.fromhex('555356578b5c24148b74241883c6048b6c241cb8')+struct.pack('<I',oa)+bytes.fromhex('ffd05f5e5b5dc20c00')
old=c.WINFUNCTYPE(c.c_uint,c.c_void_p,c.c_void_p,c.c_void_p)(alloc(wrap))
new=c.CFUNCTYPE(c.c_uint,c.c_void_p,c.c_void_p,c.c_float)(alloc((p/'frustum-sse.bin').read_bytes()))
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
saved=getcw();rng=random.Random(684);F=c.c_float*100;P=c.c_float*3;frame=c.create_string_buffer(1024);checks=0
try:
 for mode in [0x27f,0x67f,0xa7f,0xe7f]:
  setcw(mode)
  for i in range(15000):
   scale=[1,1000,1e-20,1e20][i%4];a=F(*[rng.uniform(-1,1)*scale for _ in range(100)]);point=P(*[rng.uniform(-1,1)*scale for _ in range(3)])
   if i%7==0:
    # Exactly on selected plane anchor; catches zero comparison behavior.
    j=[7,10,13,16,19][i%5]
    for t in range(3):point[t]=a[j+t]
   if i%11==0:
    for j in range(31,49):a[j]=0
   if i%17==0:a[37]=float('nan')
   r1=old(a,point,c.addressof(frame)+512);r2=new(a,point,0.0)
   if r1!=r2:
    (p/'frustum-failure.json').write_text(json.dumps({'mode':hex(mode),'i':i,'old':r1,'new':r2,'camera':list(a),'point':list(point)}));raise AssertionError((hex(mode),i,r1,r2))
   checks+=1
  print(hex(mode),'passed',checks,flush=True)
 for mode in [0x7f,0xc7f,0x37f,0xf7f]:
  setcw(mode);assert new(F(),P(),0)==0xffffffff
finally:setcw(saved)
report={'comparisons':checks,'exact_mask_matches':checks,'rounding_modes':4,'unsupported_precision_fallback':True,'ranges':[1,1000,1e-20,1e20],'zero_planes':True,'nan_plane':True}
(p/'frustum-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
