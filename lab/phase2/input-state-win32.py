import ctypes as c,json
u=c.WinDLL('user32')
print(json.dumps({hex(k):hex(u.GetAsyncKeyState(k)&65535) for k in [1,2,4,5,6,16,17,18,32,37,38,39,40,91,92]}))
