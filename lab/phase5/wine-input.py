"""Drive only the isolated game through its Win32 input API."""
import ctypes as c
from ctypes import wintypes as w
import sys, time, json

u = c.WinDLL('user32', use_last_error=True)
u.FindWindowW.restype = w.HWND
u.FindWindowW.argtypes = [w.LPCWSTR, w.LPCWSTR]
hwnd = u.FindWindowW(None, 'Dungeon Siege')
assert hwnd, 'No Dungeon Siege window in this prefix'
u.SetForegroundWindow(hwnd)

class Mouse(c.Structure):
    _fields_ = [('dx',w.LONG),('dy',w.LONG),('data',w.DWORD),('flags',w.DWORD),('time',w.DWORD),('extra',c.c_size_t)]
class Key(c.Structure):
    _fields_ = [('vk',w.WORD),('scan',w.WORD),('flags',w.DWORD),('time',w.DWORD),('extra',c.c_size_t)]
class Payload(c.Union):
    _fields_ = [('mouse',Mouse),('key',Key)]
class Input(c.Structure):
    _fields_ = [('type',w.DWORD),('payload',Payload)]
u.SendInput.argtypes = [w.UINT,c.POINTER(Input),c.c_int]
u.SendInput.restype = w.UINT
def send(event):
    assert u.SendInput(1,c.byref(event),c.sizeof(event)) == 1, c.get_last_error()

mode = sys.argv[1]
if mode in ('move','click','rightclick'):
    x,y = map(int,sys.argv[2:4])
    pt=w.POINT(x,y);assert u.ClientToScreen(hwnd,c.byref(pt))
    assert u.SetCursorPos(pt.x,pt.y)
    time.sleep(.2)
    if mode in ('click','rightclick'):
        send(Input(0,Payload(mouse=Mouse(0,0,0,8 if mode=="rightclick" else 2,0,0))))
        time.sleep(.12)
        send(Input(0,Payload(mouse=Mouse(0,0,0,16 if mode=="rightclick" else 4,0,0))))
elif mode=='key':
    vk=int(sys.argv[2]);duration=float(sys.argv[3]) if len(sys.argv)>3 else .12
    send(Input(1,Payload(key=Key(vk,0,0,0,0))))
    time.sleep(duration)
    send(Input(1,Payload(key=Key(vk,0,2,0,0))))
elif mode!='inspect':
    raise ValueError(mode)
class CursorInfo(c.Structure):
    _fields_=[('size',w.DWORD),('flags',w.DWORD),('cursor',w.HANDLE),('position',w.POINT)]
ci=CursorInfo();ci.size=c.sizeof(ci);assert u.GetCursorInfo(c.byref(ci))
print(json.dumps({'hwnd':hwnd,'cursor_flags':ci.flags,'cursor':ci.cursor,'position':[ci.position.x,ci.position.y]}))
