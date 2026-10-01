import ctypes as c,struct,random,json,math
from pathlib import Path
lab=Path(__file__).parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(code):
    p=k.VirtualAlloc(None,4096,0x3000,0x40);assert p;c.memmove(p,code,len(code));return p
constants=c.create_string_buffer((lab/'math-constants.bin').read_bytes())
def relocate(name):
    code=bytearray((lab/(name+'.bin')).read_bytes());addr=alloc(bytes(code))
    for r in json.loads((lab/(name+'-relocations.json')).read_text()):
        if r['target']=='constant':v=c.addressof(constants)+r['addend']
        else:v=(acosaddr-(addr+r['relative_to']))&0xffffffff
        struct.pack_into('<I',code,r['offset'],v)
    c.memmove(addr,bytes(code),len(code));return addr
acosaddr=relocate('acos-original');oldaddr=relocate('slerp2-original')
store=c.create_string_buffer(16+60*8192);code=bytearray((lab/'slerp2-cache.bin').read_bytes())
for r in json.loads((lab/'slerp2-cache-relocations.json').read_text()):
    v=c.addressof(store) if r['target']=='data' else oldaddr
    struct.pack_into('<I',code,r['offset'],v+r['addend'])
newaddr=alloc(bytes(code));Fn=c.CFUNCTYPE(None,c.c_void_p,c.c_void_p,c.c_void_p,c.c_float);old,new=Fn(oldaddr),Fn(newaddr)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
saved=getcw();rng=random.Random(233);F=c.c_float*4;checks=0
try:
    for mode in [0x7f,0x47f,0x87f,0xc7f,0x27f,0x67f,0xa7f,0xe7f,0x37f]:
        setcw(mode)
        for i in range(5000):
            a=[rng.uniform(-1,1) for _ in range(4)];b=[rng.uniform(-1,1) for _ in range(4)]
            na=math.sqrt(sum(x*x for x in a));nb=math.sqrt(sum(x*x for x in b));a=[x/na for x in a];b=[x/nb for x in b]
            t=rng.random()
            if i%17==0:b=a[:]
            elif i%19==0:b=[-x for x in a]
            if i%23==0:t=0
            elif i%29==0:t=1
            for repeat in range(2):
                a1,a2=F(*a),F(*a);b1,b2=F(*b),F(*b)
                if i%31==0:b1,b2=a1,a2
                o1,o2=F(1,2,3,4),F(1,2,3,4)
                if i%37==0:o1,o2=a1,a2
                elif i%41==0:o1,o2=b1,b2
                old(o1,a1,b1,t);new(o2,a2,b2,t)
                assert bytes(o1)==bytes(o2),(mode,i,list(o1),list(o2))
                assert bytes(a1)==bytes(a2) and bytes(b1)==bytes(b2)
                checks+=1
        print(hex(mode),'passed',checks,flush=True)
    c.c_uint.from_buffer(store).value=1
    a1,a2=F(*a),F(*a);b1,b2=F(*b),F(*b);o1,o2=F(),F();old(o1,a1,b1,t);new(o2,a2,b2,t)
    assert bytes(o1)==bytes(o2) and c.c_uint.from_buffer(store).value==1
finally:setcw(saved)
stats=struct.unpack_from('<4I',store)
report={'comparisons':checks,'exact_output_matches':checks,'hits':stats[1],'misses':stats[2],'lock_contention':'passed'}
(lab/'slerp2-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
