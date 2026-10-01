typedef unsigned U;
static __attribute__((always_inline)) void norm(const float *a,float *out) {
 double x=a[0],y=a[1],z=a[2];double n=(x*x+y*y)+z*z;
 __asm__("sqrtsd %0,%0":"+x"(n));
 if(n!=0.0) {double inv=1.0/n;float xx=x*inv,yy=y*inv,zz=z*inv;out[0]=xx;out[1]=yy;out[2]=zz;}
}
static __attribute__((always_inline)) void cross(float *o,const float *a,const float *b) {
 o[0]=(double)b[2]*(double)a[1]-(double)b[1]*(double)a[2];
 o[1]=(double)b[0]*(double)a[2]-(double)b[2]*(double)a[0];
 o[2]=(double)b[1]*(double)a[0]-(double)b[0]*(double)a[1];
}
void __attribute__((thiscall)) ortho(const float *a,float *out) {
 unsigned short cw;U oldcsr,csr;
 __asm__ volatile("fnstcw %0":"=m"(cw));
 if((cw&0x300)!=0x200 || (cw&63)!=63) {((void (__attribute__((thiscall)) *)(const float*,float*))0x22334455)(a,out);return;}
 __asm__ volatile("stmxcsr %0":"=m"(oldcsr));csr=(oldcsr&0xffff1fbfu)|((cw<<3)&0x6000);__asm__ volatile("ldmxcsr %0"::"m"(csr));
 norm(a,out);cross(out+6,out,a+3);norm(out+6,out+6);cross(out+3,out+6,out);norm(out+3,out+3);
 __asm__ volatile("ldmxcsr %0"::"m"(oldcsr));
}
