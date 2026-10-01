import sys
"""Bounded, non-debugger sampling of the isolated game's busiest thread.

Runs with the task-local 32-bit embedded Python under the test Wine prefix.
Reads thread contexts and a short stack; never patches memory or saves.
"""
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
open_thread=bind(k,'OpenThread',w.HANDLE,[w.DWORD,w.BOOL,w.DWORD])
times=bind(k,'GetThreadTimes',w.BOOL,[w.HANDLE]+[c.POINTER(c.c_ulonglong)]*4)
threads=[]
for t in entries(4,Thread,'Thread32First','Thread32Next'):
    if t.pid!=pid: continue
    h=open_thread(0x42,False,t.tid)
    if not h: continue
    v=[c.c_ulonglong() for _ in range(4)]
    if times(h,*[c.byref(x) for x in v]): threads.append((v[2].value+v[3].value,t.tid))
    close(h)
# This Wine build returns zero thread CPU times; its first thread is the game main thread.
tid=max(threads)[1] if any(t[0] for t in threads) else threads[0][1]
user=c.WinDLL('user32',use_last_error=True)
hwnd=bind(user,'FindWindowW',w.HWND,[w.LPCWSTR,w.LPCWSTR])(None,'Dungeon Siege')
window_pid=w.DWORD()
window_tid=bind(user,'GetWindowThreadProcessId',w.DWORD,[w.HWND,c.POINTER(w.DWORD)])(hwnd,c.byref(window_pid))
assert window_pid.value==pid and window_tid, "Live main window is required"
tid=window_tid
print(json.dumps({'pid':pid,'threads':threads,'window_pid':window_pid.value,'tid':tid}),flush=True)
hp=bind(k,'OpenProcess',w.HANDLE,[w.DWORD,w.BOOL,w.DWORD])(0x43a,False,pid)
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

from pathlib import Path
import struct
lab=Path(__file__).parent
getmod=bind(k,'GetModuleHandleExW',w.BOOL,[w.DWORD,c.c_void_p,c.POINTER(w.HMODULE)])
modname=bind(k,'GetModuleFileNameW',w.DWORD,[w.HMODULE,w.LPWSTR,w.DWORD])
functions=[]
for name in ['OpenThread','SuspendThread','ResumeThread','GetThreadContext','Sleep','CloseHandle','GetLastError']:
 addr=c.cast(getattr(k,name),c.c_void_p).value;hm=w.HMODULE();assert getmod(6,addr,c.byref(hm))
 path=c.create_unicode_buffer(1024);modname(hm,path,len(path));namepart=path.value.split('\\')[-1].lower()
 remote=next(m['base'] for m in modules if m['path'].split('\\')[-1].lower()==namepart)
 functions.append(remote+addr-hm.value)
va=bind(k,'VirtualAllocEx',c.c_void_p,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD])
wr=bind(k,'WriteProcessMemory',w.BOOL,[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)])
rd=bind(k,'ReadProcessMemory',w.BOOL,[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)])
size=52+84*256;dataaddr=va(hp,None,size,0x3000,4);codeaddr=va(hp,None,4096,0x3000,0x40);assert dataaddr and codeaddr
blob=(lab/'sampler-thread.bin').read_bytes();header=struct.pack('<13I',tid,160,11,0,0,0,*functions);n=c.c_size_t()
assert wr(hp,dataaddr,header,len(header),c.byref(n));assert wr(hp,codeaddr,blob,len(blob),c.byref(n))
thread=bind(k,'CreateRemoteThread',w.HANDLE,[w.HANDLE,c.c_void_p,c.c_size_t,c.c_void_p,c.c_void_p,w.DWORD,c.POINTER(w.DWORD)])(hp,None,0,codeaddr,dataaddr,0,None);assert thread,c.get_last_error()
status=bind(k,'WaitForSingleObject',w.DWORD,[w.HANDLE,w.DWORD])(thread,8000)
buf=c.create_string_buffer(size);assert rd(hp,dataaddr,buf,size,c.byref(n))
header=struct.unpack_from('<13I',buf);samples=[]
for i in range(header[3]):
 v=struct.unpack_from('<21I',buf,52+84*i);samples.append(dict(zip(['eip','esp','ebp','eax','ecx','stack'],list(v[:5])+[list(v[5:])])))
result={'pid':pid,'tid':tid,'wait_status':status,'error':header[4],'done':header[5],'modules':modules,'samples':samples}
(lab/(sys.argv[1] if len(sys.argv)>1 else 'cpu-inprocess-latest.json')).write_text(json.dumps(result,indent=2));print(json.dumps({'samples':len(samples),'error':header[4],'done':header[5],'wait_status':status}),flush=True)
close(thread);close(hp)
