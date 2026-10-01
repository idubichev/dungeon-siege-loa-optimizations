.intel_syntax noprefix
.text
.global _entry
_entry:
 push ebp
 mov ebp,esp
 sub esp,4
 push ebx
 push esi
 push edi
 mov esi,[ebp+8]
 mov edi,[ebp+12]
 mov ebx,[ebp+20]
again:
 lea eax,[ebp-4]
 push eax
 push dword ptr [ebp+16]
 push 4096
 push esi
 call ebx
 test eax,eax
 jz finished
 movzx eax,byte ptr [esi]
 dec edi
 jnz again
 mov eax,1
finished:
 pop edi
 pop esi
 pop ebx
 leave
 ret 16
