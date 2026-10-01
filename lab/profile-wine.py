import os,subprocess,time,re,collections
from pathlib import Path
lab=Path(__file__).parent
root=Path('~/Applications/Dungeon Siege Wine10 Test.app/Contents')
env=dict(os.environ,WINEPREFIX=str(root/'SharedSupport/prefix'),DYLD_FALLBACK_LIBRARY_PATH=str(root/'Frameworks'),WINEESYNC='1',WINEMSYNC='1',WINEDEBUG='-all',MVK_CONFIG_LOG_LEVEL='0')
for i in range(12):
 r=subprocess.run([str(root/'SharedSupport/wine/bin/wine64'),'winedbg','0xc8'],input='thread 0xcc\nbt\ninfo registers\ndetach\nquit\n',text=True,capture_output=True,env=env,timeout=15)
 (lab/f'profile-{i+1:02}.txt').write_text(r.stdout+r.stderr)
 traces=re.findall(r'Backtrace:\n(.*?)(?=Wine-dbg>|Register dump:)',r.stdout,re.S)
 print(i+1,traces[-1].splitlines()[0] if traces else 'NO TRACE',flush=True)
 time.sleep(.2)
