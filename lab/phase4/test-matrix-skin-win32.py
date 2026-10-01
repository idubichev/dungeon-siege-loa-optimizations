import ctypes as c,struct,random,math,json
from pathlib import Path
p=Path(__file__).parent/'08-matrix-skin';lab=p.parent.parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(code):
 a=k.VirtualAlloc(None,4096,0x3000,0x40);assert a;c.memmove(a,bytes(code),len(code));return a
constants=c.create_string_buffer((lab/'math-constants.bin').read_bytes())
def relocate(name):
 b=bytearray((lab/(name+'.bin')).read_bytes());a=alloc(b)
 for r in json.loads((lab/(name+'-relocations.json')).read_text()):
  v=c.addressof(constants)+r['addend'] if r['target']=='constant' else (acosaddr-(a+r['relative_to']))&0xffffffff
  struct.pack_into('<I',b,r['offset'],v)
 c.memmove(a,bytes(b),len(b));return a
acosaddr=relocate('acos-original');slerp=relocate('slerp-original');one=c.c_float(1)
qb=(lab/'quat-original.bin').read_bytes().replace(struct.pack('<I',0x72a6f0),struct.pack('<I',c.addressof(one)));oldquat=alloc(qb)
original=(p/'original.bin').read_bytes();oa=alloc(original);b=bytearray(original)
vec=alloc((lab/'vec3-original.bin').read_bytes())
for r in json.loads((p/'original-relocations.json').read_text()):struct.pack_into('<i',b,r['offset'],(vec if r['target']=='0x43e774' else slerp)-(oa+r['next']))
c.memmove(oa,bytes(b),len(b))
body=bytearray((p/'skin-loop.bin').read_bytes());addr=alloc(body)
for r in json.loads((p/'skin-loop-relocations.json').read_text()):
 value=(addr if r['target']=='code' else slerp)+r['value'];assert r['kind']=='absolute';struct.pack_into('<I',body,r['offset'],value)
c.memmove(addr,bytes(body),len(body))
def wrap(a):
 b=bytes.fromhex('555356578b6c24148b5c24188b7c241cb8')+struct.pack('<I',a)+bytes.fromhex('ffd05f5e5b5dc20c00');return c.WINFUNCTYPE(None,c.c_void_p,c.c_void_p,c.c_void_p)(alloc(b))
old=wrap(oa);new=c.CFUNCTYPE(c.c_uint,c.c_void_p,c.c_void_p,c.c_void_p)(addr)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')));getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')));getcsr=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec040fae1c248b042483c404c3')))
rng=random.Random(69320);F=c.c_float*48;N=c.c_float*64;checks=0;saved=getcw()
def norm():
 a=[rng.uniform(-1,1) for _ in range(4)];n=math.sqrt(sum(v*v for v in a));return [v/n for v in a]
try:
 for mode in [0x7f,0x47f,0x87f,0xc7f,0x27f,0x67f,0xa7f,0xe7f,0x37f]:
  setcw(mode)
  for i in range(1000):
   verts=F(*[rng.uniform(-100,100) for _ in range(48)]);v=[rng.uniform(-20,20) for _ in range(48)];outs=[F(*v),F(*v)];n=sum([norm() for _ in range(16)],[]);normals=[N(*n),N(*n)];frames=[c.create_string_buffer(1024),c.create_string_buffer(1024)];obj=c.create_string_buffer(256);struct.pack_into('<I',obj,240,i%2)
   count=1+i%16;weights=c.create_string_buffer(count*8)
   for j in range(count):struct.pack_into('<If',weights,8*j,rng.randrange(16),rng.random())
   q=norm();matrix=[rng.uniform(-1,1) for _ in range(9)];tr=[rng.uniform(-100,100) for _ in range(3)]
   for j in range(2):
    f=frames[j];struct.pack_into('<9f',f,512-244,*matrix);struct.pack_into('<4f',f,512-172,*q);struct.pack_into('<3f',f,512-104,*tr)
    for offset,value in [(-16,c.addressof(verts)),(-36,c.addressof(outs[j])),(-68,c.addressof(normals[j])),(-8,c.addressof(weights)+count*8)]:struct.pack_into('<I',f,512+offset,value)
   old(c.addressof(frames[0])+512,obj,weights);csr=getcsr();before=[bytes(outs[1]),bytes(normals[1]),frames[1].raw];ok=new(c.addressof(frames[1])+512,obj,weights)
   assert ok==int((mode&0x300)==0x200),(hex(mode),'status',ok)
   if not ok:
    assert before==[bytes(outs[1]),bytes(normals[1]),frames[1].raw], 'fallback mutation'
    old(c.addressof(frames[1])+512,obj,weights)
   assert getcsr()==csr,(hex(mode),'MXCSR')
   assert bytes(outs[0])==bytes(outs[1]) and bytes(normals[0])==bytes(normals[1]),(hex(mode),i)
   for start,size in [(-84,4),(-116,12),(-28,4)]:assert frames[0].raw[512+start:512+start+size]==frames[1].raw[512+start:512+start+size],(hex(mode),i,start)
   checks+=1
  print(hex(mode),'passed',checks,flush=True)
finally:setcw(saved)
r={'complete_loop_comparisons':checks,'vertices_per_loop':[1,16],'normal_interpolation':True,'all_output_bits_match':True,'MXCSR_restored':True,'control_modes':9};(p/'validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
