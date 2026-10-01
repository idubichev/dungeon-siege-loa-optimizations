.intel_syntax noprefix
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
 lea eax,[esi+238450]
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
 lea eax,[esi+247296]
 push eax
 call dword ptr [esi+0x3a288]
 test eax,eax
 jz failure
 mov edi,eax
 lea eax,[esi+247328]
 push eax
 push edi
 call dword ptr [esi+0x3a28c]
 test eax,eax
 jz failure
 mov [esi+311296],eax
 lea eax,[esi+247360]
 push eax
 push edi
 call dword ptr [esi+0x3a28c]
 test eax,eax
 jz failure
 lea edx,[esi+311304]
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
 mov dword ptr [esi+0x2f83],234361
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
 lea eax,[esi+247392]
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
 mov dword ptr [esi+311336],0x55475344
 mov dword ptr [esi+311340],0x31445241
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
 sub ebx,246541
 mov [ebp-20],ebx
 lea eax,[ebp-8]
 push eax
 call dword ptr [ebx+311296]
 popad
 popfd
 push dword ptr [ebp+8]
 call original
 pushfd
 pushad
 mov ebx,[ebp-20]
 lea eax,[ebp-16]
 push eax
 call dword ptr [ebx+311296]
 mov eax,[ebp-16]
 mov edx,[ebp-12]
 sub eax,[ebp-8]
 sbb edx,[ebp-4]
 inc dword ptr [ebx+311328]
 add [ebx+311320],eax
 adc [ebx+311324],edx
 inc dword ptr [ebx+311312]
 inc dword ptr [ebx+311328]
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
 .long -234883
.org 0x600,0
 .asciz "kernel32.dll"
.org 0x620,0
 .asciz "QueryPerformanceCounter"
.org 0x640,0
 .asciz "QueryPerformanceFrequency"
.org 0x660,0
 .asciz "FlushInstructionCache"
