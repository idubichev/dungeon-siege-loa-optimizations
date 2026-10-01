from PIL import Image, ImageOps, ImageFilter
from pathlib import Path
import subprocess,sys
for path in sys.argv[1:]:
 p=Path(path); im=Image.open(p).convert('RGB').crop((132,79,234,112))
 mask=Image.new('L',im.size)
 mask.putdata([0 if min(rgb)>215 else 255 for rgb in im.getdata()])
 mask=ImageOps.expand(mask,10,fill=255).resize((488,212),Image.Resampling.NEAREST)
 out=p.with_name(p.stem+'-number.png'); mask.save(out)
 v=subprocess.check_output(['tesseract',str(out),'stdout','--psm','7','-c','tessedit_char_whitelist=0123456789.'],stderr=subprocess.DEVNULL,text=True).strip()
 print(p.name,v)
