from pathlib import Path
import struct,statistics
root=Path(__file__).parent
exec((root.parent/'phase3/dump-loaded-win32.py').read_text().split('from pathlib import Path\nout=')[0])
manifest=json.loads((root/sys.argv[3]/'manifest.json').read_text());module=next(m for m in modules if m['path'].split('\\')[-1].lower()=='dsloa.exe');address=module['base']+int(manifest['state_va'],16)-0x400000
slots=manifest['slots']
def memory(addr,n):
 b=c.create_string_buffer(n);got=c.c_size_t();assert read(hp,addr,b,n,c.byref(got)) and got.value==n;return b.raw
def snapshot(full=False):
 for _ in range(100):
  raw=memory(address,24+slots*8 if full else 24);counter,ready,hz,seq,index=struct.unpack_from('<IIQII',raw);seq2=struct.unpack('<I',memory(address+16,4))[0]
  if seq==seq2 and not seq%2:break
 else:raise RuntimeError('Inconsistent clock snapshot')
 assert ready and hz
 return raw,index,hz
_,begin,_=snapshot();time.sleep(float(sys.argv[2]));raw,end,hz=snapshot(True)
assert 2<=end-begin<slots,(begin,end)
ticks=[struct.unpack_from('<Q',raw,24+8*(i%slots))[0] for i in range(begin,end)];ms=[(b-a)*1000/hz for a,b in zip(ticks,ticks[1:])];ordered=sorted(ms)
def percentile(p):return ordered[round((len(ordered)-1)*p)]
r={'pid':pid,'frames':len(ms),'elapsed_s':(ticks[-1]-ticks[0])/hz,'mean_fps':1000/statistics.mean(ms),'median_ms':percentile(.5),'p95_ms':percentile(.95),'p99_ms':percentile(.99),'worst_ms':max(ms),'percent_at_or_under_90fps_budget':100*sum(v<=1000/90 for v in ms)/len(ms),'frame_ms':ms,'method':manifest['method'],'limitation':'Timestamp hook has small overhead. Cadence must be paired with screenshots confirming active gameplay; this is not a GPU presentation trace.'}
cursor=struct.unpack('<10I',memory(module['base']+0x7bf000,40));r['cursor_probe']={'current':cursor[0],'count':cursor[1],'hits':cursor[2],'fallbacks':cursor[3],'invalid_handle_samples':cursor[9]}
r['cursor_thread_probe']=struct.unpack('<6I',memory(module['base']+0x7bf000+10024,24))
Path(sys.argv[1]).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='frame_ms'},indent=2),flush=True);close(hp)
