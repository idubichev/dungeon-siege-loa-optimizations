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
if window_pid.value==pid:tid=window_tid
print(json.dumps({'pid':pid,'threads':threads,'window_pid':window_pid.value,'tid':tid}),flush=True)
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
h=open_thread(0x5a,False,tid);assert h,c.get_last_error()
suspend=bind(k,'SuspendThread',w.DWORD,[w.HANDLE])
resume=bind(k,'ResumeThread',w.DWORD,[w.HANDLE])
context=bind(k,'GetThreadContext',w.BOOL,[w.HANDLE,c.c_void_p])
read=bind(k,'ReadProcessMemory',w.BOOL,[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)])
for m in modules:
    if m['path'].split('\\')[-1].lower()=='d3dimm.dll':
        buf=c.create_string_buffer(0x2000);got=c.c_size_t()
        if read(hp,m['base']+0x6000,buf,len(buf),c.byref(got)):
            with open(sys.argv[1]+'.dg-geometry.bin','wb') as f:f.write(buf.raw[:got.value])
samples=[];start=time.monotonic()
try:
    for _ in range(int(sys.argv[2]) if len(sys.argv)>2 else 200):
        if time.monotonic()-start>6:break
        ctx=(w.DWORD*179)();ctx[0]=0x10003
        count=suspend(h);assert count!=0xffffffff,c.get_last_error()
        try:
            assert context(h,ctx),c.get_last_error()
            stack=(w.DWORD*32)();got=c.c_size_t()
            read(hp,ctx[49],stack,c.sizeof(stack),c.byref(got))
            sample={'eip':ctx[46],'esp':ctx[49],'ebp':ctx[45],'eax':ctx[44],'ecx':ctx[43],'stack':list(stack)[:got.value//4]}
            if dg_base+0x6ea1<=ctx[46]<dg_base+0x72e8:
                mat=c.create_string_buffer(64);args=c.create_string_buffer(8)
                if read(hp,ctx[44],mat,64,c.byref(got)) and read(hp,ctx[45]+8,args,8,c.byref(got)):
                    sample['inverse_matrix']=mat.raw.hex();sample['inverse_args']=args.raw.hex()
            samples.append(sample)
        finally: resume(h)
        time.sleep(0.013)
finally:
    close(h);close(hp)
counts=collections.Counter(label(s['eip']) for s in samples)
result={'pid':pid,'tid':tid,'seconds':time.monotonic()-start,'threads':threads,'modules':modules,'samples':samples,'counts':counts}
with open(sys.argv[1],'w') as f:json.dump(result,f,indent=2)
print(json.dumps({'pid':pid,'tid':tid,'samples':len(samples),'seconds':result['seconds'],'counts':counts.most_common(30)},indent=2))
