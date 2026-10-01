from pathlib import Path
import struct,json,hashlib,subprocess
p=Path(__file__).parent;p2=p.parent/'phase2';game=Path('~/Applications/Dungeon Siege Profile Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege')
s=(p2/'build-static-patches.py').read_text();scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n};exec(s[s.index('class PE:'):s.index('def jump(')],scope);PE=scope['PE']
original=p/'DDraw-original.dll'
if not original.exists():original.write_bytes((game/'DDraw.dll').read_bytes())
pe=PE(original);pe.packed=False;oldentry=struct.unpack_from('<I',pe.b,pe.o+16)[0];out=p/'11-full-surface';out.mkdir(exist_ok=True)
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
 cmp word ptr [esi+0x30d7],0x988a
 jne failure
 cmp dword ptr [esi+0x30d9],0x416
 jne failure
 lea eax,[ebp-4]
 push eax
 push 0x40
 push 6
 lea eax,[esi+0x30d7]
 push eax
 call dword ptr [esi+0x210fc]
 test eax,eax
 jz failure
 mov word ptr [esi+0x30d7],0xdb32
 mov dword ptr [esi+0x30d9],0x90909090
 lea eax,[ebp-8]
 push eax
 push dword ptr [ebp-4]
 push 6
 lea eax,[esi+0x30d7]
 push eax
 call dword ptr [esi+0x210fc]
 test eax,eax
 jz failure
 lea eax,[esi+{pe.crva+0x200}]
 push eax
 call dword ptr [esi+0x3a288]
 test eax,eax
 jz failure
 lea edx,[esi+{pe.crva+0x220}]
 push edx
 push eax
 call dword ptr [esi+0x3a28c]
 test eax,eax
 jz failure
 mov edi,eax
 push 6
 lea eax,[esi+0x30d7]
 push eax
 push -1
 call edi
 test eax,eax
 jnz done
failure:
 xor ebx,ebx
done:
 mov eax,ebx
 pop edi
 pop esi
 pop ebx
 leave
 ret 12
'''
(out/'init.s').write_text(asm);subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(out/'init.s'),'-o',str(out/'init.obj')],check=True)
b=(out/'init.obj').read_bytes();sz,off=struct.unpack_from('<II',b,36);assert struct.unpack_from('<H',b,52)[0]==0;code=b[off:off+sz];assert len(code)<0x200
code+=b'\x90'*(0x200-len(code))+b'kernel32.dll\0';code+=b'\0'*(0x220-len(code))+b'FlushInstructionCache\0';pos,addr=pe.reserve(len(code));assert pos==0;pe.put(pos,code);struct.pack_into('<I',pe.b,pe.o+16,pe.crva)
pe.hooks.append({'name':'force-existing-full-surface-path','entry':hex(pe.base+0x30d7),'original':'8a9816040000','replacement':'32db90909090','installation':'After original packed DllMain succeeds on DLL_PROCESS_ATTACH; validate original instruction, protect/write/restore/flush, fail closed.'})
m=pe.finish(out/'DDraw.dll');m['old_entrypoint_rva']=hex(oldentry);m['original_sha256']=hashlib.sha256(original.read_bytes()).hexdigest();(out/'manifest.json').write_text(json.dumps(m,indent=2));(game/'DDraw.dll').write_bytes((out/'DDraw.dll').read_bytes());print(json.dumps(m,indent=2))
