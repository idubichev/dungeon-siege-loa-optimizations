from pathlib import Path
import struct
exec((Path(__file__).resolve().parents[1]/'phase3/dump-loaded-win32.py').read_text().split('from pathlib import Path\nout=')[0])
base=next(x['base']for x in modules if x['path'].split('\\')[-1].lower()=='dsloa.exe')
def memory(a,n):
 b=c.create_string_buffer(n);got=c.c_size_t();assert read(hp,a,b,n,c.byref(got))and got.value==n;return b.raw
def u(a):return struct.unpack('<I',memory(a,4))[0]
manager=u(base+0x7acfc8-0x400000);renderer=u(manager+0x1e0);device=u(renderer+0x600);vt=u(device)
result={'pid':pid,'manager':hex(manager),'renderer':hex(renderer),'device':hex(device),'vtable':hex(vt),'methods':{hex(i):{'address':hex(u(vt+i)),'label':label(u(vt+i))}for i in range(0,0x60,4)},'modules':modules}
Path(sys.argv[1]).write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items()if k!='modules'},indent=2));close(hp)
