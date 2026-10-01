"""Install or remove validated runtime hooks in the isolated game process."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import sys,struct,json,time
lab=Path(__file__).parent;statefile=lab/'runtime-cache-state.json'
k=c.WinDLL('kernel32',use_last_error=True);u=c.WinDLL('user32',use_last_error=True);p=c.WinDLL('psapi',use_last_error=True)
def bind(lib,name,result,args):
    fn=getattr(lib,name);fn.restype=result;fn.argtypes=args;return fn
def check(ok):
    if not ok:raise c.WinError(c.get_last_error())
find=bind(u,'FindWindowW',w.HWND,[w.LPCWSTR,w.LPCWSTR])
pid=w.DWORD();hwnd=find(None,'Dungeon Siege');assert hwnd,'Game window is not ready'
tid=bind(u,'GetWindowThreadProcessId',w.DWORD,[w.HWND,c.POINTER(w.DWORD)])(hwnd,c.byref(pid))
hp=bind(k,'OpenProcess',w.HANDLE,[w.DWORD,w.BOOL,w.DWORD])(0x438,False,pid.value);check(hp)
read=bind(k,'ReadProcessMemory',w.BOOL,[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)])
write=bind(k,'WriteProcessMemory',w.BOOL,[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)])
protect=bind(k,'VirtualProtectEx',w.BOOL,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,c.POINTER(w.DWORD)])
flush=bind(k,'FlushInstructionCache',w.BOOL,[w.HANDLE,c.c_void_p,c.c_size_t])
close=bind(k,'CloseHandle',w.BOOL,[w.HANDLE])
def get(addr,size):
    b=c.create_string_buffer(size);n=c.c_size_t();check(read(hp,addr,b,size,c.byref(n)));assert n.value==size;return b.raw
def put(addr,data):
    n=c.c_size_t();check(write(hp,addr,data,len(data),c.byref(n)));assert n.value==len(data)
class Thread(c.Structure):
    _fields_=[('size',w.DWORD),('usage',w.DWORD),('tid',w.DWORD),('pid',w.DWORD),('priority',w.LONG),('delta',w.LONG),('flags',w.DWORD)]
def patch(addr,expected,replacement):
    sh=bind(k,'CreateToolhelp32Snapshot',w.HANDLE,[w.DWORD,w.DWORD])(4,0)
    first=bind(k,'Thread32First',w.BOOL,[w.HANDLE,c.POINTER(Thread)])
    nxt=bind(k,'Thread32Next',w.BOOL,[w.HANDLE,c.POINTER(Thread)])
    op=bind(k,'OpenThread',w.HANDLE,[w.DWORD,w.BOOL,w.DWORD])
    suspend=bind(k,'SuspendThread',w.DWORD,[w.HANDLE]);resume=bind(k,'ResumeThread',w.DWORD,[w.HANDLE])
    handles=[];t=Thread();t.size=c.sizeof(t)
    try:
        ok=first(sh,c.byref(t))
        while ok:
            if t.pid==pid.value:
                h=op(2,False,t.tid)
                if h:
                    if suspend(h)!=0xffffffff:handles.append(h)
                    else:close(h)
            ok=nxt(sh,c.byref(t))
        assert handles and get(addr,len(expected))==expected,'Unexpected target bytes'
        previous=w.DWORD();check(protect(hp,addr,len(replacement),0x40,c.byref(previous)))
        try:put(addr,replacement);check(flush(hp,addr,len(replacement)))
        finally:
            ignored=w.DWORD();check(protect(hp,addr,len(replacement),previous.value,c.byref(ignored)))
    finally:
        for h in reversed(handles):resume(h);close(h)
        close(sh)
try:
    action=sys.argv[1]
    if action in ('stats','remove'):
        state=json.loads(statefile.read_text());assert state['pid']==pid.value
        expected=bytes.fromhex(state['hook'])
        assert get(state['entry'],5)==expected,'This process does not have the recorded cache'
        for name in ('matmul','slerp','light','blend','slerp2','vec3'):
            if name in state:
                hook=state[name]
                assert get(hook['entry'],5)==bytes.fromhex(hook['hook']),name+' hook does not match'
        if action=='remove':
            patch(state['entry'],expected,bytes.fromhex(state['original_prefix']))
            if 'matmul' in state:
                m=state['matmul'];patch(m['entry'],bytes.fromhex(m['hook']),bytes.fromhex(m['original_prefix']))
            if 'slerp' in state:
                m=state['slerp'];patch(m['entry'],bytes.fromhex(m['hook']),bytes.fromhex(m['original_prefix']))
            if 'light' in state:
                m=state['light'];patch(m['entry'],bytes.fromhex(m['hook']),bytes.fromhex(m['original_prefix']))
            if 'blend' in state:
                m=state['blend'];patch(m['entry'],bytes.fromhex(m['hook']),bytes.fromhex(m['original_prefix']))
            if 'slerp2' in state:
                m=state['slerp2'];patch(m['entry'],bytes.fromhex(m['hook']),bytes.fromhex(m['original_prefix']))
            if 'vec3' in state:
                m=state['vec3'];patch(m['entry'],bytes.fromhex(m['hook']),bytes.fromhex(m['original_prefix']))
        print(json.dumps({'action':action,'pid':pid.value,'counters':struct.unpack('<4I',get(state['data'],16))}))
        if 'slerp' in state:print(json.dumps({'slerp_counters':struct.unpack('<4I',get(state['slerp']['data'],16))}))
        if 'slerp2' in state:print(json.dumps({'slerp2_counters':struct.unpack('<4I',get(state['slerp2']['data'],16))}))
    elif action=='blend':
        state=json.loads(statefile.read_text());assert state['pid']==pid.value and 'blend' not in state
        entry=0x69f325;original=(lab/'blend-original.bin').read_bytes();assert get(entry,len(original)-1)==original[:-1]
        va=bind(k,'VirtualAllocEx',c.c_void_p,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD])
        addr=va(hp,None,4096,0x3000,4);check(addr)
        dispatch=b'\xe8'+struct.pack('<i',11)+b'\xe9'+struct.pack('<i',entry+len(original)-1-(addr+10))
        body=(lab/'blend-sse.bin').read_bytes();oldoffset=(16+len(body)+15)//16*16
        assert body.count(bytes.fromhex('55443322'))==1
        body=body.replace(bytes.fromhex('55443322'),struct.pack('<I',addr+oldoffset))
        code=dispatch+b'\x90'*6+body;code+=b'\x90'*(oldoffset-len(code))+original
        put(addr,code);prev=w.DWORD();check(protect(hp,addr,4096,0x20,c.byref(prev)));check(flush(hp,addr,len(code)))
        hook=b'\xe9'+struct.pack('<i',addr-(entry+5));patch(entry,original[:5],hook)
        state['blend']={'entry':entry,'code':addr,'hook':hook.hex(),'original_prefix':original[:5].hex()}
        statefile.write_text(json.dumps(state,indent=2));print(json.dumps(state['blend']))
    elif action=='light':
        state=json.loads(statefile.read_text());assert state['pid']==pid.value and 'light' not in state
        entry=0x6a1132;original=(lab/'light-original-fragment.bin').read_bytes();assert get(entry,len(original))==original
        va=bind(k,'VirtualAllocEx',c.c_void_p,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD])
        addr=va(hp,None,4096,0x3000,4);check(addr)
        dispatch=bytearray.fromhex('505152e80000000085d25a59580f8400000000e900000000')
        assert len(dispatch)==24
        struct.pack_into('<i',dispatch,4,32-8)
        struct.pack_into('<i',dispatch,15,0x6a1190-(addr+19))
        struct.pack_into('<i',dispatch,20,0x6a1177-(addr+24))
        body=(lab/'light-sse.bin').read_bytes();oldoffset=(32+len(body)+15)//16*16
        assert body.count(bytes.fromhex('55443322'))==1
        body=body.replace(bytes.fromhex('55443322'),struct.pack('<I',addr+oldoffset))
        code=bytes(dispatch)+b'\x90'*8+body;code+=b'\x90'*(oldoffset-len(code))+(lab/'light-original.bin').read_bytes()
        put(addr,code);prev=w.DWORD();check(protect(hp,addr,4096,0x20,c.byref(prev)));check(flush(hp,addr,len(code)))
        hook=b'\xe9'+struct.pack('<i',addr-(entry+5));patch(entry,original[:5],hook)
        state['light']={'entry':entry,'code':addr,'hook':hook.hex(),'original_prefix':original[:5].hex()}
        statefile.write_text(json.dumps(state,indent=2));print(json.dumps(state['light']))
    elif action=='slerp':
        state=json.loads(statefile.read_text());assert state['pid']==pid.value and 'slerp' not in state
        entry=0x69fa05;original=(lab/'slerp-original.bin').read_bytes();assert get(entry,len(original))==original
        va=bind(k,'VirtualAllocEx',c.c_void_p,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD])
        addr=va(hp,None,4096,0x3000,4);dataaddr=va(hp,None,16+60*8192,0x3000,4);check(addr and dataaddr)
        code=bytearray((lab/'slerp-cache.bin').read_bytes());offset=(len(code)+15)//16*16
        for r in json.loads((lab/'slerp-cache-relocations.json').read_text()):
            v=dataaddr if r['target']=='data' else addr+offset
            struct.pack_into('<I',code,r['offset'],v+r['addend'])
        code.extend(b'\x90'*(offset-len(code)));code.extend(original[:7]+b'\xe9'+struct.pack('<i',entry+7-(addr+offset+12)))
        put(addr,bytes(code));prev=w.DWORD();check(protect(hp,addr,4096,0x20,c.byref(prev)));check(flush(hp,addr,len(code)))
        hook=b'\xe9'+struct.pack('<i',addr-(entry+5));patch(entry,original[:5],hook)
        state['slerp']={'entry':entry,'code':addr,'data':dataaddr,'hook':hook.hex(),'original_prefix':original[:5].hex()}
        statefile.write_text(json.dumps(state,indent=2));print(json.dumps(state['slerp']))
    elif action=='slerp2':
        state=json.loads(statefile.read_text());assert state['pid']==pid.value and 'slerp2' not in state
        entry=0x41adf4;original=(lab/'slerp2-original.bin').read_bytes();assert get(entry,len(original))==original
        va=bind(k,'VirtualAllocEx',c.c_void_p,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD])
        addr=va(hp,None,4096,0x3000,4);dataaddr=va(hp,None,16+60*8192,0x3000,4);check(addr and dataaddr)
        code=bytearray((lab/'slerp2-cache.bin').read_bytes());offset=(len(code)+15)//16*16
        for r in json.loads((lab/'slerp2-cache-relocations.json').read_text()):
            v=dataaddr if r['target']=='data' else addr+offset
            struct.pack_into('<I',code,r['offset'],v+r['addend'])
        code.extend(b'\x90'*(offset-len(code)));code.extend(original[:6]+b'\xe9'+struct.pack('<i',entry+6-(addr+offset+11)))
        put(addr,bytes(code));prev=w.DWORD();check(protect(hp,addr,4096,0x20,c.byref(prev)));check(flush(hp,addr,len(code)))
        hook=b'\xe9'+struct.pack('<i',addr-(entry+5));patch(entry,original[:5],hook)
        state['slerp2']={'entry':entry,'code':addr,'data':dataaddr,'hook':hook.hex(),'original_prefix':original[:5].hex()}
        statefile.write_text(json.dumps(state,indent=2));print(json.dumps(state['slerp2']))
    elif action=='matmul':
        state=json.loads(statefile.read_text());assert state['pid']==pid.value and 'matmul' not in state
        entry=state['entry']-0x6e9b+0x6e44
        original=(lab/'matmul-original.bin').read_bytes();assert get(entry,len(original))==original
        va=bind(k,'VirtualAllocEx',c.c_void_p,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD])
        addr=va(hp,None,4096,0x3000,4);check(addr)
        code=(lab/'matmul-sse.bin').read_bytes();offset=(len(code)+15)//16*16
        assert code.count(bytes.fromhex('55443322'))==1
        code=code.replace(bytes.fromhex('55443322'),struct.pack('<I',addr+offset))
        code+=b'\x90'*(offset-len(code))+original
        put(addr,code);prev=w.DWORD();check(protect(hp,addr,4096,0x20,c.byref(prev)));check(flush(hp,addr,len(code)))
        hook=b'\xe9'+struct.pack('<i',addr-(entry+5));patch(entry,original[:5],hook)
        state['matmul']={'entry':entry,'code':addr,'hook':hook.hex(),'original_prefix':original[:5].hex()}
        statefile.write_text(json.dumps(state,indent=2));print(json.dumps(state['matmul']))
    elif action=='vec3':
        state=json.loads(statefile.read_text());assert state['pid']==pid.value and 'vec3' not in state
        entry=0x43e774
        original=(lab/'vec3-original.bin').read_bytes();assert get(entry,len(original))==original
        va=bind(k,'VirtualAllocEx',c.c_void_p,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD])
        addr=va(hp,None,4096,0x3000,4);check(addr)
        code=(lab/'vec3-sse.bin').read_bytes();offset=(len(code)+15)//16*16
        assert code.count(bytes.fromhex('55443322'))==1
        code=code.replace(bytes.fromhex('55443322'),struct.pack('<I',addr+offset))
        code+=b'\x90'*(offset-len(code))+original
        put(addr,code);prev=w.DWORD();check(protect(hp,addr,4096,0x20,c.byref(prev)));check(flush(hp,addr,len(code)))
        hook=b'\xe9'+struct.pack('<i',addr-(entry+5));patch(entry,original[:5],hook)
        state['vec3']={'entry':entry,'code':addr,'hook':hook.hex(),'original_prefix':original[:5].hex()}
        statefile.write_text(json.dumps(state,indent=2));print(json.dumps(state['vec3']))
    elif action=='install':
        mods=(w.HMODULE*256)();needed=w.DWORD()
        check(bind(p,'EnumProcessModules',w.BOOL,[w.HANDLE,c.c_void_p,w.DWORD,c.POINTER(w.DWORD)])(hp,mods,c.sizeof(mods),c.byref(needed)))
        filename=bind(p,'GetModuleFileNameExW',w.DWORD,[w.HANDLE,w.HMODULE,w.LPWSTR,w.DWORD]);base=None
        for hm in mods[:needed.value//4]:
            name=c.create_unicode_buffer(1024);filename(hp,hm,name,len(name))
            if name.value.split('\\')[-1].lower()=='d3dimm.dll':base=hm
        assert base,'D3DImm is not loaded'
        original=(lab/'inverse-original.bin').read_bytes();entry=base+0x6e9b
        assert get(entry,len(original))==original,'Renderer version or code does not match the validated routine'
        va=bind(k,'VirtualAllocEx',c.c_void_p,[w.HANDLE,c.c_void_p,c.c_size_t,w.DWORD,w.DWORD])
        dataaddr=va(hp,None,16+136*4096,0x3000,4);codeaddr=va(hp,None,4096,0x3000,4);check(dataaddr and codeaddr)
        code=bytearray((lab/'inverse-cache.bin').read_bytes());origoffset=(len(code)+15)//16*16
        for r in json.loads((lab/'inverse-cache-relocations.json').read_text()):
            value=dataaddr if r['target']=='data' else codeaddr+origoffset
            struct.pack_into('<I',code,r['offset'],value+r['addend'])
        code.extend(b'\x90'*(origoffset-len(code)));code.extend(original);assert len(code)<=4096
        put(codeaddr,bytes(code));previous=w.DWORD();check(protect(hp,codeaddr,4096,0x20,c.byref(previous)));check(flush(hp,codeaddr,len(code)))
        hook=b'\xe9'+struct.pack('<i',codeaddr-(entry+5))
        patch(entry,original[:5],hook)
        state={'pid':pid.value,'entry':entry,'code':codeaddr,'data':dataaddr,'hook':hook.hex(),'original_prefix':original[:5].hex(),'installed_at':time.time()}
        statefile.write_text(json.dumps(state,indent=2));print(json.dumps(state))
    else:raise ValueError(action)
finally:close(hp)
