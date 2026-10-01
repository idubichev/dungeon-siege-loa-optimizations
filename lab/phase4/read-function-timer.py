"""Read timing counters without suspending or modifying the test game."""
from pathlib import Path
import struct
root=Path(__file__).parent
source=(root.parent/'phase3/dump-loaded-win32.py').read_text()
exec(source.split('from pathlib import Path\nout=')[0])
manifest=json.loads((root/(sys.argv[3] if len(sys.argv)>3 else '01-function-timer')/'manifest.json').read_text())
function_count=len(manifest['functions']);thread_bytes=manifest['layout']['thread_bytes']
module=next(m for m in modules if m['path'].split('\\')[-1].lower()=='dsloa.exe')
address=module['base']+int(manifest['state_va'],16)-0x400000
def memory(address,size):
    buf=c.create_string_buffer(size);got=c.c_size_t()
    assert read(hp,address,buf,size,c.byref(got)) and got.value==size
    return buf.raw
def snapshot():
    raw=memory(address,24);qpc,tid,hz,ready,errors=struct.unpack('<IIQII',raw)
    assert ready and hz
    threads=[]
    for i in range(8):
        addr=address+24+i*thread_bytes
        for _ in range(100):
            raw=memory(addr,16+32*function_count);identifier,depth,seq,dropped=struct.unpack_from('<4I',raw)
            seq2=struct.unpack('<I',memory(addr+8,4))[0]
            if not seq%2 and seq==seq2:break
        else:raise RuntimeError('Inconsistent timing counters')
        if identifier:
            stats=[dict(zip(['calls','total','self','maximum'],struct.unpack_from('<4Q',raw,16+j*32))) for j in range(function_count)]
            threads.append({'id':identifier,'depth':depth,'sequence':seq,'dropped':dropped,'stats':stats})
    return {'time':time.perf_counter(),'hz':hz,'errors':errors,'threads':threads}
time.sleep(3)
before=snapshot();time.sleep(float(sys.argv[2]));after=snapshot()
seconds=after['time']-before['time'];hz=after['hz'];result=[]
for t in after['threads']:
    previous=next((x for x in before['threads'] if x['id']==t['id']),None)
    rows=[]
    for i,v in enumerate(t['stats']):
        old=previous['stats'][i] if previous else {'calls':0,'total':0,'self':0}
        calls=v['calls']-old['calls'];total=(v['total']-old['total'])/hz;own=(v['self']-old['self'])/hz
        rows.append({'function':manifest['functions'][i]['name'],'calls':calls,'calls_per_second':calls/seconds,'inclusive_ms':total*1000,'exclusive_ms':own*1000,'inclusive_wall_percent':total/seconds*100,'exclusive_wall_percent':own/seconds*100,'mean_inclusive_us':total/calls*1e6 if calls else 0,'lifetime_max_ms':v['maximum']/hz*1000})
    result.append({'thread':t['id'],'dropped':t['dropped'],'depth_at_end':t['depth'],'functions':rows})
output={'pid':pid,'seconds':seconds,'errors':after['errors'],'results':result,'before':before,'after':after,'method':manifest['method'],'limitation':'Includes instrumentation overhead. Inclusive recursive/nested times overlap; use exclusive totals. Maximum is since process startup, not just this interval.'}
Path(sys.argv[1]).write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({k:v for k,v in output.items() if k not in ['before','after']},indent=2),flush=True)
close(hp)
