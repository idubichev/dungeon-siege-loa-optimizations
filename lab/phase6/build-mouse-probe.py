from pathlib import Path
import struct,json,hashlib
p=Path(__file__).resolve().parent
s=(p.parent/'phase2/build-static-patches.py').read_text();scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
pe=scope['PE'](p.parent/'phase5/08-arrow-triangle/DSLOA.exe');pe.packed=False
state=pe.data_alloc(16);pos,va=pe.reserve(16)
body=b'\x89\x0d'+struct.pack('<I',state)+bytes.fromhex('5333c032db')+b'\xe9'+struct.pack('<i',0x415d1d-(va+16))
pe.put(pos,body);pe.absolute(pos+2)
pe.hook(0x415d18,bytes.fromhex('5333c032db'),va,'mouse-state-probe')
out=p/'01-probe';out.mkdir(exist_ok=True);m=pe.finish(out/'DSLOA.exe');m['state_va']=hex(state)
(out/'manifest.json').write_text(json.dumps(m,indent=2));print(m)
