from pathlib import Path
import struct,json,hashlib,subprocess,capstone
p=Path(__file__).resolve().parent
s=(p.parent/'phase2/build-static-patches.py').read_text()
scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
source=p.parent/'phase6/13-bounds/DSLOA.exe';pe=scope['PE'](source);pe.packed=False
out=p/'09-stall-log';out.mkdir(exist_ok=True)
functions=[('render',0x676a6c,0,'entry'),('native_cursor',0xbaf050,24,'entry'),
 ('Sleep',0x729080,4,'iat'),('WaitForSingleObject',0x729160,8,'iat'),
 ('WaitForMultipleObjects',0x729184,16,'iat'),('ReadFile',0x729270,20,'iat'),
 ('CreateFileA',0x729274,28,'iat'),('MapViewOfFile',0x72919c,20,'iat'),
 ('MapViewOfFileEx',0x7291a8,24,'iat'),('GetCursorPos',0x7293e4,4,'iat'),
 ('SetCursorPos',0x7293dc,8,'iat'),('PeekMessageA',0x729444,20,'iat'),
 ('MsgWaitForMultipleObjects',0x729428,20,'iat'),
 ('mouse_processing',0x414b2a,12,'entry'),('game_update',0x477118,16,'entry'),
 ('ScreenToClient',0x7293e0,8,'iat'),('ClientToScreen',0x729454,8,'iat')]
for line in (p/'update-functions.tsv').read_text().splitlines():
 address,name,purges=line.split('\t');purges=json.loads(purges);assert len(purges)==1
 functions.append(('update_'+address,int(address,16),purges[0],'entry'))
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
prefixes=[];globals={};asm=['.intel_syntax noprefix','.text']
for i,(name,address,args,kind) in enumerate(functions):
 prefix=b''
 if kind=='entry':
  for ins in cs.disasm(pe.read(address,30),address):
   assert ins.mnemonic not in ['call','jmp'] and not ins.mnemonic.startswith('j')
   prefix+=ins.bytes
   if len(prefix)>=5:break
  globals[f'_resume_{i}']=address+len(prefix)
 prefixes.append(prefix)
 asm += [f'.global _log_{i}',f'_log_{i}:','push ebp','mov ebp,esp','sub esp,4','pushfd','pushad','mov ebx,esp','sub esp,528','and esp,-16','fxsave [esp]','mov edi,dword ptr fs:[0x34]',
 'push dword ptr [0x7290a0]','push dword ptr [0x729088]','push 0x11223344','push dword ptr [ebp+4]',f'push {i}','call "_enter_log@20"','mov [ebp-4],eax','mov dword ptr fs:[0x34],edi','fxrstor [esp]','mov esp,ebx','popad','popfd']
 for offset in reversed(range(8,8+args,4)):asm.append(f'push dword ptr [ebp+{offset}]')
 asm += [f'call original_{i}','pushfd','pushad','mov ebx,esp','sub esp,528','and esp,-16','fxsave [esp]','mov edi,dword ptr fs:[0x34]','push 0x11223344','push dword ptr [ebp-4]','call "_exit_log@8"','mov dword ptr fs:[0x34],edi','fxrstor [esp]','mov esp,ebx','popad','popfd','mov esp,ebp','pop ebp',f'ret {args}',f'original_{i}:']
 if kind=='iat':asm.append(f'jmp dword ptr [{address:#x}]')
 else:asm += ['.byte '+','.join(hex(x) for x in prefix),f'jmp _resume_{i}']
(out/'shim.s').write_text('\n'.join(asm)+'\n')
subprocess.run(['clang','-target','i686-w64-windows-gnu','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-asynchronous-unwind-tables','-mno-sse','-mno-sse2','-c',str(p/'stall-log.c'),'-o',str(out/'timer.obj')],check=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(out/'shim.s'),'-o',str(out/'shim.obj')],check=True)
reference=(p.parent/'phase4/coff-reference.py').read_text()
fragment=reference[reference.index('objects=[];globals='):reference.index('state=pe.data_alloc')].replace("objects=[];globals={'_alpha_resume':0x6633b7,'_wm_resume':0x41527b}",'objects=[]').replace("out/'cursor.obj'","out/'timer.obj'")
exec(fragment);state=pe.data_alloc(24+131072*32)
shim=objects[0][1][1]
for ins in cs.disasm(bytes(pe.code[shim['pos']:shim['pos']+shim['size']]),0):
 for op in ins.operands:
  field=None;value=None
  if op.type==capstone.x86.X86_OP_MEM and not op.mem.base and not op.mem.index:field=ins.disp_offset;value=op.mem.disp
  elif op.type==capstone.x86.X86_OP_IMM and op.imm==0x11223344:field=ins.imm_offset;value=op.imm
  if field is not None and (value==0x11223344 or pe.base<=value<pe.base+pe.crva):
   pos=shim['pos']+ins.address+field
   if value==0x11223344:struct.pack_into('<I',pe.code,pos,state)
   pe.absolute(pos)
sites=[]
# Only replace call instructions recognized in Ghidra's pristine program.
for line in (p/'api-calls.tsv').read_text().splitlines():
 address,iat=[int(x,16) for x in line.split()]
 for i,(name,target,args,kind) in enumerate(functions):
  if kind=='iat' and target==iat:
   instruction=pe.read(address,6)
   assert instruction==b'\xff\x15'+struct.pack('<I',iat)
   sites.append((address,i,instruction))
for address,i,original in sites:
 off=pe.offset(address-pe.base);target=globals[f'_log_{i}']
 pe.b[off:off+6]=b'\xe8'+struct.pack('<i',target-address-5)+b'\x90'
 pe.reloc.pop(address+2-pe.base,None)
for i,(name,address,args,kind) in enumerate(functions):
 if kind=='entry':
  pe.hook(address,prefixes[i],globals[f'_log_{i}'],name)
  for r in list(pe.reloc):
   if address-pe.base<=r<address-pe.base+5:del pe.reloc[r]
m=pe.finish(out/'DSLOA.exe');m.update(state_va=hex(state),slots=131072,functions=functions,
 call_sites=[{'address':hex(a),'function':functions[i][0]}for a,i,_ in sites],source=str(source))
(out/'manifest.json').write_text(json.dumps(m,indent=2));print('Diagnostic build:',len(sites),'API call sites;',sum(x[3]=='entry'for x in functions),'entry hooks.')
