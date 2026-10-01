from pathlib import Path
import struct,json,capstone
p=Path(__file__).parent;b=(p/'slerp-last-cache.obj').read_bytes();ns=struct.unpack_from('<H',b,2)[0];syms=struct.unpack_from('<I',b,8)[0];sections=[]
for i in range(ns):
 o=20+40*i;sz,rp,relp=struct.unpack_from('<III',b,o+16);nr=struct.unpack_from('<H',b,o+32)[0];sections.append((b[o:o+8].rstrip(b'\0'),sz,rp,relp,nr))
code=bytearray(b[sections[0][2]:sections[0][2]+sections[0][1]]);offsets={1:0};rel=[]
for i in range(sections[0][4]):
 r,idx,typ=struct.unpack_from('<IIH',b,sections[0][3]+10*i);so=syms+idx*18;value,sec=struct.unpack_from('<Ih',b,so+8);assert typ in [6,20]
 if sec not in offsets:
  target=sections[sec-1];off=(len(code)+15)//16*16;code.extend(b'\0'*(off-len(code)));code.extend(b[target[2]:target[2]+target[1]]);offsets[sec]=off
 add=struct.unpack_from('<I',code,r)[0];rel.append({'offset':r,'kind':'absolute' if typ==6 else 'relative','target':'code','value':offsets[sec]+value+add})
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
for ins in cs.disasm(code[:sections[0][1]],0):
 for x in ins.operands:
  v=x.imm if x.type==capstone.x86.X86_OP_IMM else x.mem.disp if x.type==capstone.x86.X86_OP_MEM else 0
  if 0x11223344<=v<0x11224344 or v==0x22334455:
   offset=ins.address+(ins.imm_offset if x.type==capstone.x86.X86_OP_IMM else ins.disp_offset)
   rel.append({'offset':offset,'target':'data' if v!=0x22334455 else 'original','addend':v-(0x11223344 if v!=0x22334455 else 0x22334455)})
for r in rel:
 if r.get('target')=='code':r['addend']=r.pop('value');r.pop('kind')
q=p/'last-payload';q.mkdir(exist_ok=True);(q/'slerp-cache.bin').write_bytes(code);(q/'slerp-cache-relocations.json').write_text(json.dumps(rel,indent=2));(q/'slerp-original.bin').write_bytes((p.parent/'slerp-original.bin').read_bytes());print(len(code),len(rel))
