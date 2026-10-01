"""Read native-cursor state and query its real Win32 cursor objects."""
from pathlib import Path
import struct
source=(Path(__file__).parent/'dump-loaded-win32.py').read_text()
exec(source.split('from pathlib import Path\nout=')[0])
root=Path(__file__).parent
manifest=json.loads((root/'16-native-cursor/manifest.json').read_text())
module=next(m for m in modules if m['path'].split('\\')[-1].lower()=='dsloa.exe')
base=module['base'];address=base+int(manifest['state_va'],16)-0x400000
def memory(address,size):
    buf=c.create_string_buffer(size);got=c.c_size_t()
    assert read(hp,address,buf,size,c.byref(got)) and got.value==size
    return buf.raw
raw=memory(address,40+64*28)
current,count,hits,fallbacks=struct.unpack_from('<4I',raw)
assert count<=64
u=c.WinDLL('user32',use_last_error=True);g=c.WinDLL('gdi32',use_last_error=True)
class CI(c.Structure):
    _fields_=[('size',w.DWORD),('flags',w.DWORD),('cursor',w.HANDLE),('x',w.LONG),('y',w.LONG)]
class II(c.Structure):
    _fields_=[('icon',w.BOOL),('x',w.DWORD),('y',w.DWORD),('mask',w.HANDLE),('color',w.HANDLE)]
getci=bind(u,'GetCursorInfo',w.BOOL,[c.POINTER(CI)])
getii=bind(u,'GetIconInfo',w.BOOL,[w.HANDLE,c.POINTER(II)])
delete=bind(g,'DeleteObject',w.BOOL,[w.HANDLE])
ci=CI();ci.size=c.sizeof(ci);assert getci(c.byref(ci))
out=Path(sys.argv[1]);out.mkdir(exist_ok=True)
entries=[]
for i in range(count):
    image,pixels,width,height,x,y,handle=struct.unpack_from('<7I',raw,40+i*28)
    entry=dict(image=hex(image),pixels=hex(pixels),width=width,height=height,x=x,y=y,handle=handle)
    ii=II();ok=getii(handle,c.byref(ii));entry['GetIconInfo_success']=bool(ok)
    if ok:
        entry['native_hotspot']=[ii.x,ii.y];entry['native_is_icon']=bool(ii.icon)
        assert [ii.x,ii.y]==[x,y] and not ii.icon
        delete(ii.mask);delete(ii.color)
    (out/f'cursor-{i}-source.bgra').write_bytes(memory(pixels,width*height*4))
    entries.append(entry)
result={'pid':pid,'module':module,'state_address':hex(address),'current':current,'count':count,'hits':hits,'fallbacks':fallbacks,'cursor_info':{'flags':ci.flags,'handle':ci.cursor,'x':ci.x,'y':ci.y},'entries':entries}
(out/'state.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
close(hp)
