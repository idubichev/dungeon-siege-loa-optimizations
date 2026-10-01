from pathlib import Path
import sys,time,json,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'phase5'));import lab
p=Path(__file__).resolve().parent;build=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(exist_ok=True)
lab.start(build/'DSLOA.exe',out)
try:
 time.sleep(5);lab.input('click',400,378);time.sleep(7);lab.capture(out/'before.png');lab.focus()
 with (out/'reader.log').open('w')as log:
  reader=subprocess.Popen([lab.wine,lab.python,lab.win(lab.p/'read-frame-clock.py'),lab.win(out/'frame-clock.json'),'35',str(build)],env=lab.env,stdout=log,stderr=subprocess.STDOUT)
  walker=subprocess.Popen([lab.wine,lab.python,lab.win(p/'walk-win32.py')],env=lab.env,stdout=log,stderr=subprocess.STDOUT)
  assert walker.wait(timeout=45)==0;assert reader.wait(timeout=40)==0
 lab.capture(out/'after.png');pid=lab.window()['kCGWindowOwnerPID'];(out/'memory.txt').write_text(subprocess.check_output(['ps','-p',str(pid),'-o','pid=,rss=,%cpu=,etime='],text=True))
 d=json.loads((out/'frame-clock.json').read_text());result={k:v for k,v in d.items()if k!='frame_ms'};result['over_80ms']=sum(x>80 for x in d['frame_ms']);result['over_40ms']=sum(x>40 for x in d['frame_ms']);print(json.dumps(result,indent=2),flush=True)
finally:lab.stop()
