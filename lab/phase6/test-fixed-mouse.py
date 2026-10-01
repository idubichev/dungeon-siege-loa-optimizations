from pathlib import Path
import struct
root=Path(__file__).resolve().parent
exec((root.parent/'phase3/dump-loaded-win32.py').read_text().split('from pathlib import Path\nout=')[0])
def memory(a,n):
 b=c.create_string_buffer(n);got=c.c_size_t();assert read(hp,a,b,n,c.byref(got));return b.raw
base=next(m['base'] for m in modules if m['path'].split('\\')[-1].lower()=='dsloa.exe')
obj=struct.unpack('<I',memory(base+0x7bf020,4))[0]
exec((root.parent/'phase5/wine-input.py').read_text().split('mode =')[0])
def record(label):
 raw=memory(obj,0x194);pt=w.POINT();u.GetCursorPos(c.byref(pt));u.ScreenToClient(hwnd,c.byref(pt))
 ci=CursorInfo();ci.size=c.sizeof(ci);u.GetCursorInfo(c.byref(ci))
 return {'visible':ci.flags,'cursor':ci.cursor,'label':label,'pointer':[pt.x,pt.y],**{hex(o):hex(struct.unpack_from('<I',raw,o)[0]) for o in [0x48,0x4c,0x74,0x78,0x10c,0x12c,0x130,0x134,0x138]}}
class CursorInfo(c.Structure):
 _fields_=[('size',w.DWORD),('flags',w.DWORD),('cursor',w.HANDLE),('position',w.POINT)]
results=[record('before')]
pt=w.POINT(570,350);u.ClientToScreen(hwnd,c.byref(pt));u.SetCursorPos(pt.x,pt.y);time.sleep(.3);results.append(record('moved'))
for label,flags in [('left-down',2),('move-held',1),('left-up',4),('right-down',8),('right-move',1),('right-up',16),('middle-down',32),('middle-move',1),('middle-up',64)]:
 send(Input(0,Payload(mouse=Mouse(20 if flags==1 else 0,10 if flags==1 else 0,0,flags,0,0))))
 time.sleep(.3);results.append(record(label))
Path(sys.argv[1]).write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2));close(hp)
