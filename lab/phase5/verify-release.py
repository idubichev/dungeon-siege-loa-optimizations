"""Cold-load the fixed private save; capture active gameplay; stop immediately."""
import sys,time,json,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import lab

build=Path(sys.argv[1]).resolve();out=lab.p/sys.argv[2]
rotation=float(sys.argv[3]) if len(sys.argv)>3 else .65
duration=float(sys.argv[4]) if len(sys.argv)>4 else 10
lab.start(build/'DSLOA.exe',out)
try:
    reference=Image.open(lab.lab/'phase4/11-baseline-repeat/after.png').convert('RGB').crop((530,758,1070,868))
    for _ in range(30):
        lab.capture(out/'menu.png')
        current=Image.open(out/'menu.png').convert('RGB').crop((530,758,1070,868))
        if sum(ImageStat.Stat(ImageChops.difference(current,reference)).mean)/3<10:break
        time.sleep(.5)
    else:raise RuntimeError('Continue menu not confirmed')
    time.sleep(1)
    lab.input('click',400,378)
    time.sleep(7)
    if rotation:lab.input('key',37,rotation);time.sleep(1.5)
    lab.capture(out/'before.png')
    for i in range(5):
        time.sleep(2)
        lab.capture(out/f'{i+1}.png')
    lab.capture(out/'after.png',True)
    lab.input('key',27)
    time.sleep(.5)
    lab.capture(out/'paused.png',True)
    print('Uninstrumented gameplay captured; game paused for UI check.')
except:
    lab.stop()
    raise
