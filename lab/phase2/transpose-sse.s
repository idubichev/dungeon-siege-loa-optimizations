.text
.globl _transpose_sse
_transpose_sse:
 pushl %edx
 subl $4,%esp
 fnstcw (%esp)
 movzwl (%esp),%edx
 andl $63,%edx
 cmpl $63,%edx
 jne fallback
 leal 64(%ecx),%edx
 cmpl %edx,%eax
 jae separate
 leal 64(%eax),%edx
 cmpl %edx,%ecx
 jb fallback
separate:
 movdqu (%ecx),%xmm0
 movdqu 16(%ecx),%xmm1
 movdqu 32(%ecx),%xmm2
 movdqu 48(%ecx),%xmm3
 pcmpeqd %xmm7,%xmm7
 pslld $24,%xmm7
 psrld $1,%xmm7
 movdqa %xmm0,%xmm4
 pand %xmm7,%xmm4
 pcmpeqd %xmm7,%xmm4
 movdqa %xmm1,%xmm5
 pand %xmm7,%xmm5
 pcmpeqd %xmm7,%xmm5
 por %xmm5,%xmm4
 movdqa %xmm2,%xmm5
 pand %xmm7,%xmm5
 pcmpeqd %xmm7,%xmm5
 por %xmm5,%xmm4
 movdqa %xmm3,%xmm5
 pand %xmm7,%xmm5
 pcmpeqd %xmm7,%xmm5
 por %xmm5,%xmm4
 pmovmskb %xmm4,%edx
 testl %edx,%edx
 jne fallback
 movaps %xmm0,%xmm4
 unpcklps %xmm1,%xmm0
 unpckhps %xmm1,%xmm4
 movaps %xmm2,%xmm5
 unpcklps %xmm3,%xmm2
 unpckhps %xmm3,%xmm5
 movaps %xmm0,%xmm1
 movlhps %xmm2,%xmm0
 movhlps %xmm1,%xmm2
 movaps %xmm4,%xmm1
 movlhps %xmm5,%xmm4
 movhlps %xmm1,%xmm5
 movups %xmm0,(%eax)
 movups %xmm2,16(%eax)
 movups %xmm4,32(%eax)
 movups %xmm5,48(%eax)
 addl $4,%esp
 popl %edx
 retl
fallback:
 addl $4,%esp
 popl %edx
 pushl $0x22334455
 retl
