import ctypes as c,struct,random,json
from pathlib import Path
p=Path(__file__).parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(b):
 a=k.VirtualAlloc(None,4096,0x3000,0x40);assert a;c.memmove(a,b,len(b));return a
color=alloc((p/'color-add-original.bin').read_bytes());ob=bytearray((p/'light-loop-original.bin').read_bytes()+b'\xc3');oa=alloc(bytes(ob));constants=[]
for r in json.loads((p/'light-loop-original-relocations.json').read_text()):
 if r['target']=='constant':
  v=c.create_string_buffer(bytes.fromhex(r['bytes']));constants.append(v);struct.pack_into('<I',ob,r['offset'],c.addressof(v))
 else:struct.pack_into('<i',ob,r['offset'],color-(oa+r['next']))
c.memmove(oa,bytes(ob),len(ob))
body=bytearray((p/'light-loop.bin').read_bytes());addr=alloc(bytes(body))
for r in json.loads((p/'light-loop-relocations.json').read_text()):struct.pack_into('<I',body,r['offset'],(addr if r['target']=='code' else color)+r['value'])
c.memmove(addr,bytes(body),len(body))
old=c.CFUNCTYPE(None,c.c_void_p,c.c_void_p,c.c_uint)(alloc(bytes.fromhex('5556578b6c24108b7c24148b742418b8')+struct.pack('<I',oa)+bytes.fromhex('ffd05f5e5dc3')));new=c.CFUNCTYPE(c.c_uint,c.c_void_p,c.c_void_p,c.c_uint)(addr)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')));getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')));getcsr=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec040fae1c248b042483c404c3')));saved=getcw();rng=random.Random(6911);checks=0
try:
 for mode in [0x7f,0x47f,0x87f,0xc7f,0x27f,0x67f,0xa7f,0xe7f,0x37f]:
  setcw(mode)
  for i in range(1000):
   count=1+i%64;norm=(c.c_float*(count*3))(*[rng.uniform(-2,2) for _ in range(count*3)]);colors=bytes(rng.getrandbits(8) for _ in range(count*24));out=[c.create_string_buffer(colors),c.create_string_buffer(colors)];frames=[c.create_string_buffer(1024),c.create_string_buffer(1024)];light=c.create_string_buffer(bytes(rng.getrandbits(8) for _ in range(8)));direction=[rng.uniform(-2,2) for _ in range(3)];scale=rng.uniform(0,2)
   for j in range(2):
    struct.pack_into('<3f',frames[j],512-36,*direction);struct.pack_into('<f',frames[j],512-12,scale);struct.pack_into('<I',frames[j],512-4,c.addressof(out[j]));struct.pack_into('<I',frames[j],512+8,c.addressof(light))
   old(c.addressof(frames[0])+512,c.addressof(norm)+4,count);csr=getcsr();before=[out[1].raw,frames[1].raw];ok=new(c.addressof(frames[1])+512,c.addressof(norm)+4,count);assert ok==int((mode&0x300)==0x200),(hex(mode),'status',ok)
   if not ok:
    assert before==[out[1].raw,frames[1].raw],'fallback mutation';old(c.addressof(frames[1])+512,c.addressof(norm)+4,count)
   assert getcsr()==csr,(hex(mode),'MXCSR');assert out[0].raw==out[1].raw,(hex(mode),i,'colors')
   for start,size in [(-40,4),(-64,4)]:assert frames[0].raw[512+start:512+start+size]==frames[1].raw[512+start:512+start+size],(hex(mode),i,start)
   for j in range(2):assert struct.unpack_from('<I',frames[j],512-4)[0]==c.addressof(out[j])+count*24
   checks+=1
  print(hex(mode),checks,flush=True)
finally:setcw(saved)
r={'complete_loop_comparisons':checks,'vertices_per_loop':[1,64],'all_color_bits_match':True,'MXCSR_restored':True,'control_modes':9};(p/'light-loop-validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
