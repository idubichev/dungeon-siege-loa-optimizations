.intel_syntax noprefix
.text
.global _frame_entry
_frame_entry:
pushfd
pushad
push dword ptr [0x7290a0]
push dword ptr [0x729088]
push 0x11223344
call "_frame_tick@12"
popad
popfd
.byte 0x55,0x8b,0xec,0x81,0xec,0xa0,0x0,0x0,0x0
jmp _resume
