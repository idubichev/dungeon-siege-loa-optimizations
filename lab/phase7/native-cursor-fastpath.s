.intel_syntax noprefix
.text
.global _native_fastpath
_native_fastpath:
 pushfd
 pushad
 mov esi,esp
 sub esp,528
 and esp,-16
 fxsave [esp]
 push dword ptr [0x7290a0]
 push dword ptr [0x729088]
 push 0xbbf000
 push 0
 push 0
 push 0
 call _native_arrow
 test eax,eax
 jz software
 fxrstor [esp]
 mov esp,esi
 popad
 popfd
 mov byte ptr [ebx+0x145],0
 jmp _cursor_finish
software:
 fxrstor [esp]
 mov esp,esi
 popad
 popfd
 cmp byte ptr [ebp+8],0
 je _software_main
 jmp _software_background
