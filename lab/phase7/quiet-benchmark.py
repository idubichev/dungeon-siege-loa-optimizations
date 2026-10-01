"""Cold checkpoint test with no screenshots or input during the timing interval."""
from pathlib import Path
import sys,time,json,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'phase5'))
import lab
from PIL import Image,ImageChops,ImageStat
build=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();duration=float(sys.argv[3])
rotate=len(sys.argv)>4 and sys.argv[4]=='rotate'
lab.start(build/'DSLOA.exe',out)
try:
    ref=Image.open(lab.lab/'phase4/11-baseline-repeat/after.png').convert('RGB').crop((530,758,1070,868))
    for _ in range(30):
        lab.capture(out/'menu.png')
        current=Image.open(out/'menu.png').convert('RGB').crop((530,758,1070,868))
        if sum(ImageStat.Stat(ImageChops.difference(current,ref)).mean)/3<10:break
        time.sleep(.5)
    else:raise RuntimeError('Continue not confirmed')
    time.sleep(1);lab.input('click',400,378);time.sleep(7)
    lab.capture(out/'before.png');lab.focus()
    pid=lab.window()['kCGWindowOwnerPID']
    (out/'memory.txt').write_text(subprocess.check_output(['ps','-p',str(pid),'-o','pid=,rss=,%cpu=,etime='],text=True))
    with (out/'reader.log').open('w') as log:
        reader=subprocess.Popen([lab.wine,lab.python,lab.win(lab.p/'read-frame-clock.py'),lab.win(out/'frame-clock.json'),str(duration),str(build)],env=lab.env,stdout=log,stderr=subprocess.STDOUT)
        mover=None
        if rotate:
            mover=subprocess.Popen([lab.wine,lab.python,lab.win(lab.p/'wine-input.py'),'key','37',str(duration)],env=lab.env,stdout=log,stderr=subprocess.STDOUT)
        assert reader.wait(timeout=duration+15)==0
        if mover:assert mover.wait(timeout=10)==0
    lab.capture(out/'after.png')
    subprocess.run([lab.wine,lab.python,lab.win(Path(__file__).with_name('read-scene.py')),lab.win(out/'scene.json')],env=lab.env,check=True)
    r=json.loads((out/'frame-clock.json').read_text())
    print(json.dumps({k:v for k,v in r.items() if k!='frame_ms'},indent=2))
finally:lab.stop()
