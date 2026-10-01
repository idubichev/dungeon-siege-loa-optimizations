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
    manifest=json.loads((build/'manifest.json').read_text())
    reader='read-frame-clock.py' if 'slots' in manifest else 'read-function-timer.py'
    script=lab.p/reader if reader=='read-frame-clock.py' else lab.lab/'phase4'/reader
    result='frame-clock.json' if reader=='read-frame-clock.py' else 'function-timing.json'
    with (out/'reader.log').open('w') as log:
        proc=subprocess.Popen([lab.wine,lab.python,lab.win(script),lab.win(out/result),str(duration),str(build)],env=lab.env,stdout=log,stderr=subprocess.STDOUT)
        for i in range(5):
            time.sleep(duration/5)
            lab.capture(out/f'{i+1}.png')
        assert proc.wait(timeout=10)==0,(out/'reader.log').read_text()
    lab.capture(out/'after.png',True)
    summary=json.loads((out/result).read_text())
    print(json.dumps({k:v for k,v in summary.items() if k not in ('frame_ms','before','after')},indent=2))
finally:lab.stop()
