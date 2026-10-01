from pathlib import Path
import struct,json,hashlib,subprocess
p=Path(__file__).resolve().parent
s=(p.parent/'phase2/build-static-patches.py').read_text();scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
pe=scope['PE'](p/'05-cursor-fixed/DSLOA.exe');pe.packed=False;out=p/'08-slerp';out.mkdir(exist_ok=True)
entry=0x69fa05;old=pe.read(entry,5);assert old[0]==0xe9
fallback=entry+5+struct.unpack_from('<i',old,1)[0]
(out/'shim.s').write_text('.text\n')
subprocess.run(['clang','-target','i686-w64-windows-gnu','-O2','-msse2','-mfpmath=sse','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-asynchronous-unwind-tables','-ffp-contract=off','-fno-vectorize','-fno-slp-vectorize','-c',str(p/'slerp-fast.c'),'-o',str(out/'slerp.obj')],check=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(out/'shim.s'),'-o',str(out/'shim.obj')],check=True)
globals={'_original_slerp':fallback};reference=(p.parent/'phase4/coff-reference.py').read_text();fragment=reference[reference.index('objects=[];globals='):reference.index('state=pe.data_alloc')].replace("objects=[];globals={'_alpha_resume':0x6633b7,'_wm_resume':0x41527b}",'objects=[]').replace("out/'cursor.obj'","out/'slerp.obj'")
exec(fragment)
pe.hook(entry,old,globals['_slerp_fast'],'slerp-sse2');m=pe.finish(out/'DSLOA.exe');m['symbols']=globals
(out/'manifest.json').write_text(json.dumps(m,indent=2));print(m)
