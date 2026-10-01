import ctypes as c,json
from ctypes import wintypes as w
u=c.WinDLL('user32');u.FindWindowW.argtypes=[w.LPCWSTR,w.LPCWSTR];u.FindWindowW.restype=w.HWND
h=u.FindWindowW(None,'Dungeon Siege');assert h
r=w.RECT();u.GetClientRect(h,c.byref(r));print(json.dumps({'client':[r.left,r.top,r.right,r.bottom],'desktop':[u.GetSystemMetrics(0),u.GetSystemMetrics(1)]}))
