"""Read timing counters without suspending or writing to the game."""
from pathlib import Path
import struct
source=(Path(__file__).parent/'dump-loaded-win32.py').read_text()
exec(source.split('from pathlib import Path\nout=')[0])
module=next(m for m in modules if m['path'].split('\\')[-1].lower()=='ddraw.dll')
base=module['base']
def memory(address,size):
    buf=c.create_string_buffer(size);got=c.c_size_t()
    assert read(hp,address,buf,size,c.byref(got)) and got.value==size
    return buf.raw
assert memory(base+0x2f82,6)==bytes.fromhex('e97993030090')
def snapshot():
    for _ in range(100):
        buf=memory(base+0x4c000,64)
        sequence=struct.unpack_from('<I',buf,32)[0]
        again=struct.unpack('<I',memory(base+0x4c020,4))[0]
        if sequence%2==0 and sequence==again:
            assert buf[40:48]==b'DSGUARD1'
            return {'wall_seconds':time.perf_counter(),
                    'calls':struct.unpack_from('<I',buf,16)[0],
                    'ticks':struct.unpack_from('<Q',buf,24)[0],
                    'frequency':struct.unpack_from('<Q',buf,8)[0],
                    'sequence':sequence}
    raise RuntimeError('Could not obtain consistent counters')
before=snapshot();time.sleep(float(sys.argv[2]));after=snapshot()
seconds=after['wall_seconds']-before['wall_seconds']
elapsed=(after['ticks']-before['ticks'])/after['frequency']
calls=after['calls']-before['calls']
result={'pid':pid,'module':module,'before':before,'after':after,
        'seconds':seconds,'calls':calls,'calls_per_second':calls/seconds,
        'handler_wall_seconds':elapsed,'handler_wall_percent':elapsed/seconds*100,
        'mean_handler_us':elapsed/calls*1e6 if calls else None,
        'method':'QPC around DDraw+0x2f82 original surface handler. Includes its CPU work and waits, excludes initial Wine fault dispatch and outer VEH surface-list walk. Timing instrumentation overhead included. Summed serialized handler calls; counters read without game suspension.'}
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
close(hp)
