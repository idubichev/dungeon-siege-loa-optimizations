.intel_syntax noprefix
.text
.global _native_cursor
.global _cursor_wm
_native_cursor:
 pushad
 mov esi,[esp+44]
 push dword ptr [0x7290a0]
 push dword ptr [0x729088]
 push 0x11223344
 push dword ptr [ecx+0x120]
 push dword ptr [ecx+0x11c]
 push esi
 call "_build_cursor@24"
 test eax,eax
 jz fallback
 popad
 ret 16
fallback:
 popad
 push ebp
 mov ebp,esp
 sub esp,0x84
 jmp _alpha_resume
_cursor_wm:
 push dword ptr [0x11223344]
 call dword ptr [0x729400]
 jmp _wm_resume
