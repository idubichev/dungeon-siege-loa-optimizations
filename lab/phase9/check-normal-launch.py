from pathlib import Path
import time, subprocess, json, hashlib
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'phase5'))
import lab
from PIL import Image,ImageChops,ImageStat
lab.contents=Path.home()/'Applications/Dungeon Siege Wine10 Test.app/Contents'
lab.prefix=lab.contents/'SharedSupport/prefix'
lab.env.update(WINEPREFIX=str(lab.prefix),DYLD_FALLBACK_LIBRARY_PATH=str(lab.contents/'Frameworks'))
lab.wine=str(lab.contents/'SharedSupport/wine/bin/wine64')
lab.server=str(lab.contents/'SharedSupport/wine/bin/wineserver')
out=Path(__file__).resolve().parent/'23-normal-launch';out.mkdir(exist_ok=True)
subprocess.run(['open','-a',str(Path.home()/'Applications/Dungeon Siege Optimized.app')],check=True)
for _ in range(40):
    time.sleep(.5)
    try:lab.window();break
    except AssertionError:pass
lab.focus()
reference=Image.open(lab.lab/'phase4/11-baseline-repeat/after.png').convert('RGB').crop((530,758,1070,868))
for _ in range(30):
    lab.capture(out/'menu.png')
    current=Image.open(out/'menu.png').convert('RGB').crop((530,758,1070,868))
    if sum(ImageStat.Stat(ImageChops.difference(current,reference)).mean)/3<10:break
    time.sleep(.5)
else:raise RuntimeError('Continue menu not confirmed')
time.sleep(1)
lab.input('click',400,378);time.sleep(7)
for i in range(3):
    time.sleep(2);lab.capture(out/f'{i+1}.png')
lab.capture(out/'active.png',True)
lab.input('key',27);time.sleep(.4);lab.capture(out/'paused.png',True)
subprocess.run([lab.wine,lab.python,lab.win(lab.lab/'phase8/read-transform-interface.py'),lab.win(out/'interface')],env=lab.env,check=True)
for record in json.loads((lab.p/'release-protected-files.json').read_text()):
    assert hashlib.sha256(Path(record['path']).read_bytes()).hexdigest()==record['sha256'],record['path']
(out/'protected-files-check.json').write_text(json.dumps({'checked':5,'unchanged':True},indent=2)+'\n')
op=Path.home()/'Library/Application Support/Dungeon Siege Optimized/user-data/Dungeon Siege LOA/Save/Test OP.dssave'
assert hashlib.sha256(op.read_bytes()).hexdigest()=='0f282b8468e8fed5c54d99df15bb429449d8b637fcc0c2ab92e8f702713a9737'
print('Normal launcher loaded Test OP. Paused for handoff; protected files and OP save unchanged.')
