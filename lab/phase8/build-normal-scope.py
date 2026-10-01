"""Hoist MXCSR setup out of the indexed normal-transform loop."""
from pathlib import Path
import struct,json,hashlib,capstone
p=Path(__file__).resolve().parent
s=(p.parent/'phase2/build-static-patches.py').read_text()
scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
source=p.parent/'phase7/22-native-fastpath/DSLOA.exe';pe=scope['PE'](source);pe.packed=False
out=p/'05-normal-scope';out.mkdir(exist_ok=True)
entry,end=0x69f76f,0x69f7bb
original=pe.read(entry,end-entry)
assert original.hex()=='8b4df88b018b55e48d04408d3cc28b45e88d70f8a5a5a58b018b0b8b49348b75ec8b0c318bd06bd2388d4c1120518b8d64ffffff8d04408d04818b4df050e88967e9ff8345f804ff4dd875b4'
prefix=(p.parent/'phase2/scope-prefix.bin').read_bytes()
quat=(p.parent/'phase2/quat-scoped.bin').read_bytes()
# ldmxcsr; LEA rather than ADD also preserves the loop's final condition flags.
tail=bytes.fromhex('0fae5424048d642408')
qoff=(len(prefix)+len(original)+len(tail)+5+15)//16*16
pos,addr=pe.reserve(qoff+len(quat))
loop=bytearray(original);calloff=0x69f7ad-entry
assert loop[calloff]==0xe8
struct.pack_into('<i',loop,calloff+1,qoff-(len(prefix)+calloff+5))
# The original first seven bytes remain valid behind the preexisting entry hook.
assert quat[-4:]==bytes.fromhex('44332211')
quat=quat[:-4]+struct.pack('<i',0x535f42-(addr+qoff+len(quat)))
body=prefix+loop+tail
body+=b'\xe9'+struct.pack('<i',end-(addr+len(body)+5))
body+=b'\x90'*(qoff-len(body))+quat
pe.put(pos,body);pe.hook(entry,original,addr,'normal-loop-rounding-scope')
m=pe.finish(out/'DSLOA.exe');m.update(source=str(source),entry=hex(entry),end=hex(end),loop_bytes=len(original),prefix_bytes=len(prefix),quat_offset=qoff,tail=tail.hex(),description='Identical indexed normal loop and validated quaternion leaf, with MXCSR setup and restoration once per nonempty loop. Original precision fallback retained. No caches or new game state.')
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');(out/'original-loop.bin').write_bytes(original);(out/'payload.bin').write_bytes(body)
print(m['sha256'])
