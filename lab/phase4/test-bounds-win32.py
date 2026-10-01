import ctypes as c,struct,random,json,time
from pathlib import Path
p=Path(__file__).parent/'03-bounds';k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(b):
 a=k.VirtualAlloc(None,4096,0x3000,0x40);assert a;c.memmove(a,b,len(b));return a
def original(b):
 a=alloc(b)
 # stdcall(frame,vertex), establish EBP, EDX=vertex and ECX=vertex+8.
 code=bytes.fromhex('555356578b6c24148b5424188d4a08b8')+struct.pack('<I',a)+bytes.fromhex('ffd05f5e5b5dc20800')
 return c.WINFUNCTYPE(None,c.c_void_p,c.c_void_p)(alloc(code))
olds=[original((p/f'original-{i}.bin').read_bytes()) for i in range(2)]
new=c.WINFUNCTYPE(None,c.c_void_p,c.c_void_p)(alloc((p/'bounds.bin').read_bytes()))
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')));getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')));getcsr=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec040fae1c248b042483c404c3')))
rng=random.Random(6944606);saved=getcw();checks=0;start=time.perf_counter()
special=[0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x7f800000,0xff800000,0x7fc00000,0x7f800001,0xff800001,0x3f800000,0xbf800000]
try:
 for mode in [0x7f,0x47f,0x87f,0xc7f,0x27f,0x67f,0xa7f,0xe7f,0x37f]:
  setcw(mode)
  for i in range(10000):
   data=bytearray(128)
   for off in [-0x30,-0x34,-0x38,-0x2c,-0x40,-0x3c]:struct.pack_into('<I',data,96+off,rng.choice(special) if i%3==0 else rng.getrandbits(32))
   vertex=c.create_string_buffer(struct.pack('<3I',*[rng.choice(special) if i%3==0 else rng.getrandbits(32) for _ in range(3)]))
   frames=[c.create_string_buffer(bytes(data)),c.create_string_buffer(bytes(data))]
   old=olds[i%2];old(c.addressof(frames[0])+96,vertex);csr=getcsr();new(c.addressof(frames[1])+96,vertex)
   assert getcw()==mode and getcsr()==csr,('control-state',hex(mode),i)
   assert frames[0].raw==frames[1].raw,(hex(mode),i,vertex.raw.hex(),frames[0].raw.hex(),frames[1].raw.hex())
   checks+=1
finally:setcw(saved)
r={'comparisons':checks,'all_frame_bytes_match':True,'both_original_blocks':True,'control_modes':9,'cases':'Random float bit patterns, NaNs, infinities, subnormals, signed zero','MXCSR_and_x87_control_preserved':True,'seconds':time.perf_counter()-start}
(p/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
