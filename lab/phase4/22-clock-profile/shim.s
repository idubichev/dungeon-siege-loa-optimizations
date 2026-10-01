.intel_syntax noprefix
.text
.global _timer_0
_timer_0:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 0
call "_profile_enter@16"
mov [ebp-4],eax
fxrstor [esp]
mov esp,ebx
popad
popfd
call original_0
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
cmp dword ptr [ebp-4],0
je done_0
push 0x11223344
push 0
call "_profile_exit@8"
done_0:
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 0
original_0:
.byte 0x55,0x8b,0xec,0x81,0xec,0xa0,0x0,0x0,0x0
jmp _resume_0
.global _timer_1
_timer_1:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 1
call "_profile_enter@16"
mov [ebp-4],eax
fxrstor [esp]
mov esp,ebx
popad
popfd
call original_1
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
cmp dword ptr [ebp-4],0
je done_1
push 0x11223344
push 1
call "_profile_exit@8"
done_1:
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 0
original_1:
.byte 0x55,0x8b,0xec,0x83,0xec,0x20
jmp _resume_1
.global _timer_2
_timer_2:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 2
call "_profile_enter@16"
mov [ebp-4],eax
fxrstor [esp]
mov esp,ebx
popad
popfd
call original_2
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
cmp dword ptr [ebp-4],0
je done_2
push 0x11223344
push 2
call "_profile_exit@8"
done_2:
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 0
original_2:
.byte 0x55,0x8b,0xec,0x83,0xe4,0xf8
jmp _resume_2
