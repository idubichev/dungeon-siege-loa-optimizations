"""Isolated Win32 guard-fault benchmark. No game memory is accessed.

The native loop calls VirtualProtect and reads one byte each iteration.
PAGE_READWRITE and PAGE_READWRITE|PAGE_GUARD use the same loop and page.
The latter invokes a minimal native VEH, verified by an exact fault count.
The difference includes protection changes and fault dispatch, not dgVoodoo.
"""
from pathlib import Path
import ctypes as c
import json
import statistics
import struct
import sys
import time

assert c.sizeof(c.c_void_p) == 4
k = c.WinDLL('kernel32', use_last_error=True)
def bind(name, result, args):
    fn = getattr(k, name)
    fn.restype, fn.argtypes = result, args
    return fn
alloc = bind('VirtualAlloc', c.c_void_p, [c.c_void_p, c.c_size_t, c.c_uint32, c.c_uint32])
protect = bind('VirtualProtect', c.c_int, [c.c_void_p, c.c_size_t, c.c_uint32, c.POINTER(c.c_uint32)])
flush = bind('FlushInstructionCache', c.c_int, [c.c_void_p, c.c_void_p, c.c_size_t])
add = bind('AddVectoredExceptionHandler', c.c_void_p, [c.c_uint32, c.c_void_p])
remove = bind('RemoveVectoredExceptionHandler', c.c_uint32, [c.c_void_p])
free = bind('VirtualFree', c.c_int, [c.c_void_p, c.c_size_t, c.c_uint32])
qpc = bind('QueryPerformanceCounter', c.c_int, [c.POINTER(c.c_int64)])
qpf = bind('QueryPerformanceFrequency', c.c_int, [c.POINTER(c.c_int64)])
page = alloc(None, 4096, 0x3000, 4)
assert page
context = (c.c_uint32 * 2)(page, 0)
root = Path(__file__).parent
def executable(name, replace=False):
    data = (root / name).read_bytes()
    if replace:
        marker = struct.pack('<I', 0x12345678)
        assert data.count(marker) == 1
        data = data.replace(marker, struct.pack('<I', c.addressof(context)))
    address = alloc(None, len(data), 0x3000, 4)
    assert address
    c.memmove(address, data, len(data))
    old = c.c_uint32()
    assert protect(address, len(data), 0x20, c.byref(old))
    assert flush(c.c_void_p(-1), address, len(data))
    return address
handler = executable('exception-handler.bin', True)
loop_address = executable('exception-bench.bin')
loop = c.WINFUNCTYPE(c.c_int, c.c_void_p, c.c_uint32, c.c_uint32, c.c_void_p)(loop_address)
veh = add(1, handler)
assert veh
frequency = c.c_int64()
assert qpf(c.byref(frequency))
def run(count, guard):
    start, end = c.c_int64(), c.c_int64()
    before = context[1]
    assert qpc(c.byref(start))
    ok = loop(page, count, 0x104 if guard else 4, c.cast(protect, c.c_void_p))
    assert qpc(c.byref(end))
    assert ok
    handled = context[1] - before
    assert handled == (count if guard else 0), (handled, count, guard)
    return {'guard': guard, 'iterations': count, 'handled_faults': handled,
            'us_per_iteration': (end.value-start.value)/frequency.value*1e6/count}
try:
    run(1000, False)
    run(1000, True)
    rounds = []
    for i in range(7):
        pair = [run(20000, bool(guard)) for guard in ([0,1] if i%2==0 else [1,0])]
        normal = next(x for x in pair if not x['guard'])
        guarded = next(x for x in pair if x['guard'])
        delta = guarded['us_per_iteration'] - normal['us_per_iteration']
        rounds.append({'pair': pair, 'incremental_guard_us': delta})
        print('round', i+1, 'incremental guard us', round(delta, 3), flush=True)
    increments = [x['incremental_guard_us'] for x in rounds]
    result = {'timestamp': time.time(), 'label': sys.argv[2], 'rounds': rounds,
              'median_incremental_guard_us': statistics.median(increments),
              'min_incremental_guard_us': min(increments),
              'max_incremental_guard_us': max(increments),
              'method': __doc__,
              'limitation': 'Separate process, warm single-page synthetic workload. Does not measure game handler, GPU readbacks, page distribution or critical-path waits.'}
    Path(sys.argv[1]).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'rounds'}, indent=2), flush=True)
finally:
    assert remove(veh)
    for address in [loop_address, handler, page]:
        assert free(address, 0, 0x8000)
