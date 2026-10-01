.text
.globl _blend_sse
_blend_sse:
    pushl %ecx
    pushl %edx
    subl $12, %esp
    fnstcw (%esp)
    movzwl (%esp), %eax
    andl $0x300, %eax
    jz supported
    cmpl $0x200, %eax
    jne fallback
supported:
    stmxcsr 4(%esp)
    movzwl (%esp), %edx
    shll $3, %edx
    andl $0x6000, %edx
    movl 4(%esp), %ecx
    andl $0xffff1fbf, %ecx
    orl %edx, %ecx
    movl %ecx, 8(%esp)
    ldmxcsr 8(%esp)
    cmpl $0x200, %eax
    je double_precision
    movss -80(%ebp), %xmm0
    addss -104(%ebp), %xmm0
    movss -76(%ebp), %xmm1
    addss -100(%ebp), %xmm1
    movss -72(%ebp), %xmm2
    addss -96(%ebp), %xmm2
    movss %xmm2, -72(%ebp)
    mulss -88(%ebp), %xmm0
    movss %xmm0, -80(%ebp)
    mulss -88(%ebp), %xmm1
    movss %xmm1, -76(%ebp)
    mulss -88(%ebp), %xmm2
    movss %xmm2, -72(%ebp)
    movl -36(%ebp), %eax
    addl %esi, %eax
    movss -80(%ebp), %xmm0
    addss (%eax), %xmm0
    movss %xmm0, (%eax)
    movss -76(%ebp), %xmm0
    addss 4(%eax), %xmm0
    movss %xmm0, 4(%eax)
    movss -72(%ebp), %xmm0
    addss 8(%eax), %xmm0
    movss %xmm0, 8(%eax)
    jmp done
double_precision:
    cvtss2sd -80(%ebp), %xmm0
    cvtss2sd -104(%ebp), %xmm3
    addsd %xmm3, %xmm0
    cvtss2sd -76(%ebp), %xmm1
    cvtss2sd -100(%ebp), %xmm3
    addsd %xmm3, %xmm1
    cvtss2sd -72(%ebp), %xmm2
    cvtss2sd -96(%ebp), %xmm3
    addsd %xmm3, %xmm2
    cvtsd2ss %xmm2, %xmm2
    movss %xmm2, -72(%ebp)
    cvtss2sd -88(%ebp), %xmm3
    mulsd %xmm3, %xmm0
    cvtsd2ss %xmm0, %xmm0
    movss %xmm0, -80(%ebp)
    mulsd %xmm3, %xmm1
    cvtsd2ss %xmm1, %xmm1
    movss %xmm1, -76(%ebp)
    cvtss2sd -72(%ebp), %xmm2
    mulsd %xmm3, %xmm2
    cvtsd2ss %xmm2, %xmm2
    movss %xmm2, -72(%ebp)
    movl -36(%ebp), %eax
    addl %esi, %eax
    cvtss2sd -80(%ebp), %xmm0
    cvtss2sd (%eax), %xmm3
    addsd %xmm3, %xmm0
    cvtsd2ss %xmm0, %xmm0
    movss %xmm0, (%eax)
    cvtss2sd -76(%ebp), %xmm0
    cvtss2sd 4(%eax), %xmm3
    addsd %xmm3, %xmm0
    cvtsd2ss %xmm0, %xmm0
    movss %xmm0, 4(%eax)
    cvtss2sd -72(%ebp), %xmm0
    cvtss2sd 8(%eax), %xmm3
    addsd %xmm3, %xmm0
    cvtsd2ss %xmm0, %xmm0
    movss %xmm0, 8(%eax)
done:
    ldmxcsr 4(%esp)
    addl $12, %esp
    popl %edx
    popl %ecx
    retl
fallback:
    addl $12, %esp
    popl %edx
    popl %ecx
    pushl $0x22334455
    retl
