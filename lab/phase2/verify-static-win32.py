import ctypes as c,struct,json,sys
from ctypes import wintypes as w
from pathlib import Path
p=Path(__file__).parent;k=c.WinDLL('kernel32',use_last_error=True);u=c.WinDLL('user32');ps=c.WinDLL('psapi')
def bind(lib,n,r,a):f=getattr(lib,n);f.restype=r;f.argtypes=a;return f
hwnd=bind(u,'FindWindowW',w.HWND,[w.LPCWSTR,w.LPCWSTR])(None,'Dungeon Siege');assert hwnd;pid=w.DWORD();tid=u.GetWindowThreadProcessId(hwnd,c.byref(pid));hp=bind(k,'OpenProcess',w.HANDLE,[w.DWORD,w.BOOL,w.DWORD])(0x410,False,pid.value);assert hp
read=bind(k,'ReadProcessMemory',w.BOOL,[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)])
def get(a,n):
 b=c.create_string_buffer(n);got=c.c_size_t();assert read(hp,a,b,n,c.byref(got)) and got.value==n;return b.raw
mods=(w.HMODULE*256)();needed=w.DWORD();assert bind(ps,'EnumProcessModules',w.BOOL,[w.HANDLE,c.c_void_p,w.DWORD,c.POINTER(w.DWORD)])(hp,mods,c.sizeof(mods),c.byref(needed));fn=bind(ps,'GetModuleFileNameExW',w.DWORD,[w.HANDLE,w.HMODULE,w.LPWSTR,w.DWORD]);bases={}
for hm in mods[:needed.value//4]:
 s=c.create_unicode_buffer(1024);fn(hp,hm,s,len(s));bases[s.value.split('\\')[-1].lower()]=hm
level=sys.argv[1] if len(sys.argv)>1 else 'all';m=json.loads((p/('static-'+level)/'manifest.json').read_text());result={'pid':pid.value,'main_thread':tid,'hooks':[],'counters':{}}
for f in m['files']:
 name=Path(f['file']).name.lower();base=bases[name];preferred=0x400000 if name.endswith('.exe') else 0x10000000;delta=base-preferred
 for h in f['hooks']:
  entry=int(h['entry'],16)+delta;target=int(h['target'],16)+delta;expected=b'\xe9'+struct.pack('<i',target-entry-5);actual=get(entry,5);assert actual==expected,(h['name'],hex(entry),actual.hex(),expected.hex());result['hooks'].append(h['name'])
 data=base+int(f['data_section_rva'],16);result['counters'][name]=struct.unpack('<4I',get(data,16))
 if name.endswith('.exe'):result['counters']['slerp2']=struct.unpack('<4I',get(data+(491600 if level in ['last','skin-last'] else 491536),16))
assert get(0x535f3b,1)==b'\xe9';result['hooks'].append('quaternion-executable')
print(json.dumps(result));(p/('static-'+level)/'live-verification.json').write_text(json.dumps(result,indent=2));k.CloseHandle(hp)
