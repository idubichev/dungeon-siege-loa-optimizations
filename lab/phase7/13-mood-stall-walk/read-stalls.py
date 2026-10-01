from pathlib import Path
import struct,collections
root=Path(__file__).resolve().parent
exec((root.parent/'phase3/dump-loaded-win32.py').read_text().split('from pathlib import Path\nout=')[0])
m=json.loads((root/'09-stall-log/manifest.json').read_text())
base=next(x['base']for x in modules if x['path'].split('\\')[-1].lower()=='dsloa.exe')
address=base+int(m['state_va'],16)-0x400000
def memory(a,n):
 b=c.create_string_buffer(n);got=c.c_size_t();assert read(hp,a,b,n,c.byref(got))and got.value==n;return b.raw
counter,tid,hz,ready,begin=struct.unpack('<IIQII',memory(address,24));assert ready and hz
time.sleep(float(sys.argv[2]))
raw=memory(address,24+m['slots']*32);end=struct.unpack_from('<I',raw,20)[0];events=[]
for i in range(max(begin,end-m['slots']),end):
 start,finish,identifier,thread,caller,serial=struct.unpack_from('<QQ4I',raw,24+(i%m['slots'])*32)
 if serial==i+1 and finish>=start and identifier<len(m['functions']):
  events.append({'start':start,'end':finish,'id':identifier,'thread':thread,'caller':hex(caller),'ms':(finish-start)*1000/hz})
origin=min(e['start']for e in events)
for e in events:e['start_s']=(e['start']-origin)/hz;e['end_s']=(e['end']-origin)/hz;e['function']=m['functions'][e['id']][0]
groups=collections.defaultdict(list)
for e in events:groups[e['function']].append(e)
summary={name:{'calls':len(v),'total_ms':sum(e['ms']for e in v),'max_ms':max(e['ms']for e in v)}for name,v in groups.items()}
frames=sorted(groups['render'],key=lambda e:e['start'])
gaps=[{'start_s':a['end_s'],'ms':(b['start']-a['end'])*1000/hz,'next_frame_s':b['start_s']}for a,b in zip(frames,frames[1:])if b['start']-a['end']>hz*.020]
out={'pid':pid,'frequency':hz,'begin':begin,'end':end,'lost_to_wrap':max(0,end-begin-m['slots']),'summary':summary,'stalls':[e for e in events if e['ms']>20],'outside_render_gaps':gaps,'events':events,'limitation':'Diagnostic wrapper overhead is included; function intervals can overlap.'}
Path(sys.argv[1]).write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items()if k!='events'},indent=2),flush=True);close(hp)
