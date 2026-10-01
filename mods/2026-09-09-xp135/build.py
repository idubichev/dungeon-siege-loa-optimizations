"""Stage a relocation-free 1.35x combat-XP hook in the verified optimized EXE."""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parent
GAME = Path.home() / 'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
SUPPORT = Path.home() / 'Library/Application Support/Dungeon Siege Optimized'
baseline = (GAME / 'DSLOA.exe').read_bytes()
digest = lambda data: hashlib.sha256(data).hexdigest()
expected = json.loads((SUPPORT / 'static-manifest.json').read_text())['DSLOA.exe']
assert digest(baseline) == expected == '3ff1a56264040d81c6b3e6a44b53301b0f246e0c1f0cdb40f13e7f0ed9e9b4e5'
pe = struct.unpack_from('<I', baseline, 60)[0]
optional = pe + 24
image_base = struct.unpack_from('<I', baseline, optional + 28)[0]
section_table = optional + struct.unpack_from('<H', baseline, pe + 20)[0]
sections = []
for i in range(struct.unpack_from('<H', baseline, pe + 6)[0]):
    header = section_table + i * 40
    name, virtual_size, rva, raw_size, offset = struct.unpack_from('<8sIIII', baseline, header)
    sections.append((name.rstrip(b'\0'), virtual_size, rva, raw_size, offset, header))

def file_offset(va):
    return next(offset + va - image_base - rva for _, _, rva, size, offset, _ in sections
                if image_base + rva <= va < image_base + rva + size)

# All CalculateExperience exits converge here with the result in x87 ST(0).
entry = 0x5b699d
original = bytes.fromhex('5f5ec9c21000')  # pop edi; pop esi; leave; ret 16
assert baseline[file_offset(entry):file_offset(entry) + 6] == original
name, size, rva, raw_size, offset, header = [s for s in sections if s[0] == b'.dsopt'][-1]
cave_offset = (size + 15) & ~15
cave_va = image_base + rva + cave_offset
low, high = struct.unpack('<II', struct.pack('<d', 1.35))
# Push a double constant; multiply ST(0); restore ESP without altering flags;
# execute the displaced epilogue. No absolute addresses or relocations.
code = b'\x68' + struct.pack('<I', high) + b'\x68' + struct.pack('<I', low)
code += bytes.fromhex('dc0c248d642408') + original
assert cave_offset + len(code) <= raw_size
assert not any(baseline[offset + cave_offset:offset + cave_offset + len(code)])
patch = b'\xe9' + struct.pack('<i', cave_va - entry - 5) + b'\x90'
candidate = bytearray(baseline)
candidate[file_offset(entry):file_offset(entry) + 6] = patch
candidate[offset + cave_offset:offset + cave_offset + len(code)] = code
struct.pack_into('<I', candidate, header + 8, cave_offset + len(code))
ranges = [(file_offset(entry), 6), (offset + cave_offset, len(code)), (header + 8, 4)]
assert all(any(start <= i < start + length for start, length in ranges)
           for i, (a, b) in enumerate(zip(baseline, candidate)) if a != b)
(ROOT / 'DSLOA-xp135.exe').write_bytes(candidate)
metadata = dict(multiplier=1.35, scope='CalculateExperience combat awards; cast and scripted quest awards unchanged',
                baseline_sha256=expected, candidate_sha256=digest(candidate), entry=hex(entry),
                target=hex(cave_va), original_prefix=original.hex(), patch=patch.hex(),
                code=code.hex(), changed_ranges=ranges, section_header=header,
                previous_virtual_size=size, new_virtual_size=cave_offset + len(code))
(ROOT / 'patch.json').write_text(json.dumps(metadata, indent=2) + '\n')
print(json.dumps(metadata, indent=2))
