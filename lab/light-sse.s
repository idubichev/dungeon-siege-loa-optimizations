.text
.globl _light_sse
# EBP is the original lighting frame; EDI points to normal.y.
# Return EDX=0 to skip the vertex, or EDX=1 and EAX=original intensity.
_light_sse:
    subl $12, %esp
    fnstcw (%esp)
    movzwl (%esp), %eax
    movl %eax, %edx
    andl $0x300, %edx
    jz supported
    cmpl $0x200, %edx
    jne fallback
supported:
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
    movss -36(%ebp), %xmm0
    mulss -4(%edi), %xmm0
    movss -28(%ebp), %xmm1
    mulss 4(%edi), %xmm1
    addss %xmm1, %xmm0
    movss -32(%ebp), %xmm1
    mulss (%edi), %xmm1
    addss %xmm1, %xmm0
    xorps %xmm1, %xmm1
    ucomiss %xmm1, %xmm0
    jbe skip
    mulss -12(%ebp), %xmm0
    movl $0x3f800000, (%esp)
    minss (%esp), %xmm0
    movl $0x437f0000, (%esp)
    mulss (%esp), %xmm0
    movss %xmm0, -40(%ebp)
    cvtss2si %xmm0, %eax
    movl %eax, -64(%ebp)
    movl $1, %edx
    jmp done
double_precision:
    cvtss2sd -36(%ebp), %xmm0
    cvtss2sd -4(%edi), %xmm2
    mulsd %xmm2, %xmm0
    cvtss2sd -28(%ebp), %xmm1
    cvtss2sd 4(%edi), %xmm2
    mulsd %xmm2, %xmm1
    addsd %xmm1, %xmm0
    cvtss2sd -32(%ebp), %xmm1
    cvtss2sd (%edi), %xmm2
    mulsd %xmm2, %xmm1
    addsd %xmm1, %xmm0
    xorps %xmm1, %xmm1
    ucomisd %xmm1, %xmm0
    jbe skip
    cvtss2sd -12(%ebp), %xmm2
    mulsd %xmm2, %xmm0
    movl $0x3f800000, (%esp)
    cvtss2sd (%esp), %xmm2
    minsd %xmm2, %xmm0
    movl $0x437f0000, (%esp)
    cvtss2sd (%esp), %xmm2
    mulsd %xmm2, %xmm0
    cvtsd2ss %xmm0, %xmm0
    movss %xmm0, -40(%ebp)
    cvtss2si %xmm0, %eax
    movl %eax, -64(%ebp)
    movl $1, %edx
    jmp done
skip:
    xorl %eax, %eax
    xorl %edx, %edx
done:
    ldmxcsr 4(%esp)
    addl $12, %esp
    retl
fallback:
    addl $12, %esp
    movl $0x22334455, %edx
    jmpl *%edx
