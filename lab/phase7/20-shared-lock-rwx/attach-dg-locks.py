"""Attach timing through aligned renderer import pointers; never suspend threads."""
from pathlib import Path
import struct
exec((Path(__file__).resolve().parents[1]/'phase3/dump-loaded-win32.py').read_text().split('from pathlib import Path\nout=')[0])
close(hp);hp=bind(k,'OpenProcess',w.HANDLE,[w.DWORD,w.BOOL,w.DWORD])(0x438,False,pid);assert hp
write=bind(k,'WriteProcessMemory',w.BOOL,[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)])
protect=bind(k,'VirtualProtectEx',w.BOOL,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,c.POINTER(w.DWORD)])
module=bind(k,'GetModuleHandleW',w.HMODULE,[w.LPCWSTR])
manifest=json.loads((Path(__file__).resolve().parent/'09-stall-log/manifest.json').read_text())
exe=next(m['base']for m in modules if m['path'].lower().endswith('dsloa.exe'))
dg=next(m['base']for m in modules if m['path'].lower().endswith('d3dimm.dll'))
nt=next(m['base']for m in modules if m['path'].lower().endswith('ntdll.dll'))
def put(a,v):
 b=c.create_string_buffer(struct.pack('<I',v));n=c.c_size_t();assert a%4==0
 assert write(hp,a,b,4,c.byref(n))and n.value==4
def u(a):
 b=c.c_uint();n=c.c_size_t();assert read(hp,a,c.byref(b),4,c.byref(n))and n.value==4;return b.value
put(exe+int(manifest['lock_va'],16)-0x400000,u(dg+0x34468))
dd=next(m['base']for m in modules if m['path'].lower().endswith('ddraw.dll'))
result=[]
for item,rva,name in zip(manifest['dynamic'],[0x29010,0x2900c],['RtlEnterCriticalSection','RtlLeaveCriticalSection']):
 own=c.cast(getattr(c.WinDLL('ntdll'),name),c.c_void_p).value
 expected=nt+own-module('ntdll.dll');original=u(dg+rva);assert original==expected,(hex(original),hex(expected))
 slot=exe+int(item['slot'],16)-0x400000;target=exe+int(item['target'],16)-0x400000
 put(slot,original);old=w.DWORD();assert protect(hp,dg+rva,4,4,c.byref(old));put(dg+rva,target)
 ignored=w.DWORD();assert protect(hp,dg+rva,4,old.value,c.byref(ignored))
 result.append(dict(item,original=hex(original),iat=hex(dg+rva)))
 dd_iat=dd+(0x21124 if item['name']=='DG_enter' else 0x21128)
 assert u(dd_iat)==original
 assert protect(hp,dd_iat,4,0x40,c.byref(old));put(dd_iat,target)
 # Private diagnostic page stays readable/executable until this process exits.
 print('DDraw previous protection',hex(old.value),flush=True)
 result.append(dict(item,original=hex(original),iat=hex(dd_iat)))
Path(sys.argv[1]).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));close(hp)
