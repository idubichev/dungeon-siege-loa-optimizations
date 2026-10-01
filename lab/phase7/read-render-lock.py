"""Read-only shared renderer lock samples; does not suspend or alter threads."""
from pathlib import Path
import struct
exec((Path(__file__).resolve().parents[1]/'phase3/dump-loaded-win32.py').read_text().split('from pathlib import Path\nout=')[0])
dg=next(m['base']for m in modules if m['path'].lower().endswith('d3dimm.dll'))
def memory(a,n):
 b=c.create_string_buffer(n);got=c.c_size_t();assert read(hp,a,b,n,c.byref(got))and got.value==n;return b.raw
lock=struct.unpack('<I',memory(dg+0x34468,4))[0]
qpc=bind(k,'QueryPerformanceCounter',w.BOOL,[c.POINTER(c.c_longlong)]);freq=bind(k,'QueryPerformanceFrequency',w.BOOL,[c.POINTER(c.c_longlong)])
hz=c.c_longlong();assert freq(c.byref(hz));now=c.c_longlong();qpc(c.byref(now));begin=now.value;end=begin+float(sys.argv[2])*hz.value;samples=[]
while now.value<end:
 raw=struct.unpack('<6I',memory(lock,24));qpc(c.byref(now));samples.append([now.value,*raw]);time.sleep(.001)
Path(sys.argv[1]).write_text(json.dumps({'pid':pid,'lock':hex(lock),'frequency':hz.value,'begin':begin,'columns':['time','DebugInfo','LockCount','RecursionCount','OwningThread','LockSemaphore','SpinCount'],'samples':samples},separators=(',',':')))
print('Read-only lock samples',len(samples),flush=True);close(hp)
