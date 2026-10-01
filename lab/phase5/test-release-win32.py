import ctypes as c,struct,random,json,time
from pathlib import Path
p=Path(__file__).parent.parent/'phase4';k=c.WinDLL('kernel32',use_last_error=True)
k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_uint,c.c_uint]
def mapped(path):
 raw=path.read_bytes();pe=struct.unpack_from('<I',raw,60)[0];op=pe+24;sh=op+struct.unpack_from('<H',raw,pe+20)[0];n=struct.unpack_from('<H',raw,pe+6)[0]
 size=struct.unpack_from('<I',raw,op+56)[0];preferred=struct.unpack_from('<I',raw,op+28)[0];base=k.VirtualAlloc(None,size,0x3000,0x40);assert base
 for i in range(n):
  vs,va,rs,rp=struct.unpack_from('<4I',raw,sh+40*i+8)
  if rs:c.memmove(base+va,raw[rp:rp+rs],rs)
 rr,sz=struct.unpack_from('<II',raw,op+136);pos=rr
 while pos<rr+sz:
  page,length=struct.unpack('<II',c.string_at(base+pos,8))
  for entry in struct.unpack('<'+'H'*((length-8)//2),c.string_at(base+pos+8,length-8)):
   kind=entry>>12
   if kind:
    assert kind==3;v=c.c_uint.from_address(base+page+(entry&4095));v.value=(v.value+base-preferred)&0xffffffff
  pos+=length
 # The legacy EXE was linked at a fixed base and lacks relocations for its
 # original math code. Rebase those CFG-verified operands in this test mapping.
 for r in json.loads((p/'24-triangle-safe/code-absolute-refs.json').read_text()):
  v=c.c_uint.from_address(base+r['offset'])
  if v.value==r['address']:v.value=base+r['address']-preferred
 # Restore math constants initialized by the game at startup.
 for address,value in json.loads((p/'24-triangle-safe/initialized-constants.json').read_text()).items():
  data=bytes.fromhex(value);c.memmove(base+int(address,16)-preferred,data,len(data))
 return base
a=mapped(p.parent/'phase3/DS15-original.exe');b=mapped(p.parent/'phase5/08-arrow-triangle/DSLOA.exe')
fn=c.CFUNCTYPE(c.c_ubyte,*([c.c_void_p]*8));old,new=fn(a+0x328343),fn(b+0x328343)
def alloc(code):
 a=k.VirtualAlloc(None,4096,0x3000,0x40);assert a;c.memmove(a,code,len(code));return a
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')));getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')));getcsr=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec040fae1c248b042483c404c3')))
rng=random.Random(728343);saved=getcw();checks=0;start=time.perf_counter()
try:
 for mode in [0x7f,0x47f,0x87f,0xc7f,0x27f,0x67f,0xa7f,0xe7f,0x37f]:
  setcw(mode)
  for i in range(20000):
   scale=[1,1000,0.00001][i%3];data=[rng.uniform(-5,5)*scale for _ in range(15)]+[31,32,33]
   if i%9==0:data[9:12]=data[6:9]
   if i%11==0:data[3:6]=[0,1,0]
   if i%17==0:data[6:15]=[0,0,0,1,0,0,0,0,1];data[0:6]=[rng.random(),1,rng.random(),0,-1,0]
   if i>=5000:
    choices=[0.0,-0.0,1e-40,-1e-40,1e10,-1e10,1.01e10,-1.01e10,1e20,-1e20,3e38,-3e38]
    if i%3==0:data[:15]=[rng.choice(choices) for _ in range(15)]
    elif i%3==1:data[:15]=[rng.uniform(-1e10,1e10) for _ in range(15)]
   raw=struct.pack('<18f',*data)
   if i>=10000 and i%4==0:
    bits=[rng.getrandbits(32) for _ in range(15)]+[0x41f80000,0x42000000,0x42040000]
    raw=struct.pack('<18I',*bits)
   bufs=[c.create_string_buffer(raw),c.create_string_buffer(raw)]
   offsets=[0,12,24,36,48,60,64,68]
   if i%23==0:offsets[5+(i%3)]=[0,4,12,24,36,48,60][i%7]
   results=[]
   for f,buf in zip([old,new],bufs):
    addr=c.addressof(buf);csr=getcsr();results.append(f(*[addr+x for x in offsets]));assert getcw()==mode
    if f==new:assert getcsr()==csr,('MXCSR',mode,i)
   assert results[0]==results[1] and bufs[0].raw==bufs[1].raw,(hex(mode),i,results,bufs[0].raw.hex(),bufs[1].raw.hex())
   checks+=1
  print(hex(mode),checks,flush=True)
finally:setcw(saved)
r={'comparisons':checks,'actual_PE_images_executed':True,'exact_boolean_and_all_buffer_bytes':True,'modes':9,'cases':'Random rays and triangles, vertical rays, degenerate triangles, input/output aliases, extreme finite values, arbitrary binary32 including NaNs/infinities','seconds':time.perf_counter()-start}
(p.parent/'phase5/08-arrow-triangle/validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
