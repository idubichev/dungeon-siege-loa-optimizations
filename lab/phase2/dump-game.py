from pathlib import Path
import struct,capstone,sys
p=Path(__file__).parent;b=(p/'rollback/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege/DSLOA.exe').read_bytes();pe=struct.unpack_from('<I',b,60)[0];o=pe+24;sh=o+struct.unpack_from('<H',b,pe+20)[0];a=int(sys.argv[1],0);z=int(sys.argv[2],0);sections=[struct.unpack_from('<4I',b,sh+i*40+8) for i in range(struct.unpack_from('<H',b,pe+6)[0])];vs,va,rs,rp=next(s for s in sections if s[1]<=a-0x400000<s[1]+s[2]);off=rp+a-0x400000-va
for x in capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(b[off:off+z-a],a):print(hex(x.address),x.mnemonic,x.op_str)
