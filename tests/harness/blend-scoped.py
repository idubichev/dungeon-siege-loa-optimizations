import ctypes as c, struct, random, json
from pathlib import Path
lab=Path(__file__).parent
k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p
k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(code):
    p=k.VirtualAlloc(None,4096,0x3000,0x40);assert p
    c.memmove(p,code,len(code));return p
oldaddr=alloc((lab.parent/'blend-original.bin').read_bytes())
newaddr=alloc((lab/'blend-scoped.bin').read_bytes().replace(bytes.fromhex('55443322'),struct.pack('<I',oldaddr)))
def wrap(target):
    code=bytes.fromhex('55568b6c240c8b742410e8000000005e5dc20800')
    p=alloc(code);c.memmove(p+11,struct.pack('<i',target-(p+15)),4)
    return c.WINFUNCTYPE(c.c_uint,c.c_void_p,c.c_uint)(p)
old,new=wrap(oldaddr),wrap(newaddr)
getcsr=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec040fae1c248b042483c404c3')))
setcsr=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('0fae542404c3')))
raw_call=new
def new(*args):
    previous=getcsr();setcsr((previous&0xffff1fbf)|((getcw()<<3)&0x6000))
    try:return raw_call(*args)
    finally:setcsr(previous)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
rng=random.Random(4481);saved=getcw();checks=0
try:
    for mode in [0x7f,0x47f,0x87f,0xc7f,0x27f,0x67f,0xa7f,0xe7f,0x37f]:
        setcw(mode)
        for i in range(12000):
            frame=bytearray(256)
            for off in [-104,-100,-96,-88,-80,-76,-72,64,68,72]:
                struct.pack_into('<f',frame,128+off,rng.uniform(-100,100))
            a=c.create_string_buffer(bytes(frame));b=c.create_string_buffer(bytes(frame))
            # Include outputs overlapping temporary input fields.
            dest=[192,48,52,56,40,24][i%6];index=(i%5)*12
            struct.pack_into('<I',a,92,c.addressof(a)+dest-index)
            struct.pack_into('<I',b,92,c.addressof(b)+dest-index)
            r1=old(c.addressof(a)+128,index);r2=new(c.addressof(b)+128,index)
            x,y=bytearray(a.raw),bytearray(b.raw);x[92:96]=y[92:96]=b'\0'*4
            assert x==y and r1-c.addressof(a)==r2-c.addressof(b),(hex(mode),i)
            checks+=1
        print(hex(mode),'passed',checks,flush=True)
finally:setcw(saved)
(lab/'blend-scoped-validation.json').write_text(json.dumps({'comparisons':checks,'exact_matches':checks,'modes':9,'includes_aliases':True}))
