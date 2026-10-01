"""Compare entire indexed loops, including scratch/output buffers and FP state."""
import ctypes as c,struct,random,math,json
from pathlib import Path
p=Path(__file__).parent;lab=p.parent;out=p/'05-normal-scope'
k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(b):
 a=k.VirtualAlloc(None,4096,0x3000,0x40);assert a;c.memmove(a,bytes(b),len(b));return a
one=c.c_float(1)
qb=(lab/'quat-original.bin').read_bytes().replace(struct.pack('<I',0x72a6f0),struct.pack('<I',c.addressof(one)))
oldquat=alloc(qb)
qb=(lab/'quat-sse.bin').read_bytes();current=alloc(qb)
assert qb[-4:]==bytes.fromhex('44332211')
qb=qb[:-4]+struct.pack('<i',oldquat+7-(current+len(qb)));c.memmove(current,qb,len(qb))
original=(out/'original-loop.bin').read_bytes();oa=alloc(original+b'\xc3');b=bytearray(original)
struct.pack_into('<i',b,0x3f,current-(oa+0x43));c.memmove(oa,bytes(b),len(b))
manifest=json.loads((out/'manifest.json').read_text());na=alloc(b'');b=bytearray((out/'payload.bin').read_bytes())
exitoff=manifest['prefix_bytes']+len(original)+len(bytes.fromhex(manifest['tail']))
assert b[exitoff]==0xe9;b[exitoff:exitoff+5]=b'\xc3\x90\x90\x90\x90'
struct.pack_into('<i',b,len(b)-4,oldquat+7-(na+len(b)));c.memmove(na,bytes(b),len(b))
def wrap(a):
 b=bytes.fromhex('555356578b6c24148b5c2418b8')+struct.pack('<I',a)+bytes.fromhex('ffd05f5e5b5dc20800')
 return c.WINFUNCTYPE(None,c.c_void_p,c.c_void_p)(alloc(b))
old,new=wrap(oa),wrap(na)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
setcsr=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('0fae542404c3')))
getcsr=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec040fae1c248b042483c404c3')))
clear=c.CFUNCTYPE(None)(alloc(bytes.fromhex('dbe2c3')))
rng=random.Random(69769);savedcw=getcw();savedcsr=getcsr();checks=0
modes=[pc|rc|0x7f for pc in (0,0x200,0x300) for rc in (0,0x400,0x800,0xc00)]
interesting=[0,0x80000000,1,0x80000001,0x7f800000,0xff800000,0x7fc12345,0x7f812345,0x7f7fffff,0x80800000]
def values(n,adversarial):
 if adversarial:return b''.join(struct.pack('<I',rng.choice(interesting) if rng.random()<.3 else rng.getrandbits(32)) for _ in range(n))
 return struct.pack('<'+'f'*n,*[rng.uniform(-2,2) for _ in range(n)])
try:
 for mode in modes:
  for i in range(1200):
   count=1+i%64;indices=[rng.randrange(64) for _ in range(count)];indexbuf=c.create_string_buffer(struct.pack('<'+'I'*count,*indices))
   # Duplicate indices and arbitrary normal/quaternion values exercise dependencies.
   source=c.create_string_buffer(values(64*14,i%4==0));quat=c.create_string_buffer(values(4,i%4==0));position=c.create_string_buffer(values(3,i%4==0))
   pointertable=c.create_string_buffer(16);struct.pack_into('<I',pointertable,8,c.addressof(source))
   root=c.create_string_buffer(128);struct.pack_into('<I',root,0x34,c.addressof(pointertable))
   obj=c.c_uint(c.addressof(root));dest_initial=bytes(rng.getrandbits(8) for _ in range(64*24));normal_initial=values(64*3,i%4==0)
   outputs=[];frames=[]
   csr=(savedcsr|0x1f80)&~0x603f;csr|=rng.randrange(4)<<13;csr|=rng.randrange(64);csr^=rng.choice([0,0x40,0x8000,0x8040])
   for fn in (old,new):
    dest=c.create_string_buffer(dest_initial);normal=c.create_string_buffer(normal_initial);frame=c.create_string_buffer(1024);base=c.addressof(frame)+512
    for offset,value in [(-8,c.addressof(indexbuf)),(-40,count),(-28,c.addressof(dest)),(-24,c.addressof(position)+8),(-20,8),(-156,c.addressof(normal)),(-16,c.addressof(quat))]:struct.pack_into('<I',frame,512+offset,value)
    setcw(mode);clear();setcsr(csr);fn(base,c.addressof(obj))
    assert getcw()==mode and getcsr()==csr,(hex(mode),i,'FP state')
    outputs.append((bytes(dest),bytes(normal),struct.unpack_from('<I',frame,504)[0]-c.addressof(indexbuf),struct.unpack_from('<I',frame,472)[0]))
   assert outputs[0]==outputs[1],(hex(mode),i,'output mismatch')
   assert outputs[1][2:]==(4*count,0)
   checks+=1
  print(hex(mode),'passed',checks,flush=True)
finally:
 clear();setcw(savedcw);setcsr(savedcsr)
r={'complete_loop_comparisons':checks,'vertices_per_loop':[1,64],'control_modes':len(modes),'arbitrary_bits_cases':checks//4,'all_output_bits_match':True,'duplicate_indices':True,'MXCSR_and_x87_control_preserved':True,'reference':'Installed unscoped quaternion SSE leaf with its original x87 fallback; identical full indexed loop'}
(out/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
