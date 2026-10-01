from pathlib import Path
import struct
cache_dir=Path(__file__).resolve().parent
exec((cache_dir.parent/'phase3/dump-loaded-win32.py').read_text().split('from pathlib import Path\nout=')[0])
m=json.loads((cache_dir/'13-transform-cache/manifest.json').read_text());base=next(m['base'] for m in modules if m['path'].lower().endswith('dsloa.exe'));a=base+int(m['state_va'],16)-0x400000
buf=c.create_string_buffer(16);n=c.c_size_t();assert read(hp,a,buf,16,c.byref(n))
d=dict(zip(['owner','hits','misses','fallbacks'],struct.unpack('<4I',buf.raw)));d['hit_ratio']=d['hits']/max(1,d['hits']+d['misses']);Path(sys.argv[1]).write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d),flush=True);close(hp)
