from pathlib import Path
import struct,subprocess,json,capstone
p=Path(__file__).parent;b=(p.parent/'DSLOA-sse.exe').read_bytes();pe=struct.unpack_from('<I',b,60)[0];op=struct.unpack_from('<H',b,pe+20)[0];sec=[]
for i in range(struct.unpack_from('<H',b,pe+6)[0]):
 o=pe+24+op+40*i;vs,va,sz,rp=struct.unpack_from('<4I',b,o+8);sec.append((va+0x400000,sz,rp))
def read(a,n):
 v,s,o=next(t for t in sec if t[0]<=a<t[0]+t[1]);return b[o+a-v:o+a-v+n]
threshold=read(0x72a5e8,4);(p/'frustum-threshold.bin').write_bytes(threshold);print('Threshold',struct.unpack('<f',threshold))
for name,a,end in [('frustum-original',0x684d7f,0x684f54),('vec-ctor',0x47d209,0x47d222),('vec-sub',0x49efe8,0x49f00d),('vec-dot',0x64af6e,0x64af89)]:
 code=read(a,end-a);(p/(name+'.bin')).write_bytes(code)
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True;rel=[]
for ins in cs.disasm(read(0x684d7f,0x1d5),0x684d7f):
 if ins.mnemonic=='call':
  rel.append({'offset':ins.address-0x684d7f+ins.imm_offset,'relative_to':ins.address-0x684d7f+ins.size,'target':{0x47d209:'vec-ctor',0x49efe8:'vec-sub',0x64af6e:'vec-dot'}[ins.operands[0].imm]})
 for x in ins.operands:
  if x.type==capstone.x86.X86_OP_MEM and x.mem.disp==0x72a5e8:rel.append({'offset':ins.address-0x684d7f+ins.disp_offset,'target':'threshold'})
(p/'frustum-original-relocations.json').write_text(json.dumps(rel,indent=2))
s='''/* Six exact culling-plane tests; keep original code for unsupported precision. */
typedef unsigned U;
U frustum_mask(const float *camera,const float *p,float threshold) {
 unsigned short cw;U oldcsr,csr,mask=0;
 __asm__ volatile("fnstcw %0":"=m"(cw));
 if((cw&0x300)!=0x200 || (cw&63)!=63)return ~0u;
 __asm__ volatile("stmxcsr %0":"=m"(oldcsr));
 csr=(oldcsr&0xffff1fbfu)|((cw<<3)&0x6000);
 __asm__ volatile("ldmxcsr %0"::"m"(csr));
'''
for i,(pos,normal,order,bit,rounded) in enumerate([(0x34,0x94,[0,2,1],8,False),(0x1c,0x7c,[0,2,1],4,True),(0x1c,0xac,[0,2,1],1,True),(0x4c,0xb8,[2,1,0],2,True),(0x40,0xa0,[2,1,0],16,True),(0x28,0x88,[2,1,0],32,True)]):
 s+=' {\n'
 for j,v in enumerate('xyz'):
  expr=f'((double)p[{j}]-(double)camera[{pos//4+j}])'
  if rounded:expr='(float)'+expr
  s+=f'  double {v}={expr};\n'
 terms=[f'{"xyz"[j]}*(double)camera[{normal//4+j}]' for j in order]
 s+=f'  double dot=({terms[0]}+{terms[1]})+{terms[2]};\n  if(dot>(double)threshold)mask|={bit};\n }}\n'
s+=' __asm__ volatile("ldmxcsr %0"::"m"(oldcsr));\n return mask;\n}\n';(p/'frustum-sse.c').write_text(s)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-O2','-msse2','-mfpmath=sse','-ffreestanding','-fno-builtin','-fno-stack-protector','-ffp-contract=off','-frounding-math','-fno-vectorize','-fno-slp-vectorize','-c',str(p/'frustum-sse.c'),'-o',str(p/'frustum-sse.obj')],check=True)
b=(p/'frustum-sse.obj').read_bytes();size,off=struct.unpack_from('<II',b,36);assert struct.unpack_from('<H',b,52)[0]==0;(p/'frustum-sse.bin').write_bytes(b[off:off+size]);print('Code bytes',size)
