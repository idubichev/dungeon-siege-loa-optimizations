from pathlib import Path
import sys,subprocess,time
r=Path.home()/'Documents/Dungeon Siege 1/experiments/2026-09-06';sys.path.insert(0,str(r/'phase5'));import lab
out=Path(__file__).parent
if sys.argv[1]=='prod':
 c=Path.home()/'Applications/Dungeon Siege Wine10 Test.app/Contents'
 lab.wine=str(c/'SharedSupport/wine/bin/wine64');lab.env['WINEPREFIX']=str(c/'SharedSupport/prefix');lab.env['DYLD_FALLBACK_LIBRARY_PATH']=str(c/'Frameworks')
if sys.argv[2]=='capture':lab.focus();time.sleep(.3);lab.capture(out/sys.argv[3])
else:
 lab.input(*sys.argv[2:]);time.sleep(.3);lab.capture(out/'latest.png')
