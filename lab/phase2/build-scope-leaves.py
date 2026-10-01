from pathlib import Path
import subprocess,struct
p=Path(__file__).parent
for name in ['quat','blend']:
 s=(p.parent/(name+'-sse.s')).read_text();start=s.index('    stmxcsr 4(%esp)');end=s.index('    ldmxcsr 8(%esp)',start)+len('    ldmxcsr 8(%esp)\n');s=s[:start]+s[end:];s=s.replace('    ldmxcsr 4(%esp)\n','');(p/(name+'-scoped.s')).write_text(s)
 subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(p/(name+'-scoped.s')),'-o',str(p/(name+'-scoped.obj'))],check=True)
 b=(p/(name+'-scoped.obj')).read_bytes();sz,off=struct.unpack_from('<II',b,36);assert struct.unpack_from('<H',b,52)[0]==0;(p/(name+'-scoped.bin')).write_bytes(b[off:off+sz]);print(name,sz)
 s=(p.parent/('test-'+name+'-win32.py')).read_text().replace("(lab/'"+name+"-original.bin')","(lab.parent/'"+name+"-original.bin')").replace(name+'-sse.bin',name+'-scoped.bin').replace(name+'-validation.json',name+'-scoped-validation.json')
 marker='setcw=c.CFUNCTYPE'
 a=s.index(marker)
 fn='replacement' if name=='quat' else 'new'
 extra='''getcsr=c.CFUNCTYPE(c.c_uint)(alloc(bytes.fromhex('83ec040fae1c248b042483c404c3')))
setcsr=c.CFUNCTYPE(None,c.c_uint)(alloc(bytes.fromhex('0fae542404c3')))
raw_call=FN
def FN(*args):
    previous=getcsr();setcsr((previous&0xffff1fbf)|((getcw()<<3)&0x6000))
    try:return raw_call(*args)
    finally:setcsr(previous)
'''.replace('FN',fn)
 s=s[:a]+extra+s[a:];(p/('test-'+name+'-scoped-win32.py')).write_text(s)
