"""Install timing-only instrumentation into an isolated dgVoodoo DLL copy."""
from pathlib import Path
import struct,json,hashlib,subprocess
p=Path(__file__).parent
source=(p.parent/'phase2/build-static-patches.py').read_text()
scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(source[source.index('class PE:'):source.index('def jump(')],scope)
pe=scope['PE'](p/'DDraw-original.dll');pe.packed=False
oldentry=struct.unpack_from('<I',pe.b,pe.o+16)[0]
pe.data_alloc(64)
code,data=pe.crva,pe.drva
out=p/'13-guard-timer';out.mkdir(exist_ok=True)
asm=f'''.intel_syntax noprefix
.text
.global _entry
_entry:
 push ebp
 mov ebp,esp
 sub esp,8
 push ebx
 push esi
 push edi
 mov esi,[ebp+8]
 push dword ptr [ebp+16]
 push dword ptr [ebp+12]
 push esi
 lea eax,[esi+{oldentry}]
 call eax
 mov ebx,eax
 cmp dword ptr [ebp+12],1
 jne done
 test eax,eax
 jz done
 cmp dword ptr [esi+0x2f82],0x83ec8b55
 jne failure
 cmp word ptr [esi+0x2f86],0x0cec
 jne failure
 lea eax,[esi+{code+0x600}]
 push eax
 call dword ptr [esi+0x3a288]
 test eax,eax
 jz failure
 mov edi,eax
 lea eax,[esi+{code+0x620}]
 push eax
 push edi
 call dword ptr [esi+0x3a28c]
 test eax,eax
 jz failure
 mov [esi+{data}],eax
 lea eax,[esi+{code+0x640}]
 push eax
 push edi
 call dword ptr [esi+0x3a28c]
 test eax,eax
 jz failure
 lea edx,[esi+{data+8}]
 push edx
 call eax
 test eax,eax
 jz failure
 lea eax,[ebp-4]
 push eax
 push 0x40
 push 6
 lea eax,[esi+0x2f82]
 push eax
 call dword ptr [esi+0x210fc]
 test eax,eax
 jz failure
 mov byte ptr [esi+0x2f82],0xe9
 mov dword ptr [esi+0x2f83],{code+0x300-0x2f82-5}
 mov byte ptr [esi+0x2f87],0x90
 lea eax,[ebp-8]
 push eax
 push dword ptr [ebp-4]
 push 6
 lea eax,[esi+0x2f82]
 push eax
 call dword ptr [esi+0x210fc]
 test eax,eax
 jz failure
 lea eax,[esi+{code+0x660}]
 push eax
 push edi
 call dword ptr [esi+0x3a28c]
 test eax,eax
 jz failure
 push 6
 lea edx,[esi+0x2f82]
 push edx
 push -1
 call eax
 test eax,eax
 jz failure
 mov dword ptr [esi+{data+40}],0x55475344
 mov dword ptr [esi+{data+44}],0x31445241
 jmp done
failure:
 xor ebx,ebx
done:
 mov eax,ebx
 pop edi
 pop esi
 pop ebx
 leave
 ret 12
.org 0x300,0x90
timed_surface:
 push ebp
 mov ebp,esp
 sub esp,20
 pushfd
 pushad
 call get_base
get_base:
 pop ebx
 sub ebx,{code+0x30d}
 mov [ebp-20],ebx
 lea eax,[ebp-8]
 push eax
 call dword ptr [ebx+{data}]
 popad
 popfd
 push dword ptr [ebp+8]
 call original
 pushfd
 pushad
 mov ebx,[ebp-20]
 lea eax,[ebp-16]
 push eax
 call dword ptr [ebx+{data}]
 mov eax,[ebp-16]
 mov edx,[ebp-12]
 sub eax,[ebp-8]
 sbb edx,[ebp-4]
 inc dword ptr [ebx+{data+32}]
 add [ebx+{data+24}],eax
 adc [ebx+{data+28}],edx
 inc dword ptr [ebx+{data+16}]
 inc dword ptr [ebx+{data+32}]
 popad
 popfd
 mov esp,ebp
 pop ebp
 ret 4
.org 0x500,0x90
original:
 push ebp
 mov ebp,esp
 sub esp,12
 .byte 0xe9
 .long {0x2f88-code-0x50b}
.org 0x600,0
 .asciz "kernel32.dll"
.org 0x620,0
 .asciz "QueryPerformanceCounter"
.org 0x640,0
 .asciz "QueryPerformanceFrequency"
.org 0x660,0
 .asciz "FlushInstructionCache"
'''
(out/'timer.s').write_text(asm)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(out/'timer.s'),'-o',str(out/'timer.obj')],check=True)
b=(out/'timer.obj').read_bytes();n=struct.unpack_from('<H',b,2)[0]
sections=[b[20+i*40:60+i*40] for i in range(n)]
s=next(s for s in sections if s[:8].rstrip(b'\0')==b'.text')
size,offset=struct.unpack_from('<II',s,16);assert struct.unpack_from('<H',s,32)[0]==0
body=b[offset:offset+size]
assert body[0x308:0x30e] == bytes.fromhex('e8000000005b')
assert body[0x500:0x507] == bytes.fromhex('5589e583ec0ce9')
pos,addr=pe.reserve(len(body));assert pos==0
pe.put(pos,body);struct.pack_into('<I',pe.b,pe.o+16,code)
pe.hooks.append({'name':'guard-surface-wall-timer','entry_rva':'0x2f82','expected':'558bec83ec0c','target_rva':hex(code+0x300),'trampoline_rva':hex(code+0x500),'purpose':'QPC duration of existing surface guard handler, including readback waits; original operation retained.'})
m=pe.finish(out/'DDraw.dll');m['original_sha256']=hashlib.sha256((p/'DDraw-original.dll').read_bytes()).hexdigest()
m['counter_layout']={'qpc_pointer':0,'frequency':8,'calls':16,'ticks':24,'sequence':32,'magic':40}
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps(m,indent=2))
