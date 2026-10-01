.intel_syntax noprefix
.text
fld dword ptr [ecx]
fmul st(0),st(0)
fld dword ptr [ecx+4]
fmul st(0),st(0)
faddp st(1),st(0)
fld dword ptr [ecx+8]
fmul st(0),st(0)
faddp st(1),st(0)
ret
