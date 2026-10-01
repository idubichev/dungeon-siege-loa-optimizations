"""Compare full x87 extended results and exception flags against original code."""
from pathlib import Path
import ctypes as c, random, struct, json
p=Path(__file__).resolve().parent/'05-length'
k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p
k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_uint,c.c_uint]
def fn(body):
    # Save control word; three live stack values exercise stack preservation.
    prefix=bytes.fromhex('558bec83ec04d97dfcdb e2d96d08d9e8d9e8d9e88b4d0c'.replace(' ',''))
    suffix=bytes.fromhex('8b4510db38dd780addd8ddd8ddd8dbe2d96dfc89ec5dc3')
    code=prefix+body[:-1]+suffix
    address=k.VirtualAlloc(None,4096,0x3000,0x40);c.memmove(address,code,len(code))
    return c.CFUNCTYPE(None,c.c_uint,c.c_void_p,c.c_void_p)(address)
old=fn((p/'original.bin').read_bytes());new=fn((p/'length.bin').read_bytes())
rng=random.Random(438);checks=0
for mode in [0x7f,0x27f,0x37f,0x47f,0x87f,0xc7f,0xe7f,0xa7f,0xf7f]:
    for i in range(20000):
        raw=rng.randbytes(12) if i%2 else struct.pack('<3f',*[rng.uniform(-1e12,1e12) for _ in range(3)])
        v=c.create_string_buffer(raw);a=c.create_string_buffer(12);b=c.create_string_buffer(12)
        old(mode,v,a);new(mode,v,b)
        assert a.raw[:10]==b.raw[:10],(mode,i,raw.hex(),a.raw.hex(),b.raw.hex())
        assert (struct.unpack_from('<H',a.raw,10)[0]&63)==(struct.unpack_from('<H',b.raw,10)[0]&63)
        checks+=1
    print(hex(mode),checks,flush=True)
result={'comparisons':checks,'x87_modes':9,'exact_extended_80bit_results':True,
        'exact_exception_flags':True,'coverage':'Finite and arbitrary binary32 vectors, including NaN/infinity; three pre-existing x87 stack values.'}
(p/'validation.json').write_text(json.dumps(result,indent=2));print(result)
