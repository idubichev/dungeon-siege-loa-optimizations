"""Fresh checkpoint, coarse wall-time attribution or native stack sample."""
from pathlib import Path
import sys,time,json,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'phase5'))
import lab
from PIL import Image,ImageChops,ImageStat
mode=sys.argv[1];out=Path(sys.argv[2]).resolve()
build=lab.lab/'phase9/02-transform-probe'
lab.start(build/'DSLOA.exe',out)
try:
 ref=Image.open(lab.lab/'phase4/11-baseline-repeat/after.png').convert('RGB').crop((530,758,1070,868))
 for _ in range(30):
  lab.capture(out/'menu.png');cur=Image.open(out/'menu.png').convert('RGB').crop((530,758,1070,868))
  if sum(ImageStat.Stat(ImageChops.difference(cur,ref)).mean)/3<10:break
  time.sleep(.5)
 else:raise RuntimeError('Continue not confirmed')
 time.sleep(1);lab.input('click',400,378);time.sleep(7);lab.capture(out/'before.png');lab.focus()
 pid=lab.window()['kCGWindowOwnerPID']
 (out/'memory-before.txt').write_text(subprocess.check_output(['ps','-p',str(pid),'-o','pid=,rss=,%cpu=,etime='],text=True))
 time.sleep(12);lab.input('key',27);time.sleep(.3)
 subprocess.run([lab.wine,lab.python,lab.win(lab.lab/'phase9/read-transform-probe.py'),lab.win(out/'probe.json')],env=lab.env,check=True)
 lab.capture(out/'after.png')
 (out/'memory-after.txt').write_text(subprocess.check_output(['ps','-p',str(pid),'-o','pid=,rss=,%cpu=,etime='],text=True))
 print('Finished',mode,flush=True)
finally:lab.stop()
