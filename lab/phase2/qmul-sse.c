typedef unsigned U;
void * __attribute__((thiscall)) qmul(const float *a,float *out,const float *b) {
 unsigned short cw;U oldcsr,csr;
 __asm__ volatile("fnstcw %0":"=m"(cw));
 if((cw&0x300)!=0x200 || (cw&63)!=63)return ((void * (__attribute__((thiscall)) *)(const float*,float*,const float*))0x22334455)(a,out,b);
 __asm__ volatile("stmxcsr %0":"=m"(oldcsr));
 csr=(oldcsr&0xffff1fbfu)|((cw<<3)&0x6000);
 __asm__ volatile("ldmxcsr %0"::"m"(csr));
 double x=a[0],y=a[1],z=a[2],w=a[3],X=b[0],Y=b[1],Z=b[2],W=b[3];
 float rw=((w*W-X*x)-y*Y)-z*Z;
 float rx=((w*X+x*W)+y*Z)-z*Y;
 float ry=((Y*w+y*W)+z*X)-Z*x;
 float rz=((Z*w+z*W)+Y*x)-y*X;
 out[0]=rx;out[1]=ry;out[2]=rz;out[3]=rw;
 __asm__ volatile("ldmxcsr %0"::"m"(oldcsr));return out;
}
