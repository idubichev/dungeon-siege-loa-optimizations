typedef unsigned U;
#define F(off) (*(float*)(frame+(off)))
#define I(off) (*(U*)(frame+(off)))
typedef void (*Color)(U*,const U*,U);
static __attribute__((always_inline)) int overlap(U a,U na,U b,U nb){return a<b+nb && b<a+na;}
U light_loop(char *frame,float *normal,U count) {
 unsigned short cw;__asm__ volatile("fnstcw %0":"=m"(cw));if((cw&0x300)!=0x200 || (cw&63)!=63 || !count || count>1048576)return 0;
 U colors=I(-4),light=I(8)+4,ns=count*12,cs=count*24;
 if(colors+cs<colors || (U)normal+ns<(U)normal || overlap(colors,cs,(U)normal-4,ns) || overlap(colors,cs,(U)frame-128,160) || overlap(colors,cs,light,4))return 0;
 U old,csr;__asm__ volatile("stmxcsr %0":"=m"(old));csr=(old&0xffff1fbfu)|((cw<<3)&0x6000);__asm__ volatile("ldmxcsr %0"::"m"(csr));
 double dx=F(-36),dy=F(-32),dz=F(-28),scale=F(-12);
 for(U i=0;i<count;i++,normal+=3,colors+=24) {
  double dot=(dx*(double)normal[-1]+dz*(double)normal[1])+dy*(double)normal[0];
  if(dot>0.0) {
   double intensity=dot*scale;if(!(intensity<1.0))intensity=1.0;
   float value=intensity*255.0;int iv;__asm__("cvtss2si %1,%0":"=r"(iv):"x"(value));
   F(-40)=value;I(-64)=(U)iv;((Color)0x22334455)((U*)colors,(const U*)light,(U)iv);
  }
  I(-4)=colors+24;
 }
 __asm__ volatile("ldmxcsr %0"::"m"(old));return 1;
}
