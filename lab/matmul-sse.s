.text
.globl _matmul_sse
_matmul_sse:
    pushl %ebp
    movl %esp, %ebp
    subl $16, %esp
    pushl %ebx
    pushl %esi
    pushl %edi
    movl %eax, %edi
    movl %ecx, %esi
    fnstcw -4(%ebp)
    movzwl -4(%ebp), %edx
    andl $0x300, %edx
    cmpl $0x200, %edx
    jne fallback
    stmxcsr -8(%ebp)
    movzwl -4(%ebp), %edx
    shll $3, %edx
    andl $0x6000, %edx
    movl -8(%ebp), %eax
    andl $0xffff1fbf, %eax
    orl %edx, %eax
    movl %eax, -12(%ebp)
    ldmxcsr -12(%ebp)
    movl 8(%ebp), %eax
    movl $4, -16(%ebp)
outer:
    movl %edi, %edx
    movl %esi, %ecx
    movl $4, %ebx
inner:
    cvtss2sd (%eax), %xmm0
    cvtss2sd (%ecx), %xmm1
    mulsd %xmm1, %xmm0
    cvtss2sd 4(%ecx), %xmm1
    cvtss2sd 16(%eax), %xmm2
    mulsd %xmm2, %xmm1
    addsd %xmm1, %xmm0
    cvtss2sd 8(%ecx), %xmm1
    cvtss2sd 32(%eax), %xmm2
    mulsd %xmm2, %xmm1
    addsd %xmm1, %xmm0
    cvtss2sd 12(%ecx), %xmm1
    cvtss2sd 48(%eax), %xmm2
    mulsd %xmm2, %xmm1
    addsd %xmm1, %xmm0
    cvtsd2ss %xmm0, %xmm0
    movss %xmm0, (%edx)
    addl $16, %ecx
    addl $16, %edx
    decl %ebx
    jnz inner
    addl $4, %edi
    addl $4, %eax
    decl -16(%ebp)
    jnz outer
    addl $32, %eax
    ldmxcsr -8(%ebp)
    popl %edi
    popl %esi
    popl %ebx
    leave
    retl
fallback:
    movl %edi, %eax
    movl %esi, %ecx
    popl %edi
    popl %esi
    popl %ebx
    leave
    movl $0x22334455, %edx
    jmpl *%edx
