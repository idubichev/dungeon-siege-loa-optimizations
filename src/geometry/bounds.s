.intel_syntax noprefix
.text
.global _bounds
_bounds:
lea edx,[ecx-8]
movss xmm0,[ecx-8]
ucomiss xmm0,[ebp-0x2c]
jbe less0
jp next0
movss [ebp-0x2c],xmm0
jmp next0
less0:
ucomiss xmm0,[ebp-0x30]
jae next0
jp next0
movss [ebp-0x30],xmm0
next0:
movss xmm0,[ecx-4]
ucomiss xmm0,[ebp-0x40]
jbe less1
jp next1
movss [ebp-0x40],xmm0
jmp next1
less1:
ucomiss xmm0,[ebp-0x34]
jae next1
jp next1
movss [ebp-0x34],xmm0
next1:
movss xmm0,[ecx]
ucomiss xmm0,[ebp-0x3c]
jbe less2
jp next2
movss [ebp-0x3c],xmm0
jmp next2
less2:
ucomiss xmm0,[ebp-0x38]
jae next2
jp next2
movss [ebp-0x38],xmm0
next2:
ret
