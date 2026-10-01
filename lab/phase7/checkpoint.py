"""Measure the active private travel run without restarting or suspending it."""
from pathlib import Path
import json, subprocess, sys, time
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'phase5'))
import lab

out = Path(__file__).resolve().parent / 'travel' / sys.argv[1]
out.mkdir(exist_ok=True)
lab.capture(out / 'before.png')
pid = lab.window()['kCGWindowOwnerPID']
memory = subprocess.check_output(['ps', '-p', str(pid), '-o', 'pid=,rss=,%cpu=,etime='], text=True)
(out / 'memory.txt').write_text(memory)
build = lab.lab / 'phase6/14-bounds-clock'
with (out / 'reader.log').open('w') as log:
    proc = subprocess.Popen([lab.wine, lab.python, lab.win(lab.p / 'read-frame-clock.py'),
                             lab.win(out / 'frame-clock.json'), '10', str(build)],
                            env=lab.env, stdout=log, stderr=subprocess.STDOUT)
    for i in range(2):
        time.sleep(5)
        lab.capture(out / f'active-{i}.png')
    assert proc.wait(timeout=10) == 0, (out / 'reader.log').read_text()
result = json.loads((out / 'frame-clock.json').read_text())
print(memory.strip())
print(json.dumps({k: v for k, v in result.items() if k != 'frame_ms'}, indent=2))
subprocess.run([lab.wine, lab.python, lab.win(Path(__file__).with_name('read-scene.py')),
                lab.win(out / 'scene.json')], env=lab.env, check=True)
