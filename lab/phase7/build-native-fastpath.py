"""Bypass software-cursor surface copies after original worker coordination."""
from pathlib import Path
import struct,json,hashlib,subprocess,capstone
p=Path(__file__).resolve().parent
s=(p.parent/'phase2/build-static-patches.py').read_text()
scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
source=p.parent/'phase6/13-bounds/DSLOA.exe';pe=scope['PE'](source);pe.packed=False
out=p/'22-native-fastpath';out.mkdir(exist_ok=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(p/'native-cursor-fastpath.s'),'-o',str(out/'shim.obj')],check=True)
reference=(p.parent/'phase4/coff-reference.py').read_text()
fragment=reference[reference.index('objects=[];globals='):reference.index('state=pe.data_alloc')]
fragment=fragment.replace("{'_alpha_resume':0x6633b7,'_wm_resume':0x41527b}","{'_native_arrow':0xbaf050,'_cursor_finish':0x662fa9,'_software_main':0x662a9d,'_software_background':0x662a1c}")
fragment=fragment.replace("[out/'shim.obj',out/'cursor.obj']","[out/'shim.obj']")
exec(fragment)
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
sec=objects[0][1][1]
for ins in cs.disasm(bytes(pe.code[sec['pos']:sec['pos']+sec['size']]),0):
 for op in ins.operands:
  if op.type==capstone.x86.X86_OP_MEM and not op.mem.base and not op.mem.index and pe.base<=op.mem.disp<pe.base+pe.crva:
   pe.absolute(sec['pos']+ins.address+ins.disp_offset)
  elif op.type==capstone.x86.X86_OP_IMM and op.imm==0xbbf000:
   pe.absolute(sec['pos']+ins.address+ins.imm_offset)
old=bytes.fromhex('807d08000f8481000000');assert pe.read(0x662a12,10)==old
pe.hook(0x662a12,old,globals['_native_fastpath'],'native-cursor-skip-software-surface-copies')
m=pe.finish(out/'DSLOA.exe');m.update(source=str(source),symbols=globals,description='After original cursor event/window guards, update the native arrow and return before software cursor buffer copies. Native API failure preserves the original software branch.')
(out/'manifest.json').write_text(json.dumps(m,indent=2));print(m['sha256'])
