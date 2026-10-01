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
 if rotation:
  ui(p/'game-key.sh',123,rotation);time.sleep(rotation/1000+1.5)
 wid=windows[0]['kCGWindowNumber']
 subprocess.run(['screencapture','-x','-o','-l',str(wid),str(out/'before.png')],check=True)
 clock_process=None
 if clock_build:
  clock_env=env.copy();clock_env.update(WINEESYNC='1',WINEMSYNC='1',WINEDEBUG='-all',MVK_CONFIG_LOG_LEVEL='0')
  reader_name='read-function-timer.py' if 'functions' in json.loads((p/clock_build/'manifest.json').read_text()) else 'read-frame-clock.py'
  capture_name='function-timing.json' if reader_name=='read-function-timer.py' else 'frame-clock.json'
  win=lambda f:'Z:'+str(f).replace('/','\\')
  clock_process=subprocess.Popen([str(contents/'SharedSupport/wine/bin/wine64'),win(Path.home()/'Library/Application Support/Dungeon Siege Optimized/python-win32/pythonw.exe'),win(p/reader_name),win(out/capture_name),'10',clock_build],env=clock_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 subprocess.run([sys.executable,str(lab/'measure.py'),str(out.relative_to(lab))],check=True)
 if clock_process:
  stdout,_=clock_process.communicate(timeout=15);(out/'clock-reader.log').write_text(stdout);assert clock_process.returncode==0,stdout
 subprocess.run(['screencapture','-x','-o','-l',str(wid),str(out/'after.png')],check=True)
 subprocess.run(['screencapture','-C','-x',str(out/'full-desktop.png')],check=True)
 bounds=windows[0]['kCGWindowBounds'];x,y,w,h=[bounds[k] for k in ('X','Y','Width','Height')]
 Image.open(out/'full-desktop.png').crop((2*x,2*y,2*(x+w),2*(y+h))).save(out/'native-cursor.png')
 (out/'full-desktop.png').unlink()
finally:
 subprocess.run(stop,env=env,check=True);proc.wait(timeout=10);log.close()
print('Finished isolated benchmark',out,flush=True)
