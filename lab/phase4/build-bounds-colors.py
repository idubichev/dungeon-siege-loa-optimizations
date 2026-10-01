from pathlib import Path
import struct,json,hashlib,subprocess
import capstone
p=Path(__file__).parent
s=(p.parent/'phase2/build-static-patches.py').read_text()
scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
pe=scope['PE'](p/'04-cursor-colors/DSLOA.exe');pe.packed=False
out=p/'06-bounds-colors';out.mkdir(exist_ok=True)
regions=[(0x69f6f3,0x69f75e),(0x69f81d,0x69f888)]
asm=['.intel_syntax noprefix','.text'];globals={}
for i,(start,end) in enumerate(regions):
    globals[f'_resume_{i}']=end
    asm += [f'.global _bounds_{i}',f'_bounds_{i}:','pushfd','pushad','push edx','push ebp','call "_update_bounds@8"','popad','popfd',f'jmp _resume_{i}']
    (out/f'original-{i}.bin').write_bytes(pe.read(start,end-start)+b'\xc3')
(out/'shim.s').write_text('\n'.join(asm)+'\n')
subprocess.run(['clang','-target','i686-w64-windows-gnu','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-asynchronous-unwind-tables','-mno-sse','-mno-sse2','-c',str(p/'bounds.c'),'-o',str(out/'bounds.obj')],check=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(out/'shim.s'),'-o',str(out/'shim.obj')],check=True)
reference=(p/'coff-reference.py').read_text();fragment=reference[reference.index('objects=[];globals='):reference.index('state=pe.data_alloc')]
fragment=fragment.replace("objects=[];globals={'_alpha_resume':0x6633b7,'_wm_resume':0x41527b}",'objects=[]').replace("out/'cursor.obj'","out/'bounds.obj'")
exec(fragment)
for i,(start,end) in enumerate(regions):pe.hook(start,pe.read(start,end-start),globals[f'_bounds_{i}'],f'binary32-bounds-{i}')
# The C kernel has no external references; preserve a standalone copy for tests.
section=objects[1][1][1];assert not section['relocs']
(out/'bounds.bin').write_bytes(bytes(pe.code[section['pos']:section['pos']+section['size']]))
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
assert not any(i.mnemonic.startswith('f') or 'xmm' in i.op_str for i in cs.disasm((out/'bounds.bin').read_bytes(),0))
m=pe.finish(out/'DSLOA.exe');m['symbols']=globals;m['method']='Replace two per-vertex x87 min/max comparison blocks with exact integer binary32 ordering; preserve unordered NaN and signed zero behavior.'
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
