import ctypes as c, struct, random, math, json, time
from pathlib import Path
lab=Path(__file__).parent
k=c.WinDLL('kernel32',use_last_error=True)
k.VirtualAlloc.restype=c.c_void_p
k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(code):
    addr=k.VirtualAlloc(None,4096,0x3000,0x40);assert addr
    c.memmove(addr,code,len(code));return addr
one=c.c_float(1)
old=(lab/'quat-original.bin').read_bytes()
assert old.count(struct.pack('<I',0x72a6f0))==1
old=old.replace(struct.pack('<I',0x72a6f0),struct.pack('<I',c.addressof(one)))
oldaddr=alloc(old)
new=(lab/'quat-sse.bin').read_bytes();newaddr=alloc(new)
assert new[-4:]==bytes.fromhex('44332211')
c.memmove(newaddr+len(new)-4,struct.pack('<i',oldaddr+7-(newaddr+len(new))),4)
def wrapper(target):
    # stdcall(q, out, v) -> thiscall(q, out, v).
    code=bytes.fromhex('8b4c2404ff74240cff74240ce800000000c20c00')
    addr=alloc(code)
    c.memmove(addr+13,struct.pack('<i',target-(addr+17)),4)
    return c.WINFUNCTYPE(None,c.c_void_p,c.c_void_p,c.c_void_p)(addr)
original=wrapper(oldaddr);replacement=wrapper(newaddr)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
saved=getcw();rng=random.Random(3701);report=[]
F4=c.c_float*4;F3=c.c_float*3
try:
    for mode in [0x7f,0x47f,0x87f,0xc7f,0x27f,0x67f,0xa7f,0xe7f,0x37f]:
        setcw(mode);assert getcw()==mode
        mismatch=0;worst=0;first=None;n=0
        start=time.perf_counter()
        for i in range(12000):
            q=[rng.uniform(-1,1) for _ in range(4)];norm=math.sqrt(sum(x*x for x in q));q=[x/norm for x in q]
            v=[rng.uniform(-1000,1000) for _ in range(3)]
            if i<10:q=[0,0,0,1];v=[0.,float(i),-float(i)]
            a,b=F4(*q),F4(*q);v1,v2=F3(*v),F3(*v);o1,o2=F3(),F3()
            # Preserve the original's behavior even when outputs alias an input.
            if i%11==0:o1,o2=v1,v2
            elif i%17==0:o1,o2=a,b
            original(a,o1,v1);replacement(b,o2,v2);n+=1
            if c.string_at(c.addressof(o1),12)!=c.string_at(c.addressof(o2),12):
                mismatch+=1
                error=max(abs(o1[j]-o2[j]) for j in range(3));worst=max(worst,error)
                if first is None:first={'q':q,'v':v,'original':list(o1)[:3],'sse':list(o2)[:3]}
        report.append({'control':hex(mode),'cases':n,'byte_mismatches':mismatch,'worst_abs_difference':worst,'first':first,'seconds':time.perf_counter()-start})
        print(json.dumps(report[-1]),flush=True)
finally:setcw(saved)
(lab/'quat-validation.json').write_text(json.dumps(report,indent=2))
assert all(r['byte_mismatches']==0 for r in report), 'Results differ; do not install without investigating'
