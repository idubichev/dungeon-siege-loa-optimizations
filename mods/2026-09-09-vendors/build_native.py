"""Add a relocation-free store-close helper to unused executable section padding."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

ROOT = Path(__file__).resolve().parent
GAME = Path.home() / 'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
baseline = (GAME / 'DSLOA.exe').read_bytes()
expected = 'cf1671a5e652c4a5ff0b6d4b4cbd07ee472abc6556fa3e312cd43b19e5c2a2ea'
assert hashlib.sha256(baseline).hexdigest() == expected
subprocess.run(['clang', '-target', 'i686-w64-windows-gnu', '-c', str(ROOT/'reroll.s'), '-o', str(ROOT/'reroll.obj')], check=True)
obj = (ROOT/'reroll.obj').read_bytes()
code_size, code_at, reloc_at = struct.unpack_from('<III', obj, 36)
assert struct.unpack_from('<H', obj, 52)[0] == 0, 'Unexpected COFF relocations'
code = bytearray(obj[code_at:code_at+code_size])
pe = struct.unpack_from('<I', baseline, 60)[0]
optional = pe+24
base = struct.unpack_from('<I', baseline, optional+28)[0]
table = optional+struct.unpack_from('<H', baseline, pe+20)[0]
sections = []
for i in range(struct.unpack_from('<H', baseline, pe+6)[0]):
    header = table+i*40
    name, size, rva, raw_size, offset = struct.unpack_from('<8sIIII', baseline, header)
    sections.append((name.rstrip(b'\0'), size, rva, raw_size, offset, header))
section = next(s for s in reversed(sections) if s[0] == b'.dsopt' and ((s[1]+15)&~15)+len(code) <= s[3])
_, size, rva, raw_size, offset, header = section
cave_offset = (size+15)&~15
target = base+rva+cave_offset
assert not any(baseline[offset+cave_offset:offset+cave_offset+len(code)])
functions = [0x63d36d, 0x5357b0, 0x43a760, 0x573ab5, 0x573108, 0x4ac4f4,
             0x5764ec, 0x492570, 0x471544, 0x654027, 0x43a8e0, 0x57d6fa, 0x5e6418, 0x43a747, 0x654027]
calls = []
for index, address in enumerate(functions, 1):
    token = struct.pack('<I', 0x11110000+index)
    assert code.count(token) == 1
    at = code.index(token)
    assert code[at-1] == 0xe8
    struct.pack_into('<i', code, at, address-(target+at+4))
    calls.append(dict(offset=at-1, address=hex(address)))
entry = 0x5e52f8
entry_offset = next(off+entry-base-rv for _,_,rv,sz,off,_ in sections if base+rv <= entry < base+rv+sz)
original = bytes.fromhex('e870800500')
assert baseline[entry_offset:entry_offset+5] == original
patch = b'\xe8'+struct.pack('<i', target-entry-5)
candidate = bytearray(baseline)
candidate[entry_offset:entry_offset+5] = patch
candidate[offset+cave_offset:offset+cave_offset+len(code)] = code
struct.pack_into('<I', candidate, header+8, cave_offset+len(code))
ranges = [(entry_offset,5),(offset+cave_offset,len(code)),(header+8,4)]
assert all(any(start<=i<start+n for start,n in ranges) for i,(a,b) in enumerate(zip(baseline,candidate)) if a!=b)
(ROOT/'DSLOA-vendors.exe').write_bytes(candidate)
(ROOT/'reroll.bin').write_bytes(code)
meta = dict(baseline_sha256=expected, candidate_sha256=hashlib.sha256(candidate).hexdigest(),
            entry=hex(entry), target=hex(target), original_prefix=original.hex(), patch=patch.hex(),
            code=code.hex(), calls=calls, changed_ranges=ranges, reroll='last shopper exits',
            buyback_items_preserved=True)
(ROOT/'patch.json').write_text(json.dumps(meta,indent=2)+'\n')
print(f'Built {len(code)}-byte helper at {target:#x}; no absolute addresses or added relocations.')
