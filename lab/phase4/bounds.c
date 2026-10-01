/* Exact ordering of binary32 values without x87 helpers or FP mode changes.
 * NaNs remain unordered and signed zero compares equal, as in FCOMP. */
typedef unsigned int u32;
static int less(u32 a,u32 b) {
    u32 am=a&0x7fffffff,bm=b&0x7fffffff;
    if (am>0x7f800000 || bm>0x7f800000 || !(am|bm)) return 0;
    if ((a^b)&0x80000000) return (int)a<0;
    return a&0x80000000 ? a>b : a<b;
}
static void axis(u32 v,u32 *low,u32 *high) {
    if (less(*high,v)) *high=v;
    else if (less(v,*low)) *low=v;
}
void __attribute__((stdcall)) update_bounds(char *frame,const u32 *vertex) {
    axis(vertex[0],(u32*)(frame-0x30),(u32*)(frame-0x2c));
    axis(vertex[1],(u32*)(frame-0x34),(u32*)(frame-0x40));
    axis(vertex[2],(u32*)(frame-0x38),(u32*)(frame-0x3c));
}
