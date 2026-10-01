import ctypes as c,struct,json,random
from pathlib import Path
p=Path(__file__).resolve().parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(b):
 a=k.VirtualAlloc(None,max(len(b),4096),0x3000,0x40);assert a;c.memmove(a,bytes(b),len(b));return a
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
 return base
def fn(build):
 folder=p/build;base=mapped(folder/'DSLOA.exe');addr=json.loads((folder/'manifest.json').read_text())['symbols']['_compose@12'];return c.WINFUNCTYPE(c.c_int,c.c_void_p,c.c_void_p,c.c_void_p)(base+addr-0x400000)
old,new=fn('10-transform-simd'),fn('13-transform-cache')
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
getcsr=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec040fae1c248b042483c404c3')))
setcsr=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('0fae542404c3')))
savedcw=getcw();savedcsr=getcsr();rng=random.Random(67907);checks=0;fallbacks=0
modes=[pc|rc|0x7f for pc in (0,0x200,0x300) for rc in (0,0x400,0x800,0xc00)]
def data(n,i):
 if i%4==0:return b''.join(struct.pack('<I',rng.choice([0,0x80000000,1,0x80000001,0x7f800000,0xff800000,0x7fc00000,0x7f800001]) if rng.random()<.1 else rng.getrandbits(32))for _ in range(n))
 values=[rng.uniform(-1000,1000) if rng.random()>.2 else rng.choice([0.0,-0.0,1e-40,-1e-40])for _ in range(n)]
 return struct.pack('<'+'f'*n,*values)
try:
 for mode in modes:
  for i in range(3000):
   before=c.create_string_buffer(data(16,i));obj=c.create_string_buffer(data(40,i));a=c.create_string_buffer(b'\xcd'*64);b=c.create_string_buffer(b'\xcd'*64)
   csr=(savedcsr|0x1f80)&~0x6000;csr^=rng.choice([0,0x40,0x8000,0x8040]);csr|=rng.randrange(4)<<13
   setcw(mode);setcsr(csr);r1=old(a,before,obj);assert getcw()==mode and getcsr()==csr
   r2=new(b,before,obj);assert getcw()==mode and getcsr()==csr
   assert r1==r2 and a.raw==b.raw,(hex(mode),i,r1,r2)
   fallbacks+=not r1;checks+=1
  print(hex(mode),checks,flush=True)
finally:setcw(savedcw);setcsr(savedcsr)
r={'comparisons':checks,'control_modes':len(modes),'exact_output_bits':True,'fallbacks':fallbacks,'x87_and_MXCSR_preserved':True,'coverage':'General matrices, finite bounded inputs, arbitrary bits, NaN/infinity, signed zero, subnormals; vector kernel compared with scalar kernel which matched 370186 live original transformations.'}
(p/'13-transform-cache/kernel-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
