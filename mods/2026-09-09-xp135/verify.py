"""Exercise the actual staged hook without launching or attaching to the game."""
from pathlib import Path
import json
import math
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import *

root = Path(__file__).resolve().parent
meta = json.loads((root / 'patch.json').read_text())
entry = int(meta['entry'], 16)
target = int(meta['target'], 16)
patch = bytes.fromhex(meta['patch'])
code = bytes.fromhex(meta['code'])
disassembly = [f'{i.address:x}: {i.mnemonic} {i.op_str}'
               for i in Cs(CS_ARCH_X86, CS_MODE_32).disasm(code, target)]
results = []
for relocation in [0, 0x1000000]:
    for value in [0.0, 0.125, 1.0, 6.0, 100.0, 1039.38, 1e9, 1e12]:
        u = Uc(UC_ARCH_X86, UC_MODE_32)
        for address in [entry + relocation, target + relocation]:
            u.mem_map(address & ~0xfff, 0x1000)
        u.mem_map(0x2000000, 0x4000)
        start, ret, output, source, frame = 0x2000000, 0x2000100, 0x2001000, 0x2001100, 0x2002800
        u.mem_write(source, struct.pack('<dd', value, 123.25))
        # Keep a second x87 stack value to detect accidental stack imbalance.
        setup = b'\xdd\x05' + struct.pack('<I', source + 8)
        setup += b'\xdd\x05' + struct.pack('<I', source)
        setup += b'\xe9' + struct.pack('<i', entry + relocation - (start + len(setup) + 5))
        u.mem_write(start, setup)
        u.mem_write(entry + relocation, patch)
        u.mem_write(target + relocation, code)
        finish = b'\xdd\x1d' + struct.pack('<I', output)
        finish += b'\xdd\x1d' + struct.pack('<I', output + 8)
        u.mem_write(ret, finish)
        u.mem_write(frame - 0x2c, struct.pack('<II', 0x11112222, 0x33334444))
        u.mem_write(frame, struct.pack('<II', 0x55556666, ret))
        u.reg_write(UC_X86_REG_ESP, frame - 0x2c)
        u.reg_write(UC_X86_REG_EBP, frame)
        for register in [UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX, UC_X86_REG_EDX]:
            u.reg_write(register, 0x12345678)
        u.reg_write(UC_X86_REG_EFLAGS, 0x246)
        u.emu_start(start, ret + len(finish), count=40)
        actual, sentinel = struct.unpack('<dd', bytes(u.mem_read(output, 16)))
        assert math.isclose(actual, value * 1.35, rel_tol=1e-12, abs_tol=1e-12), (value, actual)
        assert sentinel == 123.25
        assert u.reg_read(UC_X86_REG_ESP) == frame + 24
        assert u.reg_read(UC_X86_REG_EBP) == 0x55556666
        assert u.reg_read(UC_X86_REG_EDI) == 0x11112222
        assert u.reg_read(UC_X86_REG_ESI) == 0x33334444
        assert u.reg_read(UC_X86_REG_EFLAGS) == 0x246
        for register in [UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX, UC_X86_REG_EDX]:
            assert u.reg_read(register) == 0x12345678
        results.append(dict(input=value, output=actual, relocation=hex(relocation)))
report = dict(status='passed', method='Unicorn x86 emulation of staged hook and caller epilogue',
              cases=results, disassembly=disassembly, in_game_test=False)
(root / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(f'Passed {len(results)} cases, including relocated addresses, x87 stack, registers, flags and return cleanup.')
