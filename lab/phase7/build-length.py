from pathlib import Path
import struct,json,hashlib,subprocess
p=Path(__file__).resolve().parent
s=(p.parent/'phase2/build-static-patches.py').read_text()
scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
pe=scope['PE'](p.parent/'phase6/13-bounds/DSLOA.exe');pe.packed=False
out=p/'01-length';out.mkdir(exist_ok=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(out/'length.s'),'-o',str(out/'length.obj')],check=True)
b=(out/'length.obj').read_bytes();size,rp=struct.unpack_from('<II',b,36);code=b[rp:rp+size]
old=pe.read(0x43e8c3,31)
assert old.hex()=='d94108d94104d901d9c0d8c9d9c2d8cbdec1d9c3d8ccdec1dddbddd8ddd8c3'
pos,va=pe.reserve(len(code));pe.put(pos,code)
pe.hook(0x43e8c3,old[:6],va,'squared-length-stack')
m=pe.finish(out/'DSLOA.exe')
(out/'original.bin').write_bytes(old);(out/'length.bin').write_bytes(code)
(out/'manifest.json').write_text(json.dumps(m,indent=2));print(m)
