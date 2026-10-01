from pathlib import Path
import struct,subprocess,json,capstone
p=Path(__file__).parent
exec((p/'build-frustum.py').read_text().split('threshold=')[0])
base=0x41acde;code=read(base,0x116);(p/'qmatrix-original.bin').write_bytes(code);cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True;rel=[]
for ins in cs.disasm(code,base):
 for x in ins.operands:
  if x.type==capstone.x86.X86_OP_MEM and x.mem.disp in [0x72a6d8,0x72a6f4,0x72a6f0]:
   name=hex(x.mem.disp);(p/(name+'.bin')).write_bytes(read(x.mem.disp,4));rel.append({'offset':ins.address-base+ins.disp_offset,'target':name})
  if x.type==capstone.x86.X86_OP_IMM and x.imm==0x7ac39c:rel.append({'offset':ins.address-base+ins.imm_offset,'target':'identity'})
(p/'identity.bin').write_bytes(struct.pack('<9f',1,0,0,0,1,0,0,0,1));(p/'qmatrix-original-relocations.json').write_text(json.dumps(rel,indent=2))
s='''typedef unsigned U;
typedef struct { U mode,valid,key[4],output[9]; } Entry;
typedef struct { volatile U lock; U hits,misses,reserved; Entry entries[8192]; } Store;
typedef void * (__attribute__((thiscall)) *Original)(const U*,U*);
void * __attribute__((thiscall)) qmatrix_cache(const U *a,U *out) {
 Store *store=(Store*)0x11223344;Original original=(Original)0x22334455;
 unsigned short cw;__asm__ volatile("fnstcw %0":"=m"(cw));
 if((cw&63)!=63 || (U)out-(U)a<16 || (U)a-(U)out<36)return original(a,out);
 U key[4],hash=2166136261u,small=1;
 for(U i=0;i<4;i++) {key[i]=a[i];U v=key[i]&0x7fffffffu;if(v>=0x7f800000u)return original(a,out);if(v>=0x3c800000u)small=0;hash=(hash^key[i])*16777619u;}
 if(small)return original(a,out);
 hash^=cw;hash^=hash>>16;hash*=0x85ebca6bu;hash^=hash>>13;hash*=0xc2b2ae35u;hash^=hash>>16;
 if(!__sync_bool_compare_and_swap(&store->lock,0,1))return original(a,out);
 Entry *e=&store->entries[hash&8191];
 if(e->valid && e->mode==cw && e->key[0]==key[0] && e->key[1]==key[1] && e->key[2]==key[2] && e->key[3]==key[3]) {
  for(U i=0;i<9;i++)out[i]=e->output[i];store->hits++;__sync_lock_release(&store->lock);return out;
 }
 e->valid=0;e->mode=cw;for(U i=0;i<4;i++)e->key[i]=key[i];
 void *result=original(a,out);for(U i=0;i<9;i++)e->output[i]=out[i];e->valid=1;store->misses++;__sync_lock_release(&store->lock);return result;
}
'''
(p/'qmatrix-cache.c').write_text(s)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-sse','-mno-mmx','-fno-vectorize','-fno-slp-vectorize','-c',str(p/'qmatrix-cache.c'),'-o',str(p/'qmatrix-cache.obj')],check=True)
b=(p/'qmatrix-cache.obj').read_bytes();size,off=struct.unpack_from('<II',b,36);assert struct.unpack_from('<H',b,52)[0]==0;(p/'qmatrix-cache.bin').write_bytes(b[off:off+size]);print('Bytes',size)
