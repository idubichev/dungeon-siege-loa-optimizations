.intel_syntax noprefix
.text
.global _bounds_0
_bounds_0:
pushfd
pushad
push edx
push ebp
call "_update_bounds@8"
popad
popfd
jmp _resume_0
.global _bounds_1
_bounds_1:
pushfd
pushad
push edx
push ebp
call "_update_bounds@8"
popad
popfd
jmp _resume_1
