import ctypes as c,struct,random,json
from pathlib import Path
p=Path(__file__).resolve().parent/'13-bounds';k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_uint,c.c_uint]
def fn(code):
 # EBP points 64 bytes into bound storage, ECX to Z of input position.
 wrapper=bytes.fromhex('558b6c240883c5408b4c240c83c108894de8')+code+bytes.fromhex('5dc3')
 a=k.VirtualAlloc(None,4096,0x3000,0x40);c.memmove(a,wrapper,len(wrapper));return c.CFUNCTYPE(None,c.c_void_p,c.c_void_p)(a)
new=fn((p/'bounds.bin').read_bytes()[:-1]);olds=[fn((p/(hex(a)+'-original.bin')).read_bytes()) for a in [0x69f6ed,0x69f81a]]
rng=random.Random(6916);checks=0
for i in range(50000):
 raw=bytearray(rng.randbytes(64));v=c.create_string_buffer(rng.randbytes(12))
 if i<25000:
  for off in [20,16,0,12,4,8]:struct.pack_into('<f',raw,off,rng.uniform(-1e10,1e10))
  v=c.create_string_buffer(struct.pack('<3f',*[rng.uniform(-1e10,1e10) for _ in range(3)]))
 buffers=[c.create_string_buffer(bytes(raw)) for _ in range(3)]
 for f,b in zip([*olds,new],buffers):f(b,v)
 # Ignore temporary pointer at EBP-0x18 because all wrappers set it.
 assert buffers[0].raw==buffers[1].raw==buffers[2].raw,(i,[b.raw.hex() for b in buffers]);checks+=1
r={'cases':checks,'original_branches':2,'exact_all_buffer_bytes':True,'coverage':'finite values and arbitrary binary32 bounds/positions including NaN, infinity, reversed bounds'}
(p/'validation.json').write_text(json.dumps(r,indent=2));print(r)
