from pathlib import Path
import struct,subprocess
p=Path(__file__).parent
exec((p/'build-frustum.py').read_text().split('threshold=')[0])
(p/'qmul-original.bin').write_bytes(read(0x5361ef,0x99))
s='''typedef unsigned U;
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
'''
(p/'qmul-sse.c').write_text(s)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-O2','-msse2','-mfpmath=sse','-ffreestanding','-fno-builtin','-fno-stack-protector','-ffp-contract=off','-frounding-math','-fno-vectorize','-fno-slp-vectorize','-c',str(p/'qmul-sse.c'),'-o',str(p/'qmul-sse.obj')],check=True)
b=(p/'qmul-sse.obj').read_bytes();size,off=struct.unpack_from('<II',b,36);assert struct.unpack_from('<H',b,52)[0]==0;(p/'qmul-sse.bin').write_bytes(b[off:off+size]);print(size)
