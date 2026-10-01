.intel_syntax noprefix
.text
.global _entry
_entry:
 mov eax,[esp+4]
 mov eax,[eax]
 cmp dword ptr [eax],0x80000001
 jne other
 cmp dword ptr [eax+16],2
 jb other
 mov edx,0x12345678
 mov ecx,[edx]
 cmp dword ptr [eax+24],ecx
 jne other
 inc dword ptr [edx+4]
 mov eax,-1
 ret 4
other:
 xor eax,eax
 ret 4
