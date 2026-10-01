from pathlib import Path
import struct,json,hashlib,subprocess,sys
import capstone
p=Path(__file__).parent;p3=p.parent/'phase3'
s=(p.parent/'phase2/build-static-patches.py').read_text()
scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
pe=scope['PE'](p3/'16-native-cursor/DSLOA.exe');pe.packed=False
level=sys.argv[1] if len(sys.argv)>1 else 'coarse'
out=p/('01-function-timer' if level=='coarse' else '02-render-timer');out.mkdir(exist_ok=True)
functions=[('render_pass',0x676a6c,0,0xa0),('object_draw',0x678315,4,0x144),('skinning',0x69f008,8,0x13c),('lighting',0x6a0d02,8,0x88)]
if level=='render':functions += [('draw_67901a',0x67901a,4,0),('draw_6a0808',0x6a0808,8,0),('draw_6a0684',0x6a0684,8,0),('draw_677fac',0x677fac,12,0),('visibility_677e7e',0x677e7e,4,0),('intersection_681f0f',0x681f0f,20,0)]
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
prefixes=[]
for name,entry,args,stack in functions:
    data=pe.read(entry,20);length=0
    for ins in cs.disasm(data,entry):
        assert ins.mnemonic not in ['call','jmp'] and not ins.mnemonic.startswith('j')
        length+=ins.size
        if length>=5:break
    prefixes.append(data[:length])
asm=['.intel_syntax noprefix','.text']
globals={}
for i,(name,entry,args,stack) in enumerate(functions):
    prefix=prefixes[i];globals[f'_resume_{i}']=entry+len(prefix)
    asm += [f'.global _timer_{i}',f'_timer_{i}:','push ebp','mov ebp,esp','sub esp,4','pushfd','pushad','push dword ptr [0x7290a0]','push dword ptr [0x729088]','push 0x11223344',f'push {i}','call "_profile_enter@16"','mov [ebp-4],eax','popad','popfd']
    for offset in reversed(range(8,8+args,4)):asm.append(f'push dword ptr [ebp+{offset}]')
    asm += [f'call original_{i}','pushfd','pushad','cmp dword ptr [ebp-4],0',f'je done_{i}','push 0x11223344',f'push {i}','call "_profile_exit@8"',f'done_{i}:','popad','popfd','mov esp,ebp','pop ebp',f'ret {args}',f'original_{i}:','.byte '+','.join(hex(x) for x in prefix),f'jmp _resume_{i}']
(out/'shim.s').write_text('\n'.join(asm)+'\n')
subprocess.run(['clang','-target','i686-w64-windows-gnu',f'-DFUNCTION_COUNT={len(functions)}','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-asynchronous-unwind-tables','-mno-sse','-mno-sse2','-c',str(p/'function-timer.c'),'-o',str(out/'timer.obj')],check=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(out/'shim.s'),'-o',str(out/'shim.obj')],check=True)
# Reuse the already exercised COFF linker, without its cursor-specific hooks.
reference=(p/'coff-reference.py').read_text()
fragment=reference[reference.index('objects=[];globals='):reference.index('state=pe.data_alloc')]
fragment=fragment.replace("objects=[];globals={'_alpha_resume':0x6633b7,'_wm_resume':0x41527b}",'objects=[]')
fragment=fragment.replace("out/'cursor.obj'","out/'timer.obj'")
exec(fragment)
thread_bytes=16+32*len(functions)+24*128
state=pe.data_alloc(24+8*thread_bytes)
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
shim=objects[0][1][1]
for ins in cs.disasm(bytes(pe.code[shim['pos']:shim['pos']+shim['size']]),0):
    for op in ins.operands:
        field=None;value=None
        if op.type==capstone.x86.X86_OP_MEM and not op.mem.base and not op.mem.index:field=ins.disp_offset;value=op.mem.disp
        elif op.type==capstone.x86.X86_OP_IMM and op.imm==0x11223344:field=ins.imm_offset;value=op.imm
        if field is not None and (value==0x11223344 or 0x400000<=value<0x800000):
            pos=shim['pos']+ins.address+field
            if value==0x11223344:struct.pack_into('<I',pe.code,pos,state)
            pe.absolute(pos)
for i,(name,entry,args,stack) in enumerate(functions):
    expected=prefixes[i]
    pe.hook(entry,expected,globals[f'_timer_{i}'],name)
    for r in list(pe.reloc):
        if entry-pe.base<=r<entry-pe.base+5:del pe.reloc[r]
m=pe.finish(out/'DSLOA.exe');m['state_va']=hex(state);m['functions']=[{'name':n,'entry':hex(e),'argument_bytes':a} for n,e,a,st in functions]
m['layout']={'header_bytes':24,'thread_bytes':thread_bytes,'threads':8,'stats_offset':16,'stat_bytes':32,'frame_bytes':24,'frames':128}
m['method']='Diagnostic QPC wrappers; inclusive and exclusive elapsed time by function and thread, recursion tracked. Native cursor remains enabled.'
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
