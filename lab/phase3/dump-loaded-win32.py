"""Read-only loaded-module dump of the isolated game; no thread-context access."""
import ctypes as c
from ctypes import wintypes as w
import collections, json, sys, time

k = c.WinDLL('kernel32', use_last_error=True)
p = c.WinDLL('psapi', use_last_error=True)
def bind(lib, name, result, args):
    fn = getattr(lib, name); fn.restype = result; fn.argtypes = args
    return fn
snap = bind(k, 'CreateToolhelp32Snapshot', w.HANDLE, [w.DWORD, w.DWORD])
close = bind(k, 'CloseHandle', w.BOOL, [w.HANDLE])
class Process(c.Structure):
    _fields_ = [('size',w.DWORD),('usage',w.DWORD),('pid',w.DWORD),('heap',c.c_void_p),('module',w.DWORD),('threads',w.DWORD),('parent',w.DWORD),('priority',w.LONG),('flags',w.DWORD),('exe',w.WCHAR*260)]
class Thread(c.Structure):
    _fields_ = [('size',w.DWORD),('usage',w.DWORD),('tid',w.DWORD),('pid',w.DWORD),('priority',w.LONG),('delta',w.LONG),('flags',w.DWORD)]
def entries(flag, cls, first, nxt):
    h=snap(flag,0); obj=cls();obj.size=c.sizeof(obj)
    a=bind(k,first,w.BOOL,[w.HANDLE,c.POINTER(cls)])
    b=bind(k,nxt,w.BOOL,[w.HANDLE,c.POINTER(cls)])
    try:
        ok=a(h,c.byref(obj))
        while ok:
            yield cls.from_buffer_copy(obj)
            ok=b(h,c.byref(obj))
    finally: close(h)
matches=[x for x in entries(2,Process,'Process32FirstW','Process32NextW') if x.exe.lower()=='dsloa.exe']
assert len(matches)==1, 'Expected exactly one DSLOA.exe in this Wine prefix'
pid=matches[0].pid
hp=bind(k,'OpenProcess',w.HANDLE,[w.DWORD,w.BOOL,w.DWORD])(0x410,False,pid)
assert hp, c.get_last_error()
mods=(w.HMODULE*256)();needed=w.DWORD()
assert bind(p,'EnumProcessModules',w.BOOL,[w.HANDLE,c.c_void_p,w.DWORD,c.POINTER(w.DWORD)])(hp,mods,c.sizeof(mods),c.byref(needed))
class Module(c.Structure):
    _fields_=[('base',c.c_void_p),('size',w.DWORD),('entry',c.c_void_p)]
info=bind(p,'GetModuleInformation',w.BOOL,[w.HANDLE,w.HMODULE,c.POINTER(Module),w.DWORD])
filename=bind(p,'GetModuleFileNameExW',w.DWORD,[w.HANDLE,w.HMODULE,w.LPWSTR,w.DWORD])
modules=[]
for hm in mods[:needed.value//4]:
    mi=Module();name=c.create_unicode_buffer(1024)
    if info(hp,hm,c.byref(mi),c.sizeof(mi)):
        filename(hp,hm,name,len(name));modules.append({'base':mi.base,'size':mi.size,'path':name.value})
dg_base=next((m['base'] for m in modules if m['path'].split('\\')[-1].lower()=='d3dimm.dll'),0)
def label(addr):
    for m in modules:
        if m['base']<=addr<m['base']+m['size']:
            return m['path'].split('\\')[-1]+'+0x%x'%(addr-m['base'])
    return hex(addr)

read=bind(k,'ReadProcessMemory',w.BOOL,[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)])
from pathlib import Path
out=Path(sys.argv[1]);out.mkdir(exist_ok=True)
(out/'modules.json').write_text(json.dumps({'pid':pid,'modules':modules},indent=2))
for m in modules:
 name=m['path'].split('\\')[-1]
 if name.lower() not in ['ddraw.dll','d3dimm.dll','dsloa.exe']:continue
 buf=c.create_string_buffer(m['size']);got=c.c_size_t()
 ok=read(hp,m['base'],buf,len(buf),c.byref(got))
 (out/(name+'.memory.bin')).write_bytes(buf.raw[:got.value])
 print(name,hex(m['base']),len(buf),got.value,ok,flush=True)
close(hp)
