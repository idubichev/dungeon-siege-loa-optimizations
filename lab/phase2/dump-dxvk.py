from pathlib import Path
import struct,capstone,sys
b=Path('~/Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege/d3d11.dll').read_bytes();pe=struct.unpack_from('<I',b,60)[0];o=pe+24;ss=o+struct.unpack_from('<H',b,pe+20)[0];sec=[struct.unpack_from('<4I',b,ss+i*40+8) for i in range(struct.unpack_from('<H',b,pe+6)[0])]
def off(r):
 vs,va,sz,rp=next(s for s in sec if s[1]<=r<s[1]+s[2]);return rp+r-va
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.skipdata=True
start=int(sys.argv[1],16);end=int(sys.argv[2],16)
for x in cs.disasm(b[off(start):off(end)],start):print(hex(x.address),x.mnemonic,x.op_str)
