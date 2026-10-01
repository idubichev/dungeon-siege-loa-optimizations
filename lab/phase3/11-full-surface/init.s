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
 lea eax,[esi+246272]
 push eax
 call dword ptr [esi+0x3a288]
 test eax,eax
 jz failure
 lea edx,[esi+246304]
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
