import ctypes as c,struct,json
from pathlib import Path
p=Path(__file__).parent;k=c.WinDLL('kernel32');k.VirtualAlloc.restype=c.c_void_p;k.VirtualAlloc.argtypes=[c.c_void_p,c.c_size_t,c.c_ulong,c.c_ulong]
def alloc(b):
 a=k.VirtualAlloc(None,4096,0x3000,0x40);assert a;c.memmove(a,b,len(b));return a
code=alloc((p/'patch-thread.bin').read_bytes());target=alloc(bytes.fromhex('b82a000000c3'));data=alloc(b'');fn=c.CFUNCTYPE(c.c_uint)(target)
names=['OpenThread','SuspendThread','ResumeThread','GetThreadContext','Sleep','CloseHandle','VirtualProtect','FlushInstructionCache'];ptrs=[c.cast(getattr(k,n),c.c_void_p).value for n in names]
k.CreateThread.restype=c.c_void_p;k.CreateThread.argtypes=[c.c_void_p,c.c_size_t,c.c_void_p,c.c_void_p,c.c_ulong,c.c_void_p]
k.WaitForSingleObject.argtypes=[c.c_void_p,c.c_ulong];k.CloseHandle.argtypes=[c.c_void_p]
for i in range(100):
 old=42+(i%2);new=43-(i%2);expected=b'\xb8'+struct.pack('<I',old);replacement=b'\xb8'+struct.pack('<I',new)
 b=struct.pack('<12I',k.GetCurrentThreadId(),target,5,99,*ptrs)+expected.ljust(32,b'\0')+replacement.ljust(32,b'\0');c.memmove(data,b,len(b))
 h=k.CreateThread(None,0,code,data,0,None);assert h;assert k.WaitForSingleObject(h,5000)==0;k.CloseHandle(h)
 result=struct.unpack('<I',c.string_at(data+12,4))[0];assert result==0 and fn()==new,(i,result,fn())
print(json.dumps({'safe_patch_round_trips':100,'context':'in process control and integer only','value':fn()}));(p/'patch-thread-validation.json').write_text(json.dumps({'safe_patch_round_trips':100,'expected_value':42,'actual_value':fn()}))
