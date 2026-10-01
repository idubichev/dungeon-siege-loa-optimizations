import ctypes as c,time
u=c.WinDLL("user32")
h=u.FindWindowW(None,"Dungeon Siege")
print("hwnd",h,"iconic",u.IsIconic(h),"visible",u.IsWindowVisible(h))
u.ShowWindow(h,9)
u.SetForegroundWindow(h)
time.sleep(1)
print("after",u.IsIconic(h),u.IsWindowVisible(h))
