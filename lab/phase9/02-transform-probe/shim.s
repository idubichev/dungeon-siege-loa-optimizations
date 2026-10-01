.intel_syntax noprefix
.text
.global _transform_hook
_transform_hook:
 pushfd
 pushad
 push 0x11223344
 push ebx
 push dword ptr [ebp-0x30]
 call "_probe@12"
 popad
 popfd
 mov eax,dword ptr [ebx+0x98]
 mov [ebp-0x70],eax
 mov [ebp-0x6c],eax
 mov [ebp-0x68],eax
 jmp _resume
