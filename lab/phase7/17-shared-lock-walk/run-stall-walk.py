from pathlib import Path
import sys,time,subprocess,shutil,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'phase5'));import lab
p=Path(__file__).resolve().parent;out=(p/sys.argv[1]).resolve();out.mkdir(exist_ok=True)
shutil.copy2(p/'09-stall-log/manifest.json',out/'manifest.json')
lab.start(p/'09-stall-log/DSLOA.exe',out);time.sleep(5);lab.input('click',400,378);time.sleep(7)
subprocess.run([lab.wine,lab.python,lab.win(p/'attach-dg-locks.py'),lab.win(out/'lock-hooks.json')],env=lab.env,check=True)
lab.capture(out/'before.png');lab.focus()
with (out/'reader.log').open('w') as log:
 reader=subprocess.Popen([lab.wine,lab.python,lab.win(p/'read-stalls.py'),lab.win(out/'stalls.json'),'35'],env=lab.env,stdout=log,stderr=subprocess.STDOUT)
 walker=subprocess.Popen([lab.wine,lab.python,lab.win(p/'walk-win32.py')],env=lab.env,stdout=log,stderr=subprocess.STDOUT)
 walker.wait(timeout=45);reader.wait(timeout=15)
lab.capture(out/'after.png')
d=json.loads((out/'stalls.json').read_text());print(json.dumps({'lost':d['lost_to_wrap'],'summary':d['summary'],'main_stalls':[e for e in d['stalls']if e['thread']==d['events'][next(i for i,e in enumerate(d['events'])if e['function']=='render')]['thread']]},indent=2))
