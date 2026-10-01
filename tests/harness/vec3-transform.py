import ctypes as c,struct,random,json
from pathlib import Path
lab=Path(__file__).parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(code):
 p=k.VirtualAlloc(None,4096,0x3000,0x40);assert p;c.memmove(p,code,len(code));return p
oldaddr=alloc((lab/'vec3-original.bin').read_bytes());newaddr=alloc((lab/'vec3-sse.bin').read_bytes().replace(bytes.fromhex('55443322'),struct.pack('<I',oldaddr)))
def wrap(target):
 code=bytes.fromhex('8b4c2404'+'ff742414'*4+'b844332211'+'e800000000c21400')
 p=alloc(code);c.memmove(p+26,struct.pack('<i',target-(p+30)),4)
 return c.WINFUNCTYPE(c.c_uint,c.c_void_p,c.c_void_p,c.c_void_p,c.c_int,c.c_int)(p)
old,new=wrap(oldaddr),wrap(newaddr)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
saved=getcw();rng=random.Random(405);F=c.c_float*256;checks=0
try:
 for mode in [0x7f,0x47f,0x87f,0xc7f,0x27f,0x67f,0xa7f,0xe7f,0x37f]:
  setcw(mode)
  for i in range(8000):
   v=[rng.uniform(-1000,1000) for _ in range(256)]
   a,b=F(*v),F(*v);stride=[12,16,20,0][i%4];count=[0,1,2,4,16][i%5]
   im,io,ii=0,64,128
   if i%7==0:io=ii
   elif i%11==0:io=ii+1
   elif i%13==0:io=im
   elif i%17==0:im=ii
   r1=old(c.addressof(a)+im*4,c.addressof(a)+io*4,c.addressof(a)+ii*4,count,stride)
   r2=new(c.addressof(b)+im*4,c.addressof(b)+io*4,c.addressof(b)+ii*4,count,stride)
   assert r1==r2==0x11223344,(r1,r2)
   assert bytes(a)==bytes(b),(hex(mode),i,next((j,a[j],b[j]) for j in range(256) if struct.pack('<f',a[j])!=struct.pack('<f',b[j])))
   checks+=1
  print(hex(mode),'passed',checks,flush=True)
finally:setcw(saved)
report={'comparisons':checks,'exact_output_matches':checks,'aliases':'matched','strides':[0,12,16,20],'counts':[0,1,2,4,16],'eax':'preserved'}
(lab/'vec3-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
