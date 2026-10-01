.intel_syntax noprefix
.text
.global _log_0
_log_0:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 0
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
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
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
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
.global _log_1
_log_1:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 1
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+28]
push dword ptr [ebp+24]
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_1
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 24
original_1:
.byte 0x53,0x57,0x56,0x83,0xec,0x14
jmp _resume_1
.global _log_2
_log_2:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 2
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_2
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_2:
jmp dword ptr [0x729080]
.global _log_3
_log_3:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 3
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_3
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_3:
jmp dword ptr [0x729160]
.global _log_4
_log_4:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 4
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 16
original_4:
jmp dword ptr [0x729184]
.global _log_5
_log_5:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 5
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+24]
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_5
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 20
original_5:
jmp dword ptr [0x729270]
.global _log_6
_log_6:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 6
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+32]
push dword ptr [ebp+28]
push dword ptr [ebp+24]
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_6
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 28
original_6:
jmp dword ptr [0x729274]
.global _log_7
_log_7:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 7
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+24]
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_7
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 20
original_7:
jmp dword ptr [0x72919c]
.global _log_8
_log_8:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 8
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+28]
push dword ptr [ebp+24]
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_8
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 24
original_8:
jmp dword ptr [0x7291a8]
.global _log_9
_log_9:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 9
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_9
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_9:
jmp dword ptr [0x7293e4]
.global _log_10
_log_10:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 10
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_10
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_10:
jmp dword ptr [0x7293dc]
.global _log_11
_log_11:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 11
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+24]
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_11
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 20
original_11:
jmp dword ptr [0x729444]
.global _log_12
_log_12:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 12
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+24]
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_12
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 20
original_12:
jmp dword ptr [0x729428]
.global _log_13
_log_13:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 13
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_13
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 12
original_13:
.byte 0x55,0x8b,0xec,0x83,0xec,0x40
jmp _resume_13
.global _log_14
_log_14:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 14
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_14
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 16
original_14:
.byte 0x55,0x8b,0xec,0x83,0xec,0x34
jmp _resume_14
.global _log_15
_log_15:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 15
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_15
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_15:
jmp dword ptr [0x7293e0]
.global _log_16
_log_16:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 16
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_16
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_16:
jmp dword ptr [0x729454]
.global _log_17
_log_17:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 17
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_17
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_17:
.byte 0xd9,0x44,0x24,0x4,0x56
jmp _resume_17
.global _log_18
_log_18:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 18
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_18
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_18:
.byte 0x55,0x8b,0xec,0x83,0xec,0x3c
jmp _resume_18
.global _log_19
_log_19:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 19
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
call original_19
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 0
original_19:
.byte 0x55,0x8b,0xec,0x51,0x51
jmp _resume_19
.global _log_20
_log_20:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 20
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_20
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_20:
.byte 0xa1,0x44,0xcf,0x7a,0x0
jmp _resume_20
.global _log_21
_log_21:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 21
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_21
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_21:
.byte 0xd9,0x44,0x24,0x4,0x56
jmp _resume_21
.global _log_22
_log_22:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 22
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_22
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_22:
.byte 0xd9,0x44,0x24,0x4,0x56
jmp _resume_22
.global _log_23
_log_23:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 23
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_23
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_23:
.byte 0x55,0x8b,0xec,0x81,0xec,0xb0,0x0,0x0,0x0
jmp _resume_23
.global _log_24
_log_24:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 24
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_24
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_24:
.byte 0x55,0x8b,0xec,0x83,0xec,0x14
jmp _resume_24
.global _log_25
_log_25:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 25
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_25
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_25:
.byte 0x55,0x8b,0xec,0x51,0x51
jmp _resume_25
.global _log_26
_log_26:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 26
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
call original_26
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 0
original_26:
.byte 0x55,0x8b,0xec,0x51,0x56
jmp _resume_26
.global _log_27
_log_27:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 27
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_27
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_27:
.byte 0x55,0x8b,0xec,0x51,0x56
jmp _resume_27
.global _log_28
_log_28:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 28
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
call original_28
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 0
original_28:
.byte 0x56,0x8b,0xf1,0xdd,0x86,0xd8,0x1,0x0,0x0
jmp _resume_28
.global _log_29
_log_29:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 29
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
call original_29
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 0
original_29:
.byte 0x55,0x8b,0xec,0x83,0xec,0x18
jmp _resume_29
.global _log_30
_log_30:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 30
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
call original_30
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 0
original_30:
.byte 0x55,0x8b,0xec,0x83,0xec,0x3c
jmp _resume_30
.global _log_31
_log_31:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 31
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_31
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_31:
.byte 0x55,0x8b,0xec,0x83,0xec,0x24
jmp _resume_31
.global _log_32
_log_32:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 32
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+24]
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_32
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 0
original_32:
.byte 0x55,0x8b,0xec,0x51,0x51
jmp _resume_32
.global _log_33
_log_33:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 33
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_33
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_33:
.byte 0x8b,0x44,0x24,0x8,0xd9,0xee
jmp _resume_33
.global _log_34
_log_34:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 34
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_34
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_34:
.byte 0x55,0x8b,0xec,0x51,0xd9,0x45,0xc
jmp _resume_34
.global _log_35
_log_35:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 35
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_35
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 12
original_35:
.byte 0x55,0x8b,0xec,0x83,0xec,0x24
jmp _resume_35
.global _log_36
_log_36:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 36
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_36
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 16
original_36:
.byte 0x55,0x8b,0xec,0x53,0x56
jmp _resume_36
.global _log_37
_log_37:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 37
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_37
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_37:
.byte 0x80,0xb9,0xc9,0x0,0x0,0x0,0x0
jmp _resume_37
.global _log_38
_log_38:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 38
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_38
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_38:
.byte 0x53,0x56,0x57,0x8b,0xf9
jmp _resume_38
.global _log_39
_log_39:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 39
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+24]
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_39
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 20
original_39:
.byte 0x55,0x8b,0xec,0x83,0xec,0x18
jmp _resume_39
.global _log_40
_log_40:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 40
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_40
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_40:
.byte 0x80,0xb9,0xc8,0x0,0x0,0x0,0x0
jmp _resume_40
.global _log_41
_log_41:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 41
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_41
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_41:
.byte 0x55,0x8b,0xec,0x8b,0x45,0x8
jmp _resume_41
.global _log_42
_log_42:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 42
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+32]
push dword ptr [ebp+28]
push dword ptr [ebp+24]
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_42
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 28
original_42:
.byte 0x55,0x8b,0xec,0xdb,0x45,0xc
jmp _resume_42
.global _log_43
_log_43:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 43
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_43
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 8
original_43:
.byte 0x55,0x8b,0xec,0x83,0xec,0x20
jmp _resume_43
.global _log_44
_log_44:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 44
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_44
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 12
original_44:
.byte 0x55,0x8b,0xec,0x51,0x51
jmp _resume_44
.global _log_45
_log_45:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 45
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_45
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 12
original_45:
.byte 0x56,0x57,0x8b,0xf1,0x8d,0xbe,0x88,0xc,0x0,0x0
jmp _resume_45
.global _log_46
_log_46:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 46
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_46
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_46:
.byte 0x55,0x8b,0xec,0x81,0xec,0x9c,0x0,0x0,0x0
jmp _resume_46
.global _log_47
_log_47:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 47
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+20]
push dword ptr [ebp+16]
push dword ptr [ebp+12]
push dword ptr [ebp+8]
call original_47
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 16
original_47:
.byte 0x55,0x8b,0xec,0x81,0xec,0xf8,0x0,0x0,0x0
jmp _resume_47
.global _log_48
_log_48:
push ebp
mov ebp,esp
sub esp,4
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
push dword ptr [ebp+4]
push 48
call "_enter_log@20"
mov [ebp-4],eax
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
push dword ptr [ebp+8]
call original_48
pushfd
pushad
mov ebx,esp
sub esp,528
and esp,-16
fxsave [esp]
mov edi,dword ptr fs:[0x34]
push 0x11223344
push dword ptr [ebp-4]
call "_exit_log@8"
mov dword ptr fs:[0x34],edi
fxrstor [esp]
mov esp,ebx
popad
popfd
mov esp,ebp
pop ebp
ret 4
original_48:
.byte 0x53,0x55,0x56,0x57,0x8b,0xf1
jmp _resume_48
