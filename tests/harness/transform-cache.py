import ctypes as c,struct,json,random
from pathlib import Path
p=Path(__file__).resolve().parent
source=(p/'test-transform-kernel-win32.py').read_text()
exec(source[:source.index('old,new=')])
build=p/'13-transform-cache';manifest=json.loads((build/'manifest.json').read_text());base=mapped(build/'DSLOA.exe')
c.memmove(base+0x41efc7-0x400000,b'\xc3',1)
apply=c.WINFUNCTYPE(c.c_int,c.c_void_p,c.c_void_p,c.c_void_p)(base+manifest['symbols']['_apply_cached@12']-0x400000)
compose=c.WINFUNCTYPE(c.c_int,c.c_void_p,c.c_void_p,c.c_void_p)(base+manifest['symbols']['_compose@12']-0x400000)
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
saved=getcw();setcw(0x27f)
cache=c.create_string_buffer(manifest['state_bytes']);renderer=c.create_string_buffer(0x604);inner=c.create_string_buffer(0x400);device=(c.c_uint*2)();vt=(c.c_uint*15)();before=c.create_string_buffer(64);actual=c.create_string_buffer(64);expected=c.create_string_buffer(64);obj=c.create_string_buffer(160)
counts={'get':0,'set':0};get_failure=False
@c.WINFUNCTYPE(c.c_int,c.c_void_p,c.c_uint,c.c_void_p)
def get(d,state,out):
 counts['get']+=1
 if get_failure:return -1
 c.memmove(out,before,64);return 0
@c.WINFUNCTYPE(c.c_int,c.c_void_p,c.c_uint,c.c_void_p)
def put(d,state,mat):
 counts['set']+=1;c.memmove(actual,mat,64);return 0
vt[12]=c.cast(get,c.c_void_p).value;vt[11]=c.cast(put,c.c_void_p).value;device[0]=c.addressof(vt);device[1]=c.addressof(inner);c.c_uint.from_address(c.addressof(renderer)+0x600).value=c.addressof(device)
rng=random.Random(120);checks=0
try:
 for case in range(2000):
  for array,n in [(before,16),(obj,40)]:c.memmove(array,struct.pack('<'+'f'*n,*[rng.uniform(-100,100)for _ in range(n)]),n*4)
  assert compose(expected,before,obj)==1
  for repeat in range(3):
   assert apply(renderer,obj,cache)==1 and actual.raw==expected.raw;checks+=1
  # Every matrix/rotation/position/scale word is part of the exact key.
  array,index=(before,case%16) if case%2 else (obj,([*range(4,16),38])[case%13])
  c.c_uint.from_address(c.addressof(array)+4*index).value^=1
  assert compose(expected,before,obj)==1
  assert apply(renderer,obj,cache)==1 and actual.raw==expected.raw;checks+=1
 # State-block recording, failed GetTransform, unsupported x87 mode, nonfinite input.
 sets=counts['set'];inner[0x3d0]=b'\x01';assert apply(renderer,obj,cache)==0;inner[0x3d0]=b'\x00'
 get_failure=True;assert apply(renderer,obj,cache)==0;get_failure=False
 setcw(0x7f);assert apply(renderer,obj,cache)==0;setcw(0x27f)
 c.c_uint.from_address(c.addressof(obj)+4*38).value=0x7f800000;assert apply(renderer,obj,cache)==0
 assert counts['set']==sets
 owner,hits,misses,fallbacks=struct.unpack_from('<4I',cache.raw)
 assert hits==4000 and misses==4000 and fallbacks==4,(hits,misses,fallbacks)
 c.c_uint.from_buffer(cache).value=0xffffffff;assert apply(renderer,obj,cache)==0
 # Pointer reuse and hash collisions are distinguished by complete input keys.
 c.c_uint.from_buffer(cache).value=owner
 area=c.create_string_buffer(32768+160);a=c.addressof(area);b=a+16384
 for address in [a,b,a,b]:
  c.memmove(address,struct.pack('<40f',*[rng.uniform(-20,20)for _ in range(40)]),160)
  assert compose(expected,before,address)==1
  assert apply(renderer,address,cache)==1 and actual.raw==expected.raw;checks+=1
 result={'exact_comparisons':checks,'cache_hits':hits,'cache_misses':misses,'guards_checked':['state-block recording','GetTransform failure','24-bit nearest x87','nonfinite input','thread owner mismatch'],'all_input_words_checked':True,'address_reuse_and_collisions_checked':True,'fixed_cache_bytes':manifest['state_bytes']}
 (build/'cache-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
finally:setcw(saved)
