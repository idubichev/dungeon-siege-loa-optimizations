.text
.globl _quat_sse
_quat_sse:
    subl $12, %esp
    fnstcw (%esp)
    movzwl (%esp), %eax
    movl %eax, %edx
    andl $0x300, %edx
    jnz fallback
    # Match the x87 rounding mode; retain the caller's MXCSR for restoration.
    stmxcsr 4(%esp)
    shll $3, %eax
    andl $0x6000, %eax
    movl 4(%esp), %edx
    andl $0xffff1fbf, %edx
    orl %eax, %edx
    movl %edx, 8(%esp)
    ldmxcsr 8(%esp)
    movl $0x3f800000, (%esp)
    movl 20(%esp), %eax
    movl 16(%esp), %edx
    movss 12(%ecx), %xmm4
    addss %xmm4, %xmm4
    movaps %xmm4, %xmm5
    mulss 12(%ecx), %xmm5
    subss (%esp), %xmm5
    movss 8(%eax), %xmm6
    mulss 8(%ecx), %xmm6
    movss 4(%eax), %xmm0
    mulss 4(%ecx), %xmm0
    addss %xmm0, %xmm6
    movss (%eax), %xmm0
    mulss (%ecx), %xmm0
    addss %xmm0, %xmm6
    addss %xmm6, %xmm6

    movss 8(%eax), %xmm0
    mulss 4(%ecx), %xmm0
    movss 4(%eax), %xmm1
    mulss 8(%ecx), %xmm1
    subss %xmm1, %xmm0
    mulss %xmm4, %xmm0
    movaps %xmm5, %xmm1
    mulss (%eax), %xmm1
    addss %xmm1, %xmm0
    movaps %xmm6, %xmm1
    mulss (%ecx), %xmm1
    addss %xmm1, %xmm0
    movss %xmm0, (%edx)

    movss (%eax), %xmm0
    mulss 8(%ecx), %xmm0
    movss 8(%eax), %xmm1
    mulss (%ecx), %xmm1
    subss %xmm1, %xmm0
    mulss %xmm4, %xmm0
    movaps %xmm5, %xmm1
    mulss 4(%eax), %xmm1
    addss %xmm1, %xmm0
    movaps %xmm6, %xmm1
    mulss 4(%ecx), %xmm1
    addss %xmm1, %xmm0
    movss %xmm0, 4(%edx)

    movss 4(%eax), %xmm0
    mulss (%ecx), %xmm0
    movss (%eax), %xmm1
    mulss 4(%ecx), %xmm1
    subss %xmm1, %xmm0
    mulss %xmm4, %xmm0
    movaps %xmm5, %xmm1
    mulss 8(%eax), %xmm1
    addss %xmm1, %xmm0
    movaps %xmm6, %xmm1
    mulss 8(%ecx), %xmm1
    addss %xmm1, %xmm0
    movss %xmm0, 8(%edx)
    ldmxcsr 4(%esp)
    addl $12, %esp
    retl $8
fallback:
    addl $12, %esp
    flds 12(%ecx)
    movl 8(%esp), %eax
    .byte 0xe9
    .long 0x11223344 # Filled with a relative branch to the original function + 7.
