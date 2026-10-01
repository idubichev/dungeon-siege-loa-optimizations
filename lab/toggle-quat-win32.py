"""Same-process benchmark toggle; touches only the already verified five-byte hook."""
from pathlib import Path
manager=Path(r'Z:\Users\you\Library\Application Support\Dungeon Siege Optimized\runtime-cache-win32.py')
exec(manager.read_text().split('\ntry:\n    action=')[0])
try:
 entry=0x535f3b
 fast=b'\xe9'+struct.pack('<i',0xaad0a0-(entry+5))
 original=(Path(__file__).parent/'quat-original.bin').read_bytes()[:5]
 if sys.argv[1]=='off':patch(entry,fast,original)
 elif sys.argv[1]=='on':patch(entry,original,fast)
 else:raise ValueError(sys.argv[1])
 print('Quaternion patch',sys.argv[1],flush=True)
finally:close(hp)
