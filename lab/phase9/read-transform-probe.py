from pathlib import Path
import struct
probe_dir=Path(__file__).resolve().parent
exec((probe_dir.parent/'phase3/dump-loaded-win32.py').read_text().split('from pathlib import Path\nout=')[0])
build=probe_dir/'02-transform-probe';m=json.loads((build/'manifest.json').read_text());base=next(m['base'] for m in modules if m['path'].lower().endswith('dsloa.exe'));a=base+int(m['state_va'],16)-0x400000
buf=c.create_string_buffer(m['state_bytes']);n=c.c_size_t();seq=c.c_uint()
for _ in range(1000):
 assert read(hp,a,buf,len(buf),c.byref(n));assert read(hp,a,c.byref(seq),4,c.byref(n))
 if seq.value%2==0 and seq.value==struct.unpack_from('<I',buf.raw)[0]:break
else:raise RuntimeError('Could not take a consistent probe snapshot')
fields=['sequence','calls','get_failed','identity','left_match','right_match','neither'];d=dict(zip(fields,struct.unpack_from('<7I',buf.raw)))
for i,k in enumerate(['before','after','left','right']):d[k]=list(struct.unpack_from('<16f',buf.raw,28+i*64))
d['object']=list(struct.unpack_from('<40f',buf.raw,28+256));Path(sys.argv[1]).write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:d[k]for k in fields}),flush=True);close(hp)
