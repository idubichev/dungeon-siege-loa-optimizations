from pathlib import Path
import struct,json,hashlib,subprocess,sys
import capstone
p=Path(__file__).parent;s=(p.parent/'phase2/build-static-patches.py').read_text();scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
source=p/sys.argv[1]/'DSLOA.exe';pe=scope['PE'](source);pe.packed=False;out=p/sys.argv[2];out.mkdir(exist_ok=True)
original=bytes.fromhex('558bec81eca0000000');assert pe.read(0x676a6c,9)==original
(out/'shim.s').write_text('.intel_syntax noprefix\n.text\n.global _frame_entry\n_frame_entry:\npushfd\npushad\npush dword ptr [0x7290a0]\npush dword ptr [0x729088]\npush 0x11223344\ncall "_frame_tick@12"\npopad\npopfd\n.byte '+','.join(hex(x) for x in original)+'\njmp _resume\n')
subprocess.run(['clang','-target','i686-w64-windows-gnu','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-asynchronous-unwind-tables','-mno-sse','-mno-sse2','-c',str(p/'frame-clock.c'),'-o',str(out/'clock.obj')],check=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(out/'shim.s'),'-o',str(out/'shim.obj')],check=True)
globals={'_resume':0x676a75};reference=(p/'coff-reference.py').read_text();fragment=reference[reference.index('objects=[];globals='):reference.index('state=pe.data_alloc')]
fragment=fragment.replace("objects=[];globals={'_alpha_resume':0x6633b7,'_wm_resume':0x41527b}",'objects=[]').replace("out/'cursor.obj'","out/'clock.obj'")
exec(fragment);state=pe.data_alloc(24+16384*8)
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True;shim=objects[0][1][1]
for ins in cs.disasm(bytes(pe.code[shim['pos']:shim['pos']+shim['size']]),0):
 for op in ins.operands:
  field=None;value=None
  if op.type==capstone.x86.X86_OP_MEM and not op.mem.base and not op.mem.index:field=ins.disp_offset;value=op.mem.disp
  elif op.type==capstone.x86.X86_OP_IMM and op.imm==0x11223344:field=ins.imm_offset;value=op.imm
  if field is not None and (value==0x11223344 or 0x400000<=value<0x800000):
   pos=shim['pos']+ins.address+field
   if value==0x11223344:struct.pack_into('<I',pe.code,pos,state)
   pe.absolute(pos)
pe.hook(0x676a6c,original,globals['_frame_entry'],'frame-clock');m=pe.finish(out/'DSLOA.exe');m.update(state_va=hex(state),slots=16384,source=str(source),method='QPC timestamp once per render-pass entry; CPU frame cadence, not GPU presentation timing.')
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
