import ctypes as c,struct,random,json
from pathlib import Path
p=Path(__file__).parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(b):
 a=k.VirtualAlloc(None,4096,0x3000,0x40);assert a;c.memmove(a,b,len(b));return a
def wrap(a):
 return c.CFUNCTYPE(c.c_uint,c.c_void_p,c.c_void_p)(alloc(bytes.fromhex('8b4424048b4c2408ba')+struct.pack('<I',a)+bytes.fromhex('ffd2c3')))
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')));getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')));saved=getcw();rng=random.Random(651);checks=0
try:
 for name in ['transpose','transpose2']:
  oa=alloc((p/(name+'-original.bin')).read_bytes());body=(p/(name+'-sse.bin')).read_bytes().replace(bytes.fromhex('55443322'),struct.pack('<I',oa));old,new=wrap(oa),wrap(alloc(body))
  for cw in [0x7f,0x47f,0x87f,0xc7f,0x27f,0x67f,0xa7f,0xe7f,0x37f]:
   setcw(cw)
   for i in range(4000):
    data=bytearray(struct.pack('<48I',*[rng.getrandbits(32) for _ in range(48)]))
    if i%2==0:
     for j in range(48):struct.pack_into('<f',data,j*4,rng.uniform(-1000,1000))
    src=32;dst=[112,32,36,28,48,16,80,12][i%8];bufs=[c.create_string_buffer(bytes(data)),c.create_string_buffer(bytes(data))]
    for fn,b in zip([old,new],bufs):assert fn(c.addressof(b)+dst,c.addressof(b)+src)==c.addressof(b)+dst
    assert bufs[0].raw==bufs[1].raw,(name,hex(cw),i,src,dst);checks+=1
   print(name,hex(cw),checks,flush=True)
finally:setcw(saved)
r={'comparisons':checks,'all_output_bits_match':True,'control_modes':9,'alias_layouts':8,'arbitrary_float_bits':True};(p/'transpose-validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
