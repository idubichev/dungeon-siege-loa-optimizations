"""One persistent input process for the private, invincible travel checkpoint."""
from pathlib import Path
root=Path(__file__).resolve().parent
exec((root.parent/'phase5/wine-input.py').read_text().split('mode =')[0])
points=[(410,295)]*7+[(570,320),(550,285),(510,280),(465,280),(435,280)]
for x,y in points:
    pt=w.POINT(x,y);assert u.ClientToScreen(hwnd,c.byref(pt));assert u.SetCursorPos(pt.x,pt.y)
    time.sleep(.15)
    send(Input(0,Payload(mouse=Mouse(0,0,0,2,0,0))))
    time.sleep(.08)
    send(Input(0,Payload(mouse=Mouse(0,0,0,4,0,0))))
    time.sleep(2.5)
