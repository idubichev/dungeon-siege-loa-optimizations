from pathlib import Path
p=Path(__file__).resolve().parent
source=p.parent/'phase4/build-clock-profile.py'
s=source.read_text().replace("p/'12-triangle/DSLOA.exe'","p.parent/'phase5/08-arrow-triangle/DSLOA.exe'")
s=s.replace("out=p/'22-clock-profile'","out=p.parent/'phase5/13-draw-profile'")
functions=[('render_pass',0x676a6c,0,0),('skinning',0x69f008,8,0),
           ('draw',0x67901a,4,0),('translation_matrix',0x65fd3b,4,0),
           ('rotation_matrix',0x65fd97,4,0),('scale_matrix',0x65fe08,4,0),
           ('transpose_matrix',0x4f582b,4,0),('squared_length',0x43e8c3,0,0),
           ('ray_trace',0x69395c,16,0),('vertical_trace',0x693c45,16,0)]
lines=s.splitlines()
lines=[('functions='+repr(functions)) if line.startswith('functions=') else line for line in lines]
exec(compile('\n'.join(lines),str(source),'exec'),{'__file__':str(source)})
