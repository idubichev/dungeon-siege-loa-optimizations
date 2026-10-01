from pathlib import Path
import struct,json,hashlib,subprocess
import capstone
p=Path(__file__).parent;out=p/'08-matrix-skin';out.mkdir(exist_ok=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-O2','-msse2','-mfpmath=sse','-ffreestanding','-fno-builtin','-fno-stack-protector','-ffp-contract=off','-frounding-math','-fno-vectorize','-fno-slp-vectorize','-c',str(p/'matrix-skin.c'),'-o',str(out/'skin-loop.obj')],check=True)
s=(p.parent/'phase2/build-skin-loop.py').read_text().replace('p=Path(__file__).parent;','p=Path(__file__).parent/"08-matrix-skin";')
exec(s,{"__file__":__file__})
s=(p.parent/'phase2/build-static-patches.py').read_text();scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
pe=scope['PE'](p/'04-cursor-colors/DSLOA.exe');pe.packed=False
body=bytearray((out/'skin-loop.bin').read_bytes());pos,addr=pe.reserve(64+len(body))
for r in json.loads((out/'skin-loop-relocations.json').read_text()):
 assert r['kind']=='absolute';value=(addr+64 if r['target']=='code' else 0x69fa05)+r['value'];struct.pack_into('<I',body,r['offset'],value);pe.absolute(pos+64+r['offset'])
d=bytearray.fromhex('60575355e80000000083c40c85c0610f84000000008b7df88b75e46bf60ce900000000')
struct.pack_into('<i',d,5,64-9);struct.pack_into('<i',d,17,0x69f2f1-(addr+21));struct.pack_into('<i',d,31,0x69f3a6-(addr+35))
pe.put(pos,d+b'\x90'*(64-len(d))+body);pe.hook(0x69f24a,bytes.fromhex('e9a2000000'),addr,'matrix-skin-batch')
m=pe.finish(out/'DSLOA.exe');(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
original=bytearray(pe.read(0x69f24f,0x69f2fa-0x69f24f));rel=[]
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
for i in cs.disasm(original,0x69f24f):
 if i.mnemonic=='call':rel.append({'offset':i.address-0x69f24f+i.imm_offset,'next':i.address-0x69f24f+i.size,'target':hex(i.operands[0].imm)})
(out/'original.bin').write_bytes(original+b'\xc3');(out/'original-relocations.json').write_text(json.dumps(rel,indent=2)+'\n');print(json.dumps(m,indent=2))
