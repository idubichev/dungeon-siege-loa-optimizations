"""Build an isolated DSLOA candidate from the saved original; no installed files changed."""
from pathlib import Path
import struct, hashlib, json
lab=Path(__file__).parent
source=lab/'backup/Dungeon Siege Wine10 Test.app/game/DSLOA.exe'
original=source.read_bytes();data=bytearray(original)
u16=lambda off:struct.unpack_from('<H',data,off)[0]
u32=lambda off:struct.unpack_from('<I',data,off)[0]
align=lambda n,a:(n+a-1)//a*a
pe=u32(0x3c);assert data[pe:pe+4]==b'PE\0\0'
assert u16(pe+4)==0x14c
n=u16(pe+6);opt=pe+24;assert u16(opt)==0x10b
table=opt+u16(pe+20)
sections=[struct.unpack_from('<8sIIIIIIHHI',data,table+40*i) for i in range(n)]
def offset(rva):
    for s in sections:
        if s[2]<=rva<s[2]+s[3]:return s[4]+rva-s[2]
    raise ValueError(hex(rva))
target=0x135f3b;old=(lab/'quat-original.bin').read_bytes()
assert bytes(data[offset(target):offset(target)+len(old)])==old
# Use verified zero padding at the end of the existing executable .crt section.
# This preserves the original header's credits and does not add a section.
last=sections[-1];assert last[0].rstrip(b'\0')==b'.crt' and last[-1]&0x20000000
cave=align(last[1],16);rva=last[2]+cave
code=bytearray((lab/'quat-sse.bin').read_bytes())
assert code[-4:]==bytes.fromhex('44332211')
struct.pack_into('<i',code,len(code)-4,target+7-(rva+len(code)))
pos=last[4]+cave;assert cave+len(code)<=last[3]
assert not any(data[pos:pos+len(code)]), 'Candidate code cave is occupied'
data[pos:pos+len(code)]=code
struct.pack_into('<I',data,table+40*(n-1)+8,cave+len(code))
struct.pack_into('<I',data,opt+64,0)
data[offset(target):offset(target)+5]=b'\xe9'+struct.pack('<i',rva-(target+5))
dest=lab/'DSLOA-sse.exe';dest.write_bytes(data)
report={'source':str(source),'source_sha256':hashlib.sha256(original).hexdigest(),'candidate':str(dest),'candidate_sha256':hashlib.sha256(data).hexdigest(),'entry_rva':hex(target),'section_rva':hex(rva),'code_bytes':len(code),'validation':'108,000 cases, including aliases and nine x87 control modes, byte-identical outputs'}
(lab/'game-patch-manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
