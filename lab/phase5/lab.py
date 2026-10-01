"""Test the isolated Profile prefix without temporary terminal windows."""
from pathlib import Path
import json, os, subprocess, sys, time, shutil
from PIL import Image

p=Path(__file__).resolve().parent
lab=p.parent
contents=Path.home()/'Applications/Dungeon Siege Profile Test.app/Contents'
prefix=contents/'SharedSupport/prefix'
env=os.environ.copy()
env.update(WINEPREFIX=str(prefix),DYLD_FALLBACK_LIBRARY_PATH=str(contents/'Frameworks'),
           WINEESYNC='1',WINEMSYNC='1',WINEDEBUG='-all',MVK_CONFIG_LOG_LEVEL='0',
           MVK_CONFIG_FULL_IMAGE_VIEW_SWIZZLE='1')
wine=str(contents/'SharedSupport/wine/bin/wine64')
server=str(contents/'SharedSupport/wine/bin/wineserver')
def win(path): return 'Z:'+str(path).replace('/','\\')
python=win(Path.home()/'Library/Application Support/Dungeon Siege Optimized/python-win32/pythonw.exe')
def window():
    windows=[json.loads(x) for x in subprocess.check_output([str(lab/'windows')],text=True).splitlines()]
    windows=[w for w in windows if w.get('kCGWindowName')=='Dungeon Siege']
    assert len(windows)==1, windows
    return windows[0]
def focus():
    pid=window()['kCGWindowOwnerPID']
    subprocess.run(['osascript','-e',f'tell application "System Events" to set frontmost of first application process whose unix id is {pid} to true'],check=True,timeout=5)
def input(*args):
    focus()
    subprocess.run([wine,python,win(p/'wine-input.py'),*map(str,args)],env=env,check=True,stdout=subprocess.DEVNULL,timeout=10)
def stop():
    subprocess.run([server,'-k'],env=env,check=False,timeout=10)
    subprocess.run([server,'-w'],env=env,check=True,timeout=10)
def capture(name,cursor=False):
    w=window();dest=Path(name)
    if not dest.is_absolute():dest=p/dest
    dest.parent.mkdir(exist_ok=True)
    if cursor:
        focus();time.sleep(.15)
        tmp=dest.with_suffix('.desktop.png')
        subprocess.run(['screencapture','-C','-x',str(tmp)],check=True)
        b=w['kCGWindowBounds'];x,y,width,height=[b[k] for k in ('X','Y','Width','Height')]
        Image.open(tmp).crop((2*x,2*y,2*(x+width),2*(y+height))).save(dest)
        tmp.unlink()
    else:
        subprocess.run(['screencapture','-x','-o','-l',str(w['kCGWindowNumber']),str(dest)],check=True)
def start(exe,out,fix=False):
    stop();out=Path(out);out.mkdir(exist_ok=True)
    documents=prefix/'drive_c/users/Wineskin/Documents'
    if not documents.exists():
        documents.symlink_to(contents/'SharedSupport/profile-user-data',target_is_directory=True)
    shutil.copy2(exe,prefix/'drive_c/GOG Games/Dungeon Siege/DSLOA.exe')
    launch_env=env.copy()
    if fix:launch_env['DYLD_INSERT_LIBRARIES']=str(p/'cursor-focus.dylib')
    with (out/'launch.log').open('w') as log:
        proc=subprocess.Popen([wine,'DSLOA.exe','nointro=true','fullscreen=false','nospacecheck=true','bltonly=true'],
                         cwd=prefix/'drive_c/GOG Games/Dungeon Siege',env=launch_env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    for i in range(40):
        time.sleep(.25)
        if proc.poll() is not None:
            raise RuntimeError(f'Game exited during launch: {proc.returncode}; see {out}/launch.log')
        try:window();break
        except AssertionError:pass
    focus();capture(out/'menu.png')
    print('Started isolated game',window()['kCGWindowOwnerPID'])

if __name__=='__main__':
    command=sys.argv[1]
    if command=='start':start(sys.argv[2],p/sys.argv[3],len(sys.argv)>4 and sys.argv[4]=='fix')
    elif command=='input':input(*sys.argv[2:])
    elif command=='capture':capture(sys.argv[2],len(sys.argv)>3)
    elif command=='stop':stop()
    else:raise ValueError(command)
