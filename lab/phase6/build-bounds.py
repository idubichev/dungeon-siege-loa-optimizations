from pathlib import Path
import struct,json,hashlib,subprocess
p=Path(__file__).resolve().parent
s=(p.parent/'phase2/build-static-patches.py').read_text();scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
pe=scope['PE'](p/'08-slerp/DSLOA.exe');pe.packed=False;out=p/'13-bounds';out.mkdir(exist_ok=True)
src=['.intel_syntax noprefix','.text','.global _bounds','_bounds:','lea edx,[ecx-8]']
for i,(v,mx,mn) in enumerate([('-8','-0x2c','-0x30'),('-4','-0x40','-0x34'),('','-0x3c','-0x38')]):
 src += [f'movss xmm0,[ecx{v}]',f'ucomiss xmm0,[ebp{mx}]',f'jbe less{i}',f'jp next{i}',f'movss [ebp{mx}],xmm0',f'jmp next{i}',f'less{i}:',f'ucomiss xmm0,[ebp{mn}]',f'jae next{i}',f'jp next{i}',f'movss [ebp{mn}],xmm0',f'next{i}:']
src+=['ret'];(out/'bounds.s').write_text('\n'.join(src)+'\n')
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(out/'bounds.s'),'-o',str(out/'bounds.obj')],check=True)
b=(out/'bounds.obj').read_bytes();size,rp=struct.unpack_from('<II',b,36);body=b[rp:rp+size];assert body[-1]==0xc3
for start,end in [(0x69f6ed,0x69f75e),(0x69f81a,0x69f888)]:
 original=pe.read(start,end-start);(out/(hex(start)+'-original.bin')).write_bytes(original)
 code=(bytes.fromhex('8b4de8') if start==0x69f6ed else b'')+body[:-1]
 pos,va=pe.reserve(len(code)+5);pe.put(pos,code+b'\xe9'+struct.pack('<i',end-(va+len(code)+5)))
 pe.hook(start,original[:6],va,'mesh-bounds-sse-'+hex(start))
(out/'bounds.bin').write_bytes(body)
m=pe.finish(out/'DSLOA.exe');(out/'manifest.json').write_text(json.dumps(m,indent=2));print(m)
