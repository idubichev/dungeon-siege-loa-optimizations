.intel_syntax noprefix
.text
.global _transform_hook
_transform_hook:
 pushfd
 pushad
 push 0x11223344
 push ebx
 push dword ptr [ebp-0x30]
 call "_apply_cached@12"
 test eax,eax
 jz fallback
 popad
 popfd
 mov eax,dword ptr [ebx+0x98]
 mov [ebp-0x70],eax
 mov [ebp-0x6c],eax
 mov [ebp-0x68],eax
 jmp _resume
fallback:
 popad
 popfd
 mov ecx,[ebp-0x30]
 push esi
 call _translation
 mov ecx,[ebp-0x30]
 push edi
 call _rotation
 fld dword ptr [ebx+0x98]
 mov ecx,[ebp-0x30]
 fst dword ptr [ebp-0x70]
 lea eax,[ebp-0x70]
 fst dword ptr [ebp-0x6c]
 push eax
 fstp dword ptr [ebp-0x68]
 call _scale
 jmp _resume
