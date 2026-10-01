import ctypes as c,json,sys,time
from ctypes import wintypes as w
u=c.WinDLL('user32');u.FindWindowW.restype=w.HWND;u.FindWindowW.argtypes=[w.LPCWSTR,w.LPCWSTR];h=u.FindWindowW(None,'dgVoodoo 2.53 Setup');assert h
u.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.SendMessageW.restype=w.LPARAM
controls=[]
@c.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
def cb(x,p):
 t=c.create_unicode_buffer(512);cl=c.create_unicode_buffer(100);u.GetWindowTextW(x,t,512);u.GetClassNameW(x,cl,100)
 if u.IsWindowVisible(x):
  r=w.RECT();u.GetWindowRect(x,c.byref(r));row=dict(hwnd=x,id=u.GetDlgCtrlID(x),text=t.value,cls=cl.value,rect=[r.left,r.top,r.right,r.bottom])
  if cl.value=='Button':row['checked']=u.SendMessageW(x,0xf0,0,0)
  if cl.value=='ComboBox':
   row['selected']=u.SendMessageW(x,0x147,0,0);row['items']=[]
   for i in range(u.SendMessageW(x,0x146,0,0)):
    b=c.create_unicode_buffer(1024);u.SendMessageW(x,0x148,i,c.addressof(b));row['items'].append(b.value)
  controls.append(row)
 return True
if len(sys.argv)>1:
 x=int(sys.argv[2]);mode=sys.argv[1]
 if mode=='click':u.SendMessageW(x,0xf5,0,0)
 elif mode=='select':
  u.SendMessageW(x,0x14e,int(sys.argv[3]),0);u.SendMessageW(u.GetParent(x),0x111,u.GetDlgCtrlID(x)|(1<<16),x)
 time.sleep(.2)
u.EnumChildWindows(h,cb,0);print(json.dumps(controls,indent=2))
