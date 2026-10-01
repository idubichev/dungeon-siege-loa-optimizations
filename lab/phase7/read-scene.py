"""Read scene counters identified in the pristine executable with Ghidra."""
from pathlib import Path
import struct
root = Path(__file__).resolve().parent
exec((root.parent / 'phase3/dump-loaded-win32.py').read_text().split('from pathlib import Path\nout=')[0])
module = next(m for m in modules if m['path'].split('\\')[-1].lower() == 'dsloa.exe')
delta = module['base'] - 0x400000
def memory(address, size):
    buf = c.create_string_buffer(size); got = c.c_size_t()
    assert read(hp, address, buf, size, c.byref(got)) and got.value == size
    return buf.raw
def u32(address): return struct.unpack('<I', memory(address, 4))[0]
manager = u32(0x7acf80 + delta)
mask = u32(manager + 0xc0)
assert mask and not (mask & (mask - 1))
scene = u32(u32(manager + 0xc8) + (mask.bit_length() - 1) * 4)
head = u32(scene + 0x6c)
node = u32(head); seen = set(); visible = 0
while node != head:
    assert node not in seen and len(seen) < 100000
    seen.add(node)
    entry = u32(node + 8)
    visible += memory(entry + 0x3d, 1) != b'\0'
    node = u32(node)
pool = u32(0x7acfec + delta)
pool_start, pool_end = struct.unpack('<II', memory(pool, 8))
result = {'pid': pid, 'manager': hex(manager), 'scene': hex(scene),
          'scene_list_entries': len(seen), 'visible_flags': visible,
          'skinning_position_buffer_elements': (pool_end-pool_start)//12,
          'caveat': 'Live read without suspension; visibility flags can span adjacent frames.'}
Path(sys.argv[1]).write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result), flush=True)
close(hp)
