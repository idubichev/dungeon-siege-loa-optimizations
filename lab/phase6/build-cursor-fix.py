from pathlib import Path
import struct,json,hashlib
p=Path(__file__).resolve().parent;p4=p.parent/'phase4'
cursor=(p4/'build-cursor-colors.py').read_text().replace("p.parent/'phase4/04-cursor-colors'", "p.parent/'phase6/03-native-arrow'").replace("p.parent/'phase4/native-cursor-colors.c'", "p.parent/'phase6/native-arrow.c'").replace('40+64*28+8192','40')
exec(compile(cursor,str(p4/'build-cursor-colors.py'),'exec'),{'__file__':str(p4/'build-cursor-colors.py')})
triangle=(p4/'build-triangle-safe.py').read_text().replace("p/'04-cursor-colors/DSLOA.exe'", "p.parent/'phase6/03-native-arrow/DSLOA.exe'").replace("out=p/'24-triangle-safe'", "out=p.parent/'phase6/04-triangle'")
exec(compile(triangle,str(p4/'build-triangle-safe.py'),'exec'),{'__file__':str(p4/'build-triangle-safe.py')})
s=(p.parent/'phase2/build-static-patches.py').read_text();scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
pe=scope['PE'](p/'04-triangle/DSLOA.exe');pe.packed=False
state=int(json.loads((p/'03-native-arrow/manifest.json').read_text())['state_va'],16)
pos,va=pe.reserve(16)
pe.put(pos,b'\x89\x0d'+struct.pack('<I',state+32)+bytes.fromhex('5333c032db')+b'\xe9'+struct.pack('<i',0x415d1d-(va+16)));pe.absolute(pos+2)
pe.hook(0x415d18,bytes.fromhex('5333c032db'),va,'native-cursor-track-camera-mode')
entry=0x415d2d;old=bytes.fromhex('66f7810c010000800f750b')
assert pe.read(entry,len(old))==old,pe.read(entry,len(old)).hex()
o=pe.offset(entry-pe.base);pe.b[o:o+len(old)]=b'\x90'*len(old)
out=p/'05-cursor-fixed';out.mkdir(exist_ok=True);m=pe.finish(out/'DSLOA.exe');m['state_va']=hex(state);m['direct_patches']=[{'entry':hex(entry),'original':old.hex(),'replacement':('90'*len(old)),'purpose':'Button-held pointing stays absolute; fullscreen and explicit relative camera modes remain available.'}]
(out/'manifest.json').write_text(json.dumps(m,indent=2));print(m)
