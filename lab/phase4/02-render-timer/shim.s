.intel_syntax noprefix
.text
.global _timer_0
_timer_0:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 0
call "_profile_enter@16"
mov [ebp-4],eax
popad
popfd
call original_0
pushfd
pushad
cmp dword ptr [ebp-4],0
je done_0
push 0x11223344
push 0
call "_profile_exit@8"
done_0:
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
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 1
call "_profile_enter@16"
mov [ebp-4],eax
popad
popfd
push dword ptr [ebp+8]
call original_1
pushfd
pushad
cmp dword ptr [ebp-4],0
je done_1
push 0x11223344
push 1
call "_profile_exit@8"
done_1:
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_1:
.byte 0x55,0x8b,0xec,0x81,0xec,0x44,0x1,0x0,0x0
jmp _resume_1
.global _timer_2
_timer_2:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 2
call "_profile_enter@16"
mov [ebp-4],eax
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_2
pushfd
pushad
cmp dword ptr [ebp-4],0
je done_2
push 0x11223344
push 2
call "_profile_exit@8"
done_2:
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_2:
.byte 0x55,0x8b,0xec,0x81,0xec,0x3c,0x1,0x0,0x0
jmp _resume_2
.global _timer_3
_timer_3:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 3
call "_profile_enter@16"
mov [ebp-4],eax
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_3
pushfd
pushad
cmp dword ptr [ebp-4],0
je done_3
push 0x11223344
push 3
call "_profile_exit@8"
done_3:
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_3:
.byte 0x55,0x8b,0xec,0x81,0xec,0x88,0x0,0x0,0x0
jmp _resume_3
.global _timer_4
_timer_4:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 4
call "_profile_enter@16"
mov [ebp-4],eax
popad
popfd
push dword ptr [ebp+8]
call original_4
pushfd
pushad
cmp dword ptr [ebp-4],0
je done_4
push 0x11223344
push 4
call "_profile_exit@8"
done_4:
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_4:
.byte 0x55,0x8b,0xec,0x81,0xec,0x44,0x1,0x0,0x0
jmp _resume_4
.global _timer_5
_timer_5:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 5
call "_profile_enter@16"
mov [ebp-4],eax
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_5
pushfd
pushad
cmp dword ptr [ebp-4],0
je done_5
push 0x11223344
push 5
call "_profile_exit@8"
done_5:
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_5:
.byte 0x55,0x8b,0xec,0x83,0xec,0x30
jmp _resume_5
.global _timer_6
_timer_6:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 6
call "_profile_enter@16"
mov [ebp-4],eax
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_6
pushfd
pushad
cmp dword ptr [ebp-4],0
je done_6
push 0x11223344
push 6
call "_profile_exit@8"
done_6:
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_6:
.byte 0x55,0x8b,0xec,0x83,0xec,0x60
jmp _resume_6
.global _timer_7
_timer_7:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 7
call "_profile_enter@16"
mov [ebp-4],eax
popad
popfd
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_7
pushfd
pushad
cmp dword ptr [ebp-4],0
je done_7
push 0x11223344
push 7
call "_profile_exit@8"
done_7:
popad
popfd
mov esp,ebp
pop ebp
ret 12
original_7:
.byte 0x55,0x8b,0xec,0x83,0xec,0x58
jmp _resume_7
.global _timer_8
_timer_8:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 8
call "_profile_enter@16"
mov [ebp-4],eax
popad
popfd
push dword ptr [ebp+8]
call original_8
pushfd
pushad
cmp dword ptr [ebp-4],0
je done_8
push 0x11223344
push 8
call "_profile_exit@8"
done_8:
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_8:
.byte 0xa1,0x80,0xcf,0x7a,0x0
jmp _resume_8
.global _timer_9
_timer_9:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push 9
call "_profile_enter@16"
mov [ebp-4],eax
popad
popfd
push dword ptr [ebp+24]
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_9
pushfd
pushad
cmp dword ptr [ebp-4],0
je done_9
push 0x11223344
push 9
call "_profile_exit@8"
done_9:
popad
popfd
mov esp,ebp
pop ebp
ret 20
original_9:
.byte 0x55,0x8b,0xec,0x83,0xec,0x14
jmp _resume_9
