"""Build a one-time Ehb recruitment bonus against the verified installed game."""
from pathlib import Path
import hashlib
import json
import re
import struct
import sys

ROOT = Path(__file__).resolve().parent
GAME = Path.home() / 'Applications/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
SUPPORT = Path.home() / 'Library/Application Support/Dungeon Siege Optimized'
sys.path.insert(0, str(ROOT.parent / '2026-09-06/tools'))
from tank import Tank, write_tank

digest = lambda data: hashlib.sha256(data).hexdigest()
baseline = (GAME / 'DSLOA.exe').read_bytes()
expected = 'fd02321313e9a4e493050fc5350cad292df17f8449bda6ac8195579bb5d2da1c'
assert digest(baseline) == expected
assert json.loads((SUPPORT / 'static-manifest.json').read_text())['DSLOA.exe'] == expected
pe = struct.unpack_from('<I', baseline, 60)[0]
optional = pe + 24
image_base = struct.unpack_from('<I', baseline, optional + 28)[0]
table = optional + struct.unpack_from('<H', baseline, pe + 20)[0]
sections = []
for i in range(struct.unpack_from('<H', baseline, pe + 6)[0]):
    header = table + i * 40
    name, size, rva, raw_size, offset = struct.unpack_from('<8sIIII', baseline, header)
    sections.append((name.rstrip(b'\0'), size, rva, raw_size, offset, header))

def file_offset(va):
    return next(offset + va - image_base - rva for _, _, rva, size, offset, _ in sections
                if image_base + rva <= va < image_base + rva + size)

# Intercept only the Rules setter's call, not other internal skill setters.
# The private -1002.0 request adds two to the raw XP-derived level at +0x30.
# Starting stats (+0x38) and equipment/buff-adjusted stats (+0x34) are untouched.
# The original setter still updates XP, next-level threshold and dirty flags.
entry, setter = 0x5b9377, 0x5b9690
original = bytes.fromhex('e814030000')
assert baseline[file_offset(entry):file_offset(entry) + 5] == original
_, size, rva, raw_size, offset, header = next(s for s in sections if s[0] == b'.dsopt')
cave_offset = (size + 15) & ~15
target = image_base + rva + cave_offset
code = bytes.fromhex('9c817c2408') + struct.pack('<f', -1002.0)
addition = bytes.fromhex('6800000040d94130d80424d95c240c8d642404')
code += b'\x75' + bytes([len(addition)]) + addition + b'\x9d'
code += b'\xe9' + struct.pack('<i', setter - (target + len(code) + 5))
assert cave_offset + len(code) <= raw_size
assert not any(baseline[offset + cave_offset:offset + cave_offset + len(code)])
patch = b'\xe8' + struct.pack('<i', target - entry - 5)
candidate = bytearray(baseline)
candidate[file_offset(entry):file_offset(entry) + 5] = patch
candidate[offset + cave_offset:offset + cave_offset + len(code)] = code
struct.pack_into('<I', candidate, header + 8, cave_offset + len(code))
ranges = [(file_offset(entry), 5), (offset + cave_offset, len(code)), (header + 8, 4)]
assert all(any(start <= i < start + length for start, length in ranges)
           for i, (a, b) in enumerate(zip(baseline, candidate)) if a != b)
(ROOT / 'DSLOA-recruits.exe').write_bytes(candidate)

names = 'andiemus boryev gloern goquua gyorn kroduk lord_bolingar merik naidi phaedriel rhut rusk sikra ulfgrim ulora zed'.split()
tanks = sorted([Tank(f) for folder in ['Resources', 'DSLOA'] for f in (GAME / folder).glob('*.dsres')],
               key=lambda tank: tank.priority)
effective = {path: tank for tank in tanks for path in tank.files}
files, sources = {}, []
pattern = re.compile(r'(if\s*\(\s*GameAuditor\.GetDb\.GetBool\(\s*"party_accept_(0x[0-9a-fA-F]+)"\s*\)\s*\)\s*\{)')
for name in names:
    path = f'world/ai/jobs/actors/good/job_talk_{name}.skrit'
    raw = effective[path].read(path)
    text = raw.decode('cp1252')
    assert 'ds_recruit' not in text and '-1002' not in text
    matches = list(pattern.finditer(text))
    assert len(matches) == 1, (name, len(matches))
    match = matches[0]
    marker = 'ds_recruit_bonus_v1_' + match[2].lower()
    bonus = '\r\n' + '\r\n'.join([
        '\t\t\t// One-time natural attribute bonus; requires the paired optimized EXE.',
        f'\t\t\tif ( !GameAuditor.GetDb.GetBool( "{marker}" ) )',
        '\t\t\t{',
        *[f'\t\t\t\tRules.RCSetNaturalSkillLevel( m_Go$.Goid, "{skill}", -1002.0 );'
          for skill in ['Strength', 'Dexterity', 'Intelligence']],
        f'\t\t\t\tGameAuditor.GetDb.SetBool( "{marker}", true );',
        '\t\t\t}',
    ])
    modified = text[:match.end()] + bonus + text[match.end():]
    assert modified.replace(bonus, '', 1) == text
    assert modified.count('RCSetNaturalSkillLevel') == text.count('RCSetNaturalSkillLevel') + 3
    files[path] = modified.encode('cp1252')
    for folder, content in [('original', raw), ('source', files[path])]:
        dest = ROOT / folder / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
    sources.append(dict(name=name, path=path, archive=str(effective[path].path),
                        original_sha256=digest(raw), marker=marker))

archive = ROOT / 'DS_Companion_Bonus.dsres'
write_tank(archive, files, GAME / 'DSLOA/Expansion.dsres', 'Ehb recruits: +2 natural attributes once')
for path in files:
    assert Tank(archive).priority > effective[path].priority, path
meta = dict(baseline_sha256=expected, candidate_sha256=digest(candidate), entry=hex(entry),
            target=hex(target), setter=hex(setter), original_prefix=original.hex(), patch=patch.hex(),
            code=code.hex(), changed_ranges=ranges, bonus=2, request=-1002.0,
            archive_sha256=digest(archive.read_bytes()), recruits=sources)
(ROOT / 'patch.json').write_text(json.dumps(meta, indent=2) + '\n')
print(f'Built {len(files)} Ehb recruitment callbacks and {len(code)}-byte native helper.')
