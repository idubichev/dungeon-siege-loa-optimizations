from pathlib import Path
import struct,subprocess,json,capstone
p=Path(__file__).parent
exec((p/'build-frustum.py').read_text().split('threshold=')[0])
base=0x43e82d;code=read(base,0xf0);(p/'ortho-original.bin').write_bytes(code);cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True;rel=[]
for ins in cs.disasm(code,base):
 for x in ins.operands:
  if x.type==capstone.x86.X86_OP_MEM and x.mem.disp==0x72a5e8:rel.append(ins.address-base+ins.disp_offset)
(p/'ortho-original-relocations.json').write_text(json.dumps(rel))
s='''typedef unsigned U;
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
''';(p/'ortho-sse.c').write_text(s)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-O2','-msse2','-mfpmath=sse','-ffreestanding','-fno-builtin','-fno-stack-protector','-ffp-contract=off','-frounding-math','-fno-vectorize','-fno-slp-vectorize','-c',str(p/'ortho-sse.c'),'-o',str(p/'ortho-sse.obj')],check=True)
b=(p/'ortho-sse.obj').read_bytes();size,off=struct.unpack_from('<II',b,36)
# The compiler emits a local 1.0 literal; record COFF relocation for the .rdata section.
ns=struct.unpack_from('<H',b,2)[0];sections=[]
for i in range(ns):
 o=20+40*i;name=b[o:o+8].rstrip(b'\0').decode();sz,rp,relp=struct.unpack_from('<III',b,o+16);nr=struct.unpack_from('<H',b,o+32)[0];sections.append((name,sz,rp,relp,nr))
syms=struct.unpack_from('<I',b,8)[0];code=bytearray(b[off:off+size]);outrel=[]
for i in range(sections[0][4]):
 r,idx,typ=struct.unpack_from('<IIH',b,sections[0][3]+10*i);so=syms+idx*18;value,sec=struct.unpack_from('<Ih',b,so+8);assert typ==6
 target=sections[sec-1];literal=b[target[2]:target[2]+target[1]];literaloffset=(len(code)+15)//16*16;code.extend(b'\0'*(literaloffset-len(code)));code.extend(literal);addend=struct.unpack_from('<I',code,r)[0];outrel.append({'offset':r,'code_offset':literaloffset+value+addend})
(p/'ortho-sse.bin').write_bytes(code);(p/'ortho-sse-relocations.json').write_text(json.dumps(outrel));print('Bytes',len(code),'relocations',outrel)
