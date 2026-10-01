from pathlib import Path
import struct,json,hashlib,subprocess,capstone,sys
p=Path(__file__).resolve().parent
s=(p.parent/'phase2/build-static-patches.py').read_text();scope={'Path':Path,'struct':struct,'json':json,'hashlib':hashlib,'align':lambda v,n:(v+n-1)//n*n}
exec(s[s.index('class PE:'):s.index('def jump(')],scope)
source=p.parent/'phase8/05-normal-scope/DSLOA.exe';pe=scope['PE'](source);pe.packed=False
mode=sys.argv[1] if len(sys.argv)>1 else 'probe'
assert mode in ['probe','batch','simd','cache']
out=p/{'probe':'02-transform-probe','batch':'07-transform-batch','simd':'10-transform-simd','cache':'13-transform-cache'}[mode];out.mkdir(exist_ok=True)
asm='''.intel_syntax noprefix
.text
.global _transform_hook
_transform_hook:
 pushfd
 pushad
 push 0x11223344
 push ebx
 push dword ptr [ebp-0x30]
 call "_probe@12"
 popad
 popfd
 mov eax,dword ptr [ebx+0x98]
 mov [ebp-0x70],eax
 mov [ebp-0x6c],eax
 mov [ebp-0x68],eax
 jmp _resume
'''
if mode in ['simd','cache']:asm=(p/'transform-fallback.s').read_text()
if mode=='cache':asm=asm.replace(' push ebx',' push 0x11223344\n push ebx',1).replace('_apply_transform@8','_apply_cached@12')
(out/'shim.s').write_text(asm)
subprocess.run(['clang++','-std=c++17','-target','i686-w64-windows-gnu','-O2','-msse2','-mfpmath=sse','-ffp-contract=off','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-exceptions','-fno-rtti','-fno-asynchronous-unwind-tables','-c',str(p/('transform-'+mode+'.cpp')),'-o',str(out/'cursor.obj')],check=True)
subprocess.run(['clang','-target','i686-w64-windows-gnu','-c',str(out/'shim.s'),'-o',str(out/'shim.obj')],check=True)
globals={'_translation':0x65fd3b,'_rotation':0x65fd97,'_scale':0x65fe08,'_resume':0x6790ab,'_check_hresult':0x41efc7}
reference=(p.parent/'phase4/coff-reference.py').read_text();fragment=reference[reference.index('objects=[];globals='):reference.index('state=pe.data_alloc')]
fragment=fragment.replace("objects=[];globals={'_alpha_resume':0x6633b7,'_wm_resume':0x41527b}",'objects=[]');exec(fragment)
state_bytes=16+1024*192 if mode=='cache' else 7*4+(16*4+40)*4
state=pe.data_alloc(state_bytes)
if mode!='simd':
 shim=objects[0][1][1];start=shim['pos'];body=pe.code[start:start+shim['size']];off=body.index(bytes.fromhex('44332211'));struct.pack_into('<I',pe.code,start+off,state);pe.absolute(start+off)
expected=pe.read(0x67907e,0x2d)
assert expected.hex()=='8b4dd056e8b46cfeff8b4dd057e8076dfeffd983980000008b4dd0d955908d4590d9559450d95d98e85d6dfeff'
pe.hook(0x67907e,expected,globals['_transform_hook'],'object-transform-'+mode)
m=pe.finish(out/'DSLOA.exe');m.update(source=str(source),state_va=hex(state),symbols=globals,original=expected.hex(),state_bytes=state_bytes)
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(m['sha256'])
