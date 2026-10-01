.text
.globl _quat_sse
_quat_sse:
    subl $12, %esp
    fnstcw (%esp)
    movzwl (%esp), %eax
    movl %eax, %edx
    andl $0x300, %edx
    jz supported
    cmpl $0x200, %edx
    jne fallback
supported:
    # Match the x87 rounding mode; retain the caller's MXCSR for restoration.
    stmxcsr 4(%esp)
    shll $3, %eax
    andl $0x6000, %eax
    movl 4(%esp), %edx
    andl $0xffff1fbf, %edx
    orl %eax, %edx
    movl %edx, 8(%esp)
    ldmxcsr 8(%esp)
    movzwl (%esp), %eax
    andl $0x300, %eax
    cmpl $0x200, %eax
    je double_precision
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
    jmp finish
double_precision:
    movl $0x3f800000, (%esp)
    movl 20(%esp), %eax
    movl 16(%esp), %edx
    cvtss2sd 12(%ecx), %xmm4
    addsd %xmm4, %xmm4
    movaps %xmm4, %xmm5
    cvtss2sd 12(%ecx), %xmm7
    mulsd %xmm7, %xmm5
    cvtss2sd (%esp), %xmm7
    subsd %xmm7, %xmm5
    cvtss2sd 8(%eax), %xmm6
    cvtss2sd 8(%ecx), %xmm7
    mulsd %xmm7, %xmm6
    cvtss2sd 4(%eax), %xmm0
    cvtss2sd 4(%ecx), %xmm7
    mulsd %xmm7, %xmm0
    addsd %xmm0, %xmm6
    cvtss2sd (%eax), %xmm0
    cvtss2sd (%ecx), %xmm7
    mulsd %xmm7, %xmm0
    addsd %xmm0, %xmm6
    addsd %xmm6, %xmm6

    cvtss2sd 8(%eax), %xmm0
    cvtss2sd 4(%ecx), %xmm7
    mulsd %xmm7, %xmm0
    cvtss2sd 4(%eax), %xmm1
    cvtss2sd 8(%ecx), %xmm7
    mulsd %xmm7, %xmm1
    subsd %xmm1, %xmm0
    mulsd %xmm4, %xmm0
    movaps %xmm5, %xmm1
    cvtss2sd (%eax), %xmm7
    mulsd %xmm7, %xmm1
    addsd %xmm1, %xmm0
    movaps %xmm6, %xmm1
    cvtss2sd (%ecx), %xmm7
    mulsd %xmm7, %xmm1
    addsd %xmm1, %xmm0
    cvtsd2ss %xmm0, %xmm7
    movss %xmm7, (%edx)

    cvtss2sd (%eax), %xmm0
    cvtss2sd 8(%ecx), %xmm7
    mulsd %xmm7, %xmm0
    cvtss2sd 8(%eax), %xmm1
    cvtss2sd (%ecx), %xmm7
    mulsd %xmm7, %xmm1
    subsd %xmm1, %xmm0
    mulsd %xmm4, %xmm0
    movaps %xmm5, %xmm1
    cvtss2sd 4(%eax), %xmm7
    mulsd %xmm7, %xmm1
    addsd %xmm1, %xmm0
    movaps %xmm6, %xmm1
    cvtss2sd 4(%ecx), %xmm7
    mulsd %xmm7, %xmm1
    addsd %xmm1, %xmm0
    cvtsd2ss %xmm0, %xmm7
    movss %xmm7, 4(%edx)

    cvtss2sd 4(%eax), %xmm0
    cvtss2sd (%ecx), %xmm7
    mulsd %xmm7, %xmm0
    cvtss2sd (%eax), %xmm1
    cvtss2sd 4(%ecx), %xmm7
    mulsd %xmm7, %xmm1
    subsd %xmm1, %xmm0
    mulsd %xmm4, %xmm0
    movaps %xmm5, %xmm1
    cvtss2sd 8(%eax), %xmm7
    mulsd %xmm7, %xmm1
    addsd %xmm1, %xmm0
    movaps %xmm6, %xmm1
    cvtss2sd 8(%ecx), %xmm7
    mulsd %xmm7, %xmm1
    addsd %xmm1, %xmm0
    cvtsd2ss %xmm0, %xmm7
    movss %xmm7, 8(%edx)
finish:
    ldmxcsr 4(%esp)
    addl $12, %esp
    retl $8
fallback:
    addl $12, %esp
    flds 12(%ecx)
    movl 8(%esp), %eax
    .byte 0xe9
    .long 0x11223344 # Filled with a relative branch to the original function + 7.
