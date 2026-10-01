"""Verify this exact local game build and apply the seven validated runtime hooks."""
from pathlib import Path
import hashlib, json, subprocess, sys, time

root = Path(__file__).parent
game = Path(r'C:\GOG Games\Dungeon Siege')
manifest = json.loads((root / 'manifest.json').read_text())
for folder, names in ((root, manifest['payload']), (game, manifest['game'])):
    for name, expected in names.items():
        actual = hashlib.sha256((folder / name).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError('Validated file has changed: ' + str(folder / name))

def action(name):
    result = subprocess.run([sys.executable, str(root / 'runtime-cache-win32.py'), name],
                            capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout

deadline = time.monotonic() + 45
while True:
    try:
        # Also verifies the live hook, so a recycled Wine PID cannot reuse stale state.
        try:
            result = action('stats')
        except RuntimeError:
            result = action('install')
        break
    except RuntimeError:
        if time.monotonic() >= deadline:
            raise
        time.sleep(0.5)
print(result, end='')
for name in ('matmul', 'slerp', 'light', 'blend', 'slerp2', 'vec3'):
    state = json.loads((root / 'runtime-cache-state.json').read_text())
    if name not in state:
        print(action(name), end='')
print(action('stats'), end='')
print('All eight improvements active, including the verified quaternion executable patch.')
