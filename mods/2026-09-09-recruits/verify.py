"""Offline machine-code checks. This does not compile or run Skrit in the game."""
from pathlib import Path
import json
import struct
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import *

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root.parent / '2026-09-06/tools'))
from tank import Tank
from gas import mask
meta = json.loads((root / 'patch.json').read_text())
entry, target, setter = [int(meta[key], 16) for key in ['entry', 'target', 'setter']]
code = bytes.fromhex(meta['code'])
cases = []
for relocation in [0, 0x1000000]:
    for natural in [0.0, 1.25, 10.75, 50.125, 99.5, 178.0]:
        for request in [-1002.0, -1001.0, -1.0, 0.0, 10.5, 180.0]:
            u = Uc(UC_ARCH_X86, UC_MODE_32)
            for page in {address & ~0xfff for address in [entry + relocation, target + relocation, setter + relocation]}:
                u.mem_map(page, 0x1000)
            u.mem_map(0x2000000, 0x5000)
            start, output, source, stack, skill = 0x2000000, 0x2001000, 0x2001100, 0x2002800, 0x2003800
            u.mem_write(source, struct.pack('<d', 123.25))
            setup = b'\xdd\x05' + struct.pack('<I', source)
            setup += b'\xe9' + struct.pack('<i', entry + relocation - (start + len(setup) + 5))
            u.mem_write(start, setup)
            u.mem_write(entry + relocation, bytes.fromhex(meta['patch']))
            u.mem_write(target + relocation, code)
            u.mem_write(stack, struct.pack('<f', request))
            # Deliberately different natural, modified and starting values.
            u.mem_write(skill + 0x30, struct.pack('<fff', natural, natural + 17.0, 10.0))
            before = bytes(u.mem_read(skill, 0x50))
            registers = {UC_X86_REG_EAX: 0x12345678, UC_X86_REG_EBX: 0x23456789,
                         UC_X86_REG_ECX: skill, UC_X86_REG_EDX: 0x34567890,
                         UC_X86_REG_ESI: 0x45678901, UC_X86_REG_EDI: 0x56789012,
                         UC_X86_REG_EBP: 0x67890123, UC_X86_REG_ESP: stack}
            for register, value in registers.items():
                u.reg_write(register, value)
            u.reg_write(UC_X86_REG_EFLAGS, 0x246)
            u.emu_start(start, setter + relocation, count=40)
            actual = struct.unpack('<f', bytes(u.mem_read(stack, 4)))[0]
            assert actual == (natural + 2 if request == -1002.0 else request)
            assert bytes(u.mem_read(skill, 0x50)) == before
            assert u.reg_read(UC_X86_REG_ESP) == stack - 4
            assert struct.unpack('<I', bytes(u.mem_read(stack - 4, 4)))[0] == entry + relocation + 5
            assert u.reg_read(UC_X86_REG_EFLAGS) == 0x246
            for register, value in registers.items():
                if register != UC_X86_REG_ESP:
                    assert u.reg_read(register) == value
            u.mem_write(setter + relocation, b'\xdd\x1d' + struct.pack('<I', output))
            u.emu_start(setter + relocation, setter + relocation + 6, count=1)
            assert struct.unpack('<d', bytes(u.mem_read(output, 8)))[0] == 123.25
            cases.append(dict(natural=natural, request=request, result=actual, relocation=hex(relocation)))

archive = Tank(root / 'DS_Companion_Bonus.dsres')
assert len(archive.files) == len(meta['recruits']) == 16
assert len({row['marker'] for row in meta['recruits']}) == 16
for row in meta['recruits']:
    raw = archive.read(row['path'])
    assert raw == (root / 'source' / row['path']).read_bytes()
    text = raw.decode('cp1252')
    assert text.count(row['marker']) == 2
    masked = mask(text)
    level = 0
    for char in masked:
        if char == '{': level += 1
        if char == '}': level -= 1
        assert level >= 0
    assert level == 0

report = dict(status='passed', native_cases=len(cases), cases=cases,
              disassembly=[f'{i.address:x}: {i.mnemonic} {i.op_str}'
                           for i in Cs(CS_ARCH_X86, CS_MODE_32).disasm(code, target)],
              resource_crc_checks=16, skrit_brace_checks=16, skrit_compiled=False,
              in_game_test=False,
              scope='Actual call and helper emulated to original setter entry; vanilla setter retained byte-for-byte.')
(root / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(f'Passed {len(cases)} native cases and 16 archive/source checks. In-game validation pending.')
