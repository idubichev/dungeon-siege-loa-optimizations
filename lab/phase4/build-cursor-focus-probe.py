"""Link freestanding cursor code into a new isolated EXE code/data section."""
from pathlib import Path
import struct,json,hashlib,subprocess
import capstone
p=Path(__file__).parent.parent/'phase3'
s=(p.parent/'phase2/build-static-patches.py').read_text()
scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
pe=scope['PE'](p/'DS15-original.exe');pe.packed=False
out=p.parent/'phase4/38-cursor-focus-probe';out.mkdir(exist_ok=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-asynchronous-unwind-tables','-mno-sse','-mno-sse2','-c',str(p.parent/'phase4/native-cursor-focus-probe.c'),'-o',str(out/'cursor.obj')],check=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(p/'native-cursor.s'),'-o',str(out/'shim.obj')],check=True)
objects=[];globals={'_alpha_resume':0x6633b7,'_wm_resume':0x41527b}
for path in [out/'shim.obj',out/'cursor.obj']:
    b=path.read_bytes();n=struct.unpack_from('<H',b,2)[0];symptr,nsym=struct.unpack_from('<II',b,8)
    stringtable=b[symptr+nsym*18:]
    def name(raw):
        if raw[:4]==b'\0'*4:
            k=struct.unpack_from('<I',raw,4)[0];return stringtable[k:stringtable.find(b'\0',k)].decode()
        return raw.rstrip(b'\0').decode()
    symbols={};i=0
    while i<nsym:
        a=symptr+i*18;raw=b[a:a+18];value,section,kind,storage,aux=struct.unpack_from('<IhHBB',raw,8)
        symbols[i]={'name':name(raw[:8]),'value':value,'section':section,'storage':storage};i+=1+aux
    sections={}
    for i in range(n):
        raw=b[20+i*40:60+i*40];nm=raw[:8].rstrip(b'\0').decode();size,offset,relocptr=struct.unpack_from('<III',raw,16);nr=struct.unpack_from('<H',raw,32)[0]
        if not size:continue
        if nm.startswith(('.text','.rdata')):
            pos,va=pe.reserve(size);body=b[offset:offset+size];pe.put(pos,body)
            relocs=[struct.unpack_from('<IIH',b,relocptr+j*10) for j in range(nr)]
            sections[i+1]={'name':nm,'pos':pos,'va':va,'size':size,'relocs':relocs}
        elif nm not in ['.llvm_addrsig']:
            raise RuntimeError(('Unexpected nonempty section',nm,size))
    for sy in symbols.values():
        if sy['storage']==2 and sy['section'] in sections:
            globals[sy['name']]=sections[sy['section']]['va']+sy['value']
    objects.append((symbols,sections))
for symbols,sections in objects:
    for sec in sections.values():
        for off,symi,kind in sec['relocs']:
            sy=symbols[symi]
            target=sections[sy['section']]['va']+sy['value'] if sy['section'] in sections else globals[sy['name']]
            pos=sec['pos']+off;addend=struct.unpack_from('<i',pe.code,pos)[0]
            if kind==6:
                struct.pack_into('<I',pe.code,pos,(target+addend)&0xffffffff);pe.absolute(pos)
            elif kind==20:
                struct.pack_into('<i',pe.code,pos,target+addend-(pe.base+pe.crva+pos+4))
            else:raise RuntimeError(('Unsupported COFF relocation',kind))
state=pe.data_alloc(40+64*28+8192+24)
# Relocate explicit module/import/state operands in the tiny assembly shim.
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
shim=objects[0][1][1]
for ins in cs.disasm(bytes(pe.code[shim['pos']:shim['pos']+shim['size']]),0):
    for op in ins.operands:
        field=None;value=None
        if op.type==capstone.x86.X86_OP_MEM and not op.mem.base and not op.mem.index:
            field=ins.disp_offset;value=op.mem.disp
        elif op.type==capstone.x86.X86_OP_IMM and op.imm==0x11223344:
            field=ins.imm_offset;value=op.imm
        if field is not None and (value==0x11223344 or 0x400000<=value<0x800000):
            pos=shim['pos']+ins.address+field
            if value==0x11223344:struct.pack_into('<I',pe.code,pos,state)
            pe.absolute(pos)
pe.hook(0x6633ae,bytes.fromhex('558bec81ec84000000'),globals['_native_cursor'],'native-cursor-alpha-replacement')
pe.hook(0x415274,bytes.fromhex('57ff1500947200'),globals['_cursor_wm'],'native-cursor-window-message')
# The replaced indirect call had an absolute import operand. Its relocation
# must not later be applied to the new relative jump/NOP bytes.
for r in list(pe.reloc):
    if 0x415274-pe.base <= r < 0x41527b-pe.base:del pe.reloc[r]
# The seven-byte window-message sequence resumes after both original instructions.
off=pe.offset(0x415274-pe.base);pe.b[off+5:off+7]=b'\x90\x90'
m=pe.finish(out/'DSLOA.exe');m['input_sha256']=hashlib.sha256((p/'DS15-original.exe').read_bytes()).hexdigest()
m['symbols']=globals;m['state_va']=hex(state);m['state_bytes']=40+64*28+8192+24
m['limitations']=['Cursor images treated as immutable; cache key includes image, pixels, dimensions and hotspot.','Up to 64 native cursor handles; unsupported images or allocation failures use original software cursor.','Cursor handles remain owned by the game until process exit.','Timing DLL is separate, experimental and not part of this EXE.']
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
