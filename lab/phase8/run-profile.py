"""Fresh checkpoint, coarse wall-time attribution or native stack sample."""
from pathlib import Path
import sys,time,json,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'phase5'))
import lab
from PIL import Image,ImageChops,ImageStat
mode=sys.argv[1];out=Path(sys.argv[2]).resolve()
build=lab.lab/('phase8/02-coarse-timer' if mode=='coarse' else 'phase7/22-native-fastpath')
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
 with (out/'profiler.log').open('w') as log:
  if mode=='coarse':
   subprocess.run([lab.wine,lab.python,lab.win(lab.lab/'phase4/read-function-timer.py'),lab.win(out/'timing.json'),'15',str(build)],env=lab.env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=40)
  else:
   subprocess.run(['/usr/bin/sample',str(pid),'15','5','-file',str(out/'sample.txt')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=45)
 lab.capture(out/'after.png')
 (out/'memory-after.txt').write_text(subprocess.check_output(['ps','-p',str(pid),'-o','pid=,rss=,%cpu=,etime='],text=True))
 print('Finished',mode,flush=True)
finally:lab.stop()
