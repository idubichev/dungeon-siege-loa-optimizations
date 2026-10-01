"""Resolve the live renderer transform method without hooks or suspension."""
from pathlib import Path
import struct
p=Path(__file__).resolve().parent
source=(p.parent/'phase3/dump-loaded-win32.py').read_text()
exec(source.split('from pathlib import Path\nout=')[0])
def memory(address,size):
 b=c.create_string_buffer(size);n=c.c_size_t();assert read(hp,address,b,size,c.byref(n)) and n.value==size;return b.raw
def u32(address):return struct.unpack('<I',memory(address,4))[0]
base=next(m['base'] for m in modules if m['path'].split('\\')[-1].lower()=='dsloa.exe')
root=u32(base+0x3acf80);renderer=u32(root+0x44);interface=u32(renderer+0x600);vtable=u32(interface);method=u32(vtable+0x38)
out=Path(sys.argv[1]);out.mkdir(exist_ok=True)
result={'pid':pid,'root':hex(root),'renderer':hex(renderer),'interface':hex(interface),'vtable':hex(vtable),'method':hex(method),'method_label':label(method),'modules':modules}
stub=memory(method,2048)
assert stub[15]==0xe8
core=method+20+struct.unpack_from('<i',stub,16)[0]
assert label(core).startswith('D3DImm.DLL+')
result.update(core_method=hex(core),core_label=label(core))
(out/'transform-interface.json').write_text(json.dumps(result,indent=2)+'\n')
(out/'transform-method.bin').write_bytes(stub)
(out/'transform-core.bin').write_bytes(memory(core,4096))
print(result['method_label'],result['core_label'],flush=True);close(hp)
