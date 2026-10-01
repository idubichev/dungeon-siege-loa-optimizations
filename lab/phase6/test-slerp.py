from pathlib import Path
root=Path(__file__).resolve().parent
source=(root.parent/'test-slerp-win32.py').read_text()
exec(source[:source.index('store=c.create_string_buffer')].replace('lab=Path(__file__).parent','lab=root.parent'))
source=(root.parent/'phase4/test-triangle-safe-win32.py').read_text()
func=source[source.index('def mapped('):source.index("a=mapped(")]
func=func[:func.index(' # The legacy EXE')]+ ' return base\n'
exec(func)
base=mapped(root/'08-slerp/DSLOA.exe')
fallback=base+0x6ae000
c.memmove(fallback,b'\xe9'+struct.pack('<i',oldaddr-(fallback+5)),5)
Fn=c.CFUNCTYPE(None,c.c_void_p,c.c_void_p,c.c_float);old,new=Fn(oldaddr),Fn(base+0x7e2000)
setcw=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('508b442408890424d92c2458c3')))
getcw=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec04d93c240fb7042483c404c3')))
saved=getcw();rng=random.Random(233);F=c.c_float*4;checks=0;worst=0;fallback_checks=0
try:
 for mode in [0xe7f,0x7f,0xc7f,0x27f,0x47f,0x87f,0x37f]:
  setcw(mode)
  for i in range(20000):
   a=[rng.uniform(-1,1) for _ in range(4)];b=[rng.uniform(-1,1) for _ in range(4)]
   na=math.sqrt(sum(x*x for x in a));nb=math.sqrt(sum(x*x for x in b));a=[x/na for x in a];b=[x/nb for x in b];t=rng.random()
   fallback=False
   if i%17==0:b=a[:];fallback=True
   elif i%19==0:b=[-x for x in a];fallback=True
   if i%23==0:t=0
   elif i%29==0:t=1
   if i%37==0:t=2;fallback=True
   a1,a2=F(*a),F(*a);b1,b2=F(*b),F(*b)
   if i%31==0:b1,b2=a1,a2;fallback=True
   old(a1,b1,t);new(a2,b2,t)
   error=max(abs(x-y) for x,y in zip(a1,a2));worst=max(error,worst)
   assert error<0.000003,(mode,i,error,a,b,t,sum(x*y for x,y in zip(a,b)),list(a1),list(a2))
   if fallback:assert bytes(a1)==bytes(a2),(mode,i,'fallback');fallback_checks+=1
   assert getcw()==mode
   checks+=1
  print(hex(mode),checks,worst,flush=True)
finally:setcw(saved)
report={'comparisons':checks,'max_component_error':worst,'allowed_error':0.000003,'exact_fallback_comparisons':fallback_checks,'floating_point_modes_preserved':True}
(root/'08-slerp/validation.json').write_text(json.dumps(report,indent=2));print(report)
