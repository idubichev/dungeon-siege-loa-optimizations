"""Run one fixed-duration test from the private save, then stop its Wine prefix."""
from pathlib import Path
import subprocess,time,json,sys,shutil,os
from PIL import Image,ImageChops,ImageStat
p=Path(__file__).parent;lab=p.parent;contents=Path.home()/'Applications/Dungeon Siege Profile Test.app/Contents';prefix=contents/'SharedSupport/prefix';env=os.environ.copy();env.update(WINEPREFIX=str(prefix),DYLD_FALLBACK_LIBRARY_PATH=str(contents/'Frameworks'))
exe=Path(sys.argv[1]);out=p/sys.argv[2];out.mkdir(exist_ok=True);rotation=int(sys.argv[3]) if len(sys.argv)>3 else 0
clock_build=sys.argv[4] if len(sys.argv)>4 else None
stop=[str(contents/'SharedSupport/wine/bin/wineserver'),'-k']
subprocess.run(stop,env=env,check=False)
shutil.copy2(exe,prefix/'drive_c/GOG Games/Dungeon Siege/DSLOA.exe')
def ui(script,*args):subprocess.run(['open','-na','/Applications/Ghostty.app','--args','-e',str(script),*map(str,args)],check=True)
log=(out/'launch.log').open('w');proc=subprocess.Popen([str(lab/'phase3/launch-profile.sh'),'1','1'],stdout=log,stderr=subprocess.STDOUT)
try:
 for _ in range(80):
  windows=[json.loads(x) for x in subprocess.check_output([str(lab/'windows')],text=True).splitlines()]
  if windows:break
  if proc.poll() is not None:raise RuntimeError('Game exited during launch')
  time.sleep(.25)
 else:raise RuntimeError('No game window')
 wid=windows[0]['kCGWindowNumber']
 for _ in range(25):
  subprocess.run(['screencapture','-x','-o','-l',str(wid),str(out/'menu.png')],check=True)
  crop=(530,758,1070,868)
  actual=Image.open(out/'menu.png').convert('RGB').crop(crop)
  reference=Image.open(p/'11-baseline-repeat/after.png').convert('RGB').crop(crop)
  error=sum(ImageStat.Stat(ImageChops.difference(actual,reference)).mean)/3
  if error<10:break
  time.sleep(.5)
 else:raise RuntimeError('Continue menu not confirmed')
 time.sleep(1)
 ui(p/'game-input-debug.sh','m:404,444','w:400','c:404,444')
 time.sleep(7)
 ui(p/'game-key.sh',53,120);time.sleep(2)
 subprocess.run(['screencapture','-x','-o','-l',str(wid),str(out/'paused.png')],check=True)
 print('Paused profile game for UI checks. PID',proc.pid,'window',wid,flush=True)
 proc.wait()
except BaseException:
 subprocess.run(stop,env=env,check=False)
 raise
