"""Reuse the verified cursor hook/linker and hardened triangle builder."""
from pathlib import Path
p=Path(__file__).resolve().parent
p4=p.parent/'phase4'
cursor=(p4/'build-cursor-colors.py').read_text()
cursor=cursor.replace("p.parent/'phase4/04-cursor-colors'", "p.parent/'phase5/07-native-arrow'")
cursor=cursor.replace("p.parent/'phase4/native-cursor-colors.c'", "p.parent/'phase5/native-arrow.c'")
cursor=cursor.replace('40+64*28+8192','40')
cursor=cursor.replace("m['limitations']=['Cursor images treated as immutable; cache key includes image, pixels, dimensions and hotspot.','Up to 64 native cursor handles; unsupported images or allocation failures use original software cursor.','Cursor handles remain owned by the game until process exit.','Timing DLL is separate, experimental and not part of this EXE.']",
"m['limitations']=['Standard native arrow replaces game cursor artwork. Original software rendering is retained on API initialization failure.']")
exec(compile(cursor,str(p4/'build-cursor-colors.py'),'exec'),{'__file__':str(p4/'build-cursor-colors.py')})
triangle=(p4/'build-triangle-safe.py').read_text()
triangle=triangle.replace("p/'04-cursor-colors/DSLOA.exe'", "p.parent/'phase5/07-native-arrow/DSLOA.exe'")
triangle=triangle.replace("out=p/'24-triangle-safe'", "out=p.parent/'phase5/08-arrow-triangle'")
exec(compile(triangle,str(p4/'build-triangle-safe.py'),'exec'),{'__file__':str(p4/'build-triangle-safe.py')})
