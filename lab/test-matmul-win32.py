import ctypes as c,struct,random,json
from pathlib import Path
lab=Path(__file__).parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(code):
    p=k.VirtualAlloc(None,4096,0x3000,0x40);assert p;c.memmove(p,code,len(code));return p
oldaddr=alloc((lab/'matmul-original.bin').read_bytes())
code=(lab/'matmul-sse.bin').read_bytes().replace(bytes.fromhex('55443322'),struct.pack('<I',oldaddr));newaddr=alloc(code)
def wrap(target):
    # stdcall(out,A,B) -> EAX out, ECX A, stack B.
    code=bytes.fromhex('8b4424048b4c2408ff74240ce80000000083c404c20c00')
    p=alloc(code);c.memmove(p+13,struct.pack('<i',target-(p+17)),4)
    return c.WINFUNCTYPE(c.c_uint,c.c_void_p,c.c_void_p,c.c_void_p)(p)
old,new=wrap(oldaddr),wrap(newaddr)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
saved=getcw();rng=random.Random(44);F=c.c_float*16;checks=0
try:
    for mode in [0x27f,0x67f,0xa7f,0xe7f,0xc7f]:
        setcw(mode)
        for i in range(15000):
            a=[rng.uniform(-1000,1000) for _ in range(16)];b=[rng.uniform(-1000,1000) for _ in range(16)]
            a1,a2=F(*a),F(*a);b1,b2=F(*b),F(*b);o1,o2=F(),F()
            if i%7==0:o1,o2=a1,a2
            elif i%11==0:o1,o2=b1,b2
            r1=old(o1,a1,b1);r2=new(o2,a2,b2)
            assert r1==c.addressof(b1)+48 and r2==c.addressof(b2)+48
            assert bytes(o1)==bytes(o2),(hex(mode),i,list(o1),list(o2))
            checks+=1
        print(hex(mode),'passed',checks,flush=True)
finally:setcw(saved)
(lab/'matmul-validation.json').write_text(json.dumps({'comparisons':checks,'exact_output_matches':checks,'return_pointer':'matched','aliases':'matched'}))
