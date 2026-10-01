"""Coarse diagnostic only, derived from the current installed release."""
from pathlib import Path
p=Path(__file__).resolve().parent
source=p.parent/'phase4/build-function-timer.py'
s=source.read_text().replace("p3/'16-native-cursor/DSLOA.exe'","p.parent/'phase7/22-native-fastpath/DSLOA.exe'")
s=s.replace("out=p/('01-function-timer' if level=='coarse' else '02-render-timer')","out=p.parent/'phase8/02-coarse-timer'")
functions=[('render_pass',0x676a6c,0,0),('object_draw',0x678315,4,0),('skinning',0x69f008,8,0),('lighting',0x6a0d02,8,0),('draw',0x67901a,4,0),('game_update',0x477118,16,0)]
s='\n'.join('functions='+repr(functions) if line.startswith('functions=') else line for line in s.splitlines())
# Preserve the floating point environment and Win32 LastError around diagnostics.
s=s.replace("'pushfd','pushad'","'pushfd','pushad','mov ebx,esp','sub esp,528','and esp,-16','fxsave [esp]','mov edi,dword ptr fs:[0x34]'")
s=s.replace("'popad','popfd'","'mov dword ptr fs:[0x34],edi','fxrstor [esp]','mov esp,ebx','popad','popfd'")
exec(compile(s,str(source),'exec'),{'__file__':str(source)})
