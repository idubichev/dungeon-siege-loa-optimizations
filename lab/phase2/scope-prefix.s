.text
.globl _scope_prefix
_scope_prefix:
 subl $8,%esp
 fnstcw (%esp)
 stmxcsr 4(%esp)
 movzwl (%esp),%eax
 shll $3,%eax
 andl $0x6000,%eax
 movl 4(%esp),%edx
 andl $0xffff1fbf,%edx
 orl %eax,%edx
 movl %edx,(%esp)
 ldmxcsr (%esp)
