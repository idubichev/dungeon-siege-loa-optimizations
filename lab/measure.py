import json,subprocess,sys,time,statistics,re
from pathlib import Path
lab=Path(__file__).parent
name=sys.argv[1]
windows=[json.loads(s) for s in subprocess.check_output([str(lab/'windows')],text=True).splitlines()]
game=[w for w in windows if w.get('kCGWindowName')=='Dungeon Siege']
assert len(game)==1
w=game[0]; pid=w['kCGWindowOwnerPID'];wid=w['kCGWindowNumber']
subprocess.run(['osascript','-e',f'tell application "System Events" to set frontmost of first application process whose unix id is {pid} to true'],check=True,capture_output=True)
folder=lab/name;folder.mkdir(exist_ok=True)
values=[]
for i in range(5):
 time.sleep(2)
 p=folder/f'{i+1}.png';crop=folder/f'{i+1}-fps.png'
 subprocess.run(['screencapture','-x','-o','-l',str(wid),str(p)],check=True)
 subprocess.run(['sips','-c','38','160','--cropOffset','78','125',str(p),'--out',str(crop)],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['sips','-z','152','640',str(crop)],check=True,stdout=subprocess.DEVNULL)
 s=subprocess.check_output(['tesseract',str(crop),'stdout','--psm','7','-c','tessedit_char_whitelist=0123456789.'],stderr=subprocess.DEVNULL,text=True).strip()
 if re.fullmatch(r'\d{1,3}\.\d',s):values.append(float(s))
 print(i+1,s,flush=True)
result={'name':name,'window':w,'fps_samples':values,'mean':statistics.mean(values) if values else None,'min':min(values) if values else None,'max':max(values) if values else None,'note':'Five readings of the displayed DXVK FPS HUD, two seconds apart; this is not a frametime capture.'}
(folder/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
