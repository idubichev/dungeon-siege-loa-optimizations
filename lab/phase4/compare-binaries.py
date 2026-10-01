from pathlib import Path
import pefile,capstone,struct,json,re,hashlib
p=Path(__file__).parent;game=Path.home()/'Applications/Dungeon Siege Profile Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
paths={'base':game/'DungeonSiege.exe','loa':p.parent/'phase2/rollback/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege/DSLOA.exe'}
es={k:pefile.PE(str(v)) for k,v in paths.items()};cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
out=p/'21-binary-comparison';out.mkdir(exist_ok=True)
def read(e,va,n):return e.get_data(va-e.OPTIONAL_HEADER.ImageBase,n)
report={}
for k,e in es.items():
 imports={i.address:i.name.decode() for d in e.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name}
 s=e.sections[0];data=s.get_data();base=e.OPTIONAL_HEADER.ImageBase+s.VirtualAddress;refs={}
 for addr,name in imports.items():
  if name in ('QueryPerformanceCounter','GetTickCount','Sleep','timeGetTime'):
   hits=[base+m.start() for m in re.finditer(re.escape(struct.pack('<I',addr)),data)];refs[name]=[hex(x) for x in hits]
   lines=[]
   for hit in hits:
    lines.append('\nREFERENCE '+hex(hit))
    # Start at nearest conventional prologue where available.
    off=hit-base;start=data.rfind(b'\x55\x8b\xec',max(0,off-160),off)
    if start<0:start=max(0,off-30)
    for i in cs.disasm(data[start:off+90],base+start):lines.append(f'{i.address:08x} {i.mnemonic} {i.op_str}')
   (out/f'{k}-{name}.asm').write_text('\n'.join(lines))
 report[k]={'path':str(paths[k]),'sha256':hashlib.sha256(paths[k].read_bytes()).hexdigest(),'timing_import_refs':refs,'rdtsc_byte_candidates':[hex(base+m.start()) for m in re.finditer(b'\x0f\x31',data)]}
# Relocation-independent initial instruction signatures, with calls, branch targets,
# and absolute addresses wildcarded. The game compilers can lay out functions differently.
functions={'triangle':0x728343,'skin':0x69f008,'slerp':0x69fa05,'vec3':0x43e774,'ray':0x69395c,'vertical_ray':0x693c45,'render':0x676a6c,'alpha_cursor':0x6633ae,'length':0x43e8bb,'dot':0x43e8c3}
e=es['base'];sec=e.sections[0];base=e.OPTIONAL_HEADER.ImageBase+sec.VirtualAddress;data=sec.get_data();matches={}
for name,addr in functions.items():
 ins=list(cs.disasm(read(es['loa'],addr,100),addr))[:16];pat=[]
 for i in ins:
  wildcard=set()
  for op in i.operands:
   if op.type==capstone.x86.X86_OP_MEM and not op.mem.base and not op.mem.index and op.mem.disp:
    wildcard.update(range(i.disp_offset,i.disp_offset+i.disp_size))
   if op.type==capstone.x86.X86_OP_IMM and (i.group(capstone.CS_GRP_CALL) or i.group(capstone.CS_GRP_JUMP) or 0x400000<=op.imm<0x800000):
    wildcard.update(range(i.imm_offset,i.imm_offset+i.imm_size))
  pat.extend(b'.' if j in wildcard else re.escape(bytes([b])) for j,b in enumerate(i.bytes))
 hits=[base+m.start() for m in re.finditer(b''.join(pat),data,re.DOTALL)]
 matches[name]={'loa_va':hex(addr),'base_candidates':[hex(x) for x in hits],'signature_instructions':len(ins)}
 if len(hits)==1:
  for version,va in [('base',hits[0]),('loa',addr)]:
   body=list(cs.disasm(read(es[version],va,2500 if name=='triangle' else 600),va));(out/f'{name}-{version}.asm').write_text('\n'.join(f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in body)+'\n')
report['hot_function_signatures']=matches;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
