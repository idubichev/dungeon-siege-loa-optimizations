import ctypes as c,struct,random,json,math,time
from pathlib import Path
lab=Path(__file__).parent;k=c.WinDLL('kernel32',use_last_error=True)
k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(code):
    addr=k.VirtualAlloc(None,max(4096,len(code)),0x3000,0x40);assert addr
    c.memmove(addr,code,len(code));return addr
oldaddr=alloc((lab/'inverse-original.bin').read_bytes())
store=c.create_string_buffer(16+136*4096)
code=bytearray((lab/'inverse-cache.bin').read_bytes())
for r in json.loads((lab/'inverse-cache-relocations.json').read_text()):
    value=c.addressof(store) if r['target']=='data' else oldaddr
    struct.pack_into('<I',code,r['offset'],value+r['addend'])
newaddr=alloc(bytes(code))
def wrap(target):
    # stdcall(input, output, transpose) -> eax input, cdecl remaining args.
    code=bytes.fromhex('8b442404ff74240cff74240ce80000000083c408c20c00')
    addr=alloc(code);c.memmove(addr+13,struct.pack('<i',target-(addr+17)),4)
    return c.WINFUNCTYPE(c.c_uint,c.c_void_p,c.c_void_p,c.c_uint)(addr)
old,new=wrap(oldaddr),wrap(newaddr)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
saved=getcw();rng=random.Random(674);F=c.c_float*16;checks=0
actual=json.loads((lab/'cpu-inverse-inputs.json').read_text())
matrices=[list(struct.unpack('<16f',bytes.fromhex(s['inverse_matrix']))) for s in actual['samples'] if 'inverse_matrix' in s]
matrices += [[rng.uniform(-4,4) for _ in range(16)] for _ in range(5000)]
matrices += [[0.]*16,[float(i%5==0) for i in range(16)]]
try:
    for mode in [0x27f,0xc7f,0x7f,0x47f,0x87f]:
        setcw(mode)
        for i,mat in enumerate(matrices):
            for tr in [0,1]:
                for repeat in range(2):
                    a,b=F(*mat),F(*mat);out1,out2=F(*([42.]*16)),F(*([42.]*16))
                    if i%13==0:out1,out2=a,b
                    r1=old(a,out1,tr);r2=new(b,out2,tr)
                    assert r1&255==r2&255,(mode,i,tr,r1,r2)
                    assert bytes(out1)==bytes(out2),(mode,i,tr,list(out1),list(out2))
                    checks+=1
        print('Passed mode',hex(mode),'cumulative calls',checks,flush=True)
    # Lock contention bypass must be correct and must not clear somebody else's lock.
    c.c_uint.from_buffer(store).value=1
    a,b=F(*matrices[0]),F(*matrices[0]);x,y=F(),F()
    r1=old(a,x,1);r2=new(b,y,1);assert (r1&255)==(r2&255) and bytes(x)==bytes(y)
    assert c.c_uint.from_buffer(store).value==1
    c.c_uint.from_buffer(store).value=0
finally:setcw(saved)
stats=struct.unpack_from('<4I',store)
report={'comparisons':checks,'exact_output_matches':checks,'lock_contention':'passed','cache_hits':stats[1],'cache_misses':stats[2]}
(lab/'inverse-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
