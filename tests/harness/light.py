import ctypes as c,struct,random,json
from pathlib import Path
lab=Path(__file__).parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(code):
    p=k.VirtualAlloc(None,4096,0x3000,0x40);assert p;c.memmove(p,code,len(code));return p
constants=[];code=bytearray((lab/'light-original.bin').read_bytes())
for r in json.loads((lab/'light-original-relocations.json').read_text()):
    v=c.create_string_buffer(bytes.fromhex(r['bytes']));constants.append(v);struct.pack_into('<I',code,r['offset'],c.addressof(v))
oldaddr=alloc(bytes(code));code=(lab/'light-sse.bin').read_bytes().replace(bytes.fromhex('55443322'),struct.pack('<I',oldaddr));newaddr=alloc(code)
def wrap(target):
    code=bytes.fromhex('55578b6c240c8b7c241083c704e8000000005f5dc20800')
    p=alloc(code);c.memmove(p+14,struct.pack('<i',target-(p+18)),4)
    return c.WINFUNCTYPE(c.c_ulonglong,c.c_void_p,c.c_void_p)(p)
old,new=wrap(oldaddr),wrap(newaddr)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
saved=getcw();rng=random.Random(833);N=c.c_float*3;checks=0
try:
    for mode in [0x7f,0x47f,0x87f,0xc7f,0x27f,0x67f,0xa7f,0xe7f,0x37f]:
        setcw(mode)
        for i in range(16000):
            fields=[rng.uniform(-2,2) for _ in range(3)]+[rng.uniform(-2,2)]
            n=N(*[rng.uniform(-1,1) for _ in range(3)])
            if i%29==0:n=N(0,0,0)
            frame=bytearray(b'\xcd'*256)
            for off,v in zip([-36,-32,-28,-12],fields):struct.pack_into('<f',frame,128+off,v)
            a=c.create_string_buffer(bytes(frame));b=c.create_string_buffer(bytes(frame))
            r1=old(c.addressof(a)+128,n);r2=new(c.addressof(b)+128,n)
            assert r1==r2 and a.raw==b.raw,(hex(mode),i,fields,list(n),hex(r1),hex(r2))
            checks+=1
        print(hex(mode),'passed',checks,flush=True)
finally:setcw(saved)
(lab/'light-validation.json').write_text(json.dumps({'comparisons':checks,'exact_output_matches':checks,'frame_memory':'byte-identical','rounding_modes':9}))
