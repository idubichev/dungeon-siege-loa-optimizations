from pathlib import Path
import struct,json,hashlib,subprocess
p=Path(__file__).parent
s=(p.parent/'phase2/build-static-patches.py').read_text();scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
pe=scope['PE'](p/'29-cursor-refresh/DSLOA.exe');pe.packed=False;out=p/'30-triangle-refresh';out.mkdir(exist_ok=True)
original=bytes.fromhex('558bec81eca8000000');assert pe.read(0x728343,9)==original
(out/'shim.s').write_text('.intel_syntax noprefix\n.text\n.global _original_triangle\n_original_triangle:\n.byte '+','.join(hex(x) for x in original)+'\njmp _resume\n')
subprocess.run(['clang','-target','i686-w64-windows-gnu','-O2','-msse2','-mfpmath=sse','-ffreestanding','-fno-builtin','-fno-stack-protector','-ffp-contract=off','-frounding-math','-fno-vectorize','-fno-slp-vectorize','-c',str(p/'triangle-safe.c'),'-o',str(out/'triangle.obj')],check=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(out/'shim.s'),'-o',str(out/'shim.obj')],check=True)
globals={'_resume':0x72834c}
reference=(p/'coff-reference.py').read_text();fragment=reference[reference.index('objects=[];globals='):reference.index('state=pe.data_alloc')]
fragment=fragment.replace("objects=[];globals={'_alpha_resume':0x6633b7,'_wm_resume':0x41527b}",'objects=[]').replace("out/'cursor.obj'","out/'triangle.obj'")
exec(fragment)
pe.hook(0x728343,original,globals['_triangle_fast'],'triangle-sse-fast-path')
m=pe.finish(out/'DSLOA.exe');m['symbols']=globals;(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
