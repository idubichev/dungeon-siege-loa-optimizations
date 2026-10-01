"""Build isolated PE patches before loading; preserve original imports and relocations."""
from pathlib import Path
import struct,json,hashlib,sys
p=Path(__file__).parent;lab=p.parent;support=p/'rollback/Dungeon Siege Optimized Support';game=p/'rollback/Dungeon Siege Wine10 Test.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege'
level=sys.argv[1] if len(sys.argv)>1 else 'all';out=p/('static-'+level);out.mkdir(exist_ok=True)
def align(v,n):return (v+n-1)//n*n
def load(name):return (support/name).read_bytes()
class PE:
 def __init__(self,path):
  self.b=bytearray(path.read_bytes());self.pe=struct.unpack_from('<I',self.b,60)[0];self.o=self.pe+24;self.n=struct.unpack_from('<H',self.b,self.pe+6)[0];self.sh=self.o+struct.unpack_from('<H',self.b,self.pe+20)[0];self.base=struct.unpack_from('<I',self.b,self.o+28)[0];self.sa,self.fa=struct.unpack_from('<II',self.b,self.o+32);self.sections=[];self.reloc={};self.hooks=[];self.code=bytearray();self.data=0;self.packed=path.name.lower()=="d3dimm.dll"
  for i in range(self.n):
   pos=self.sh+i*40;vs,va,rs,rp=struct.unpack_from('<4I',self.b,pos+8);self.sections.append((va,vs,rs,rp))
  assert self.sh+(self.n+2)*40<=min(s[3] for s in self.sections if s[2])
  self.crva=align(max(va+max(vs,rs) for va,vs,rs,rp in self.sections),self.sa);self.drva=self.crva+0x10000
  rr,sz=struct.unpack_from('<II',self.b,self.o+136)
  if sz:
   pos=self.offset(rr);end=pos+sz
   while pos+8<=end:
    page,size=struct.unpack_from('<II',self.b,pos)
    if not size:break
    assert size>=8 and pos+size<=end
    for x in struct.unpack_from('<'+'H'*((size-8)//2),self.b,pos+8):
     if x>>12:assert x>>12==3;self.reloc[page+(x&4095)]=3
    pos+=size
 def offset(self,rva):
  va,vs,rs,rp=next(s for s in self.sections if s[0]<=rva<s[0]+s[2]);return rp+rva-va
 def read(self,va,n):return bytes(self.b[self.offset(va-self.base):self.offset(va-self.base)+n])
 def reserve(self,n):
  pos=align(len(self.code),16);self.code.extend(b'\x90'*(pos-len(self.code))+b'\x90'*n);return pos,self.base+self.crva+pos
 def data_alloc(self,n):
  pos=align(self.data,16);self.data=pos+n;return self.base+self.drva+pos
 def absolute(self,codepos):self.reloc[self.crva+codepos]=3
 def put(self,pos,b):self.code[pos:pos+len(b)]=b
 def hook(self,entry,expected,target,name):
  
  if not self.packed:
   assert self.read(entry,len(expected))==expected,(name,hex(entry));off=self.offset(entry-self.base);self.b[off:off+5]=b'\xe9'+struct.pack('<i',target-entry-5)
  self.hooks.append({'name':name,'entry':hex(entry),'target':hex(target),'original_prefix':expected[:5].hex()})
 def finish(self,path):
  if self.packed:
   init='renderer-init-four' if len(self.hooks)==4 else 'renderer-init';body=bytearray((p/(init+'.bin')).read_bytes());pos,addr=self.reserve(len(body));oldentry=self.base+struct.unpack_from('<I',self.b,self.o+16)[0]
   inv,mat=self.hooks[:2]
   values={'0x11110000':self.base+0x8708c,'0x22220000':self.base+0x87090,'0x33330000':oldentry,'0x44440000':self.base+0x6e9b,'0x55550000':self.base+0x6e44,'0x66660000':int(inv['target'],16)-int(inv['entry'],16)-5,'0x77770000':int(mat['target'],16)-int(mat['entry'],16)-5,'code':addr}
   if len(self.hooks)==4:
    t1,t2=self.hooks[2:];values.update({'0x88880000':int(t1['entry'],16),'0x99990000':int(t2['entry'],16),'0xaaaa0000':int(t1['target'],16)-int(t1['entry'],16)-5,'0xbbbb0000':int(t2['target'],16)-int(t2['entry'],16)-5})
   for r in json.loads((p/(init+'-relocations.json')).read_text()):
    value=values[r['target']]+r['value'];struct.pack_into('<I',body,r['offset'],value&0xffffffff)
    if r['kind']=='absolute':self.absolute(pos+r['offset'])
   self.put(pos,body);struct.pack_into('<I',self.b,self.o+16,addr-self.base)
  relocpos=align(len(self.code),4);self.code.extend(b'\0'*(relocpos-len(self.code)));groups={}
  for r,t in sorted(self.reloc.items()):groups.setdefault(r&~4095,[]).append((t<<12)|(r&4095))
  rel=bytearray()
  for page,entries in groups.items():
   if len(entries)%2:entries.append(0)
   rel.extend(struct.pack('<II',page,8+len(entries)*2)+struct.pack('<'+'H'*len(entries),*entries))
  self.code.extend(rel);assert len(self.code)<0x10000
  raw=align(len(self.b),self.fa);rs=align(len(self.code),self.fa);self.b.extend(b'\0'*(raw-len(self.b))+self.code+b'\0'*(rs-len(self.code)))
  for i,(name,vs,va,size,pointer,flags) in enumerate([(b'.dsopt',len(self.code),self.crva,rs,raw,0x60000020),(b'.dsdata',max(self.data,16),self.drva,0,0,0xc0000080)]):
   self.b[self.sh+(self.n+i)*40:self.sh+(self.n+i+1)*40]=struct.pack('<8sIIIIIIHHI',name,vs,va,size,pointer,0,0,0,0,flags)
  struct.pack_into('<H',self.b,self.pe+6,self.n+2);struct.pack_into('<I',self.b,self.o+56,align(self.drva+max(self.data,16),self.sa));struct.pack_into('<I',self.b,self.o+4,struct.unpack_from('<I',self.b,self.o+4)[0]+rs);struct.pack_into('<I',self.b,self.o+12,struct.unpack_from('<I',self.b,self.o+12)[0]+align(max(self.data,16),self.sa));struct.pack_into('<II',self.b,self.o+136,self.crva+relocpos,len(rel));struct.pack_into('<I',self.b,self.o+64,0)
  # Windows image checksum (the field itself is zero while summing).
  total=0
  for i in range(0,len(self.b),2):total+=(self.b[i]|((self.b[i+1] if i+1<len(self.b) else 0)<<8));total=(total&65535)+(total>>16)
  total=(total&65535)+(total>>16);struct.pack_into('<I',self.b,self.o+64,total+len(self.b));path.write_bytes(self.b)
  return {'file':str(path),'sha256':hashlib.sha256(self.b).hexdigest(),'code_bytes':len(self.code),'cache_bytes':self.data,'code_section_rva':hex(self.crva),'data_section_rva':hex(self.drva),'hooks':self.hooks}
def jump(source,target):return b'\xe9'+struct.pack('<i',target-source-5)
def cache(pe,name,entry,size,trampoline=0):
 body=bytearray(load(name+'-cache.bin'));orig=load(name+'-original.bin');oldoff=align(len(body),16);pos,addr=pe.reserve(oldoff+(trampoline+5 if trampoline else len(orig)));data=pe.data_alloc(size)
 for r in json.loads(load(name+'-cache-relocations.json')):
  struct.pack_into('<I',body,r['offset'],(data if r['target']=='data' else addr if r['target']=='code' else addr+oldoff)+r['addend']);pe.absolute(pos+r['offset'])
 body.extend(b'\x90'*(oldoff-len(body)));body.extend(orig[:trampoline]+jump(addr+oldoff+trampoline,entry+trampoline) if trampoline else orig);pe.put(pos,body);pe.hook(entry,orig,addr,name)
def simple(pe,name,entry,folder=support,relocs=None):
 body=bytearray((folder/(name+'-sse.bin')).read_bytes());orig=(folder/(name+'-original.bin')).read_bytes();oldoff=align(len(body),16);pos,addr=pe.reserve(oldoff+len(orig));pattern=bytes.fromhex('55443322');assert body.count(pattern)==1;i=body.index(pattern);struct.pack_into('<I',body,i,addr+oldoff);pe.absolute(pos+i)
 if relocs:
  for r in json.loads((folder/relocs).read_text()):struct.pack_into('<I',body,r['offset'],addr+r['code_offset']);pe.absolute(pos+r['offset'])
 # Preserve absolute references in copied fallback bodies as well as new code.
 import capstone
 cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
 for ins in cs.disasm(orig,0):
  for op in ins.operands:
   if op.type==capstone.x86.X86_OP_MEM and not op.mem.base and not op.mem.index and op.mem.disp:pe.absolute(pos+oldoff+ins.address+ins.disp_offset)
 body.extend(b'\x90'*(oldoff-len(body)));body.extend(orig);pe.put(pos,body);pe.hook(entry,orig,addr,name)
def blend(pe):
 entry=0x69f325;body=bytearray(load('blend-sse.bin'));orig=load('blend-original.bin');oldoff=align(16+len(body),16);pos,addr=pe.reserve(oldoff+len(orig));i=body.index(bytes.fromhex('55443322'));struct.pack_into('<I',body,i,addr+oldoff);pe.absolute(pos+16+i)
 code=b'\xe8'+struct.pack('<i',11)+jump(addr+5,0x69f371)+b'\x90'*6+body;code+=b'\x90'*(oldoff-len(code))+orig;pe.put(pos,code);pe.hook(entry,orig[:-1],addr,'blend')
def light(pe):
 entry=0x6a1132;body=bytearray(load('light-sse.bin'));old=load('light-original.bin');oldoff=align(32+len(body),16);pos,addr=pe.reserve(oldoff+len(old));i=body.index(bytes.fromhex('55443322'));struct.pack_into('<I',body,i,addr+oldoff);pe.absolute(pos+32+i)
 d=bytearray.fromhex('505152e80000000085d25a59580f8400000000e900000000');struct.pack_into('<i',d,4,24);struct.pack_into('<i',d,15,0x6a1190-(addr+19));struct.pack_into('<i',d,20,0x6a1177-(addr+24));code=d+b'\x90'*8+body;code+=b'\x90'*(oldoff-len(code))+old
 # Original x87 fallback's absolute constants retain their original VA.
 import capstone
 cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
 for ins in cs.disasm(old,0):
  for op in ins.operands:
   if op.type==capstone.x86.X86_OP_MEM and not op.mem.base and not op.mem.index and op.mem.disp:pe.absolute(pos+oldoff+ins.address+ins.disp_offset)
 pe.put(pos,code);pe.hook(entry,load('light-original-fragment.bin'),addr,'light')
def frustum(pe):
 entry=0x684d7f;end=0x684f54;body=(p/'frustum-sse.bin').read_bytes();orig=(p/'frustum-original.bin').read_bytes();oldoff=align(64+len(body),16);pos,addr=pe.reserve(oldoff+len(orig)+5)
 d=bytearray.fromhex('51528d7efcff35e8a572005753e80000000083c40c83f8ff0f84000000008945105a59e9000000005a59e900000000');struct.pack_into('<i',d,14,64-18);struct.pack_into('<i',d,26,10);struct.pack_into('<i',d,36,end-(addr+40));struct.pack_into('<i',d,43,oldoff-47);pe.absolute(pos+7)
 old=bytearray(orig)
 for r in json.loads((p/'frustum-original-relocations.json').read_text()):
  if 'relative_to' in r:struct.pack_into('<i',old,r['offset'],{'vec-ctor':0x47d209,'vec-sub':0x49efe8,'vec-dot':0x64af6e}[r['target']]-(addr+oldoff+r['relative_to']))
  else:pe.absolute(pos+oldoff+r['offset'])
 code=d+b'\x90'*(64-len(d))+body;code+=b'\x90'*(oldoff-len(code))+old+jump(addr+oldoff+len(old),end);pe.put(pos,code);pe.hook(entry,orig,addr,'frustum')
def scope(pe):
 entry=0x69f2ff;orig=(p/'scope-loop-original.bin').read_bytes();prefix=(p/'scope-prefix.bin').read_bytes();quat=(p/'quat-scoped.bin').read_bytes();b=bytearray((p/'blend-scoped.bin').read_bytes());old=load('blend-original.bin');inner=len(prefix);tail=inner+len(orig);qoff=align(tail+16,16);boff=align(qoff+len(quat),16);oldoff=align(boff+len(b),16);pos,addr=pe.reserve(oldoff+len(old))
 loop=bytearray(orig);struct.pack_into('<i',loop,34,qoff-(inner+38));loop[38:114]=b'\xe8'+struct.pack('<i',boff-(inner+43))+jump(inner+43,inner+114)+b'\x90'*66;struct.pack_into('<i',loop,148,0x69fa05-(addr+inner+152));quat=quat[:-4]+struct.pack('<i',0x535f42-(addr+qoff+len(quat)));i=b.index(bytes.fromhex('55443322'));struct.pack_into('<I',b,i,addr+oldoff);pe.absolute(pos+boff+i)
 code=prefix+loop+bytes.fromhex('0fae54240483c408')+jump(addr+tail+8,0x69f3a6);code+=b'\x90'*(qoff-len(code))+quat;code+=b'\x90'*(boff-len(code))+b;code+=b'\x90'*(oldoff-len(code))+old;pe.put(pos,code);pe.hook(entry,orig[:5],addr,'scope')
def skin(pe):
 previous=pe.hooks[-1];assert previous['name']=='scope';fallback=int(previous['target'],16);entry=int(previous['entry'],16)
 body=bytearray((p/'skin-loop.bin').read_bytes());pos,addr=pe.reserve(64+len(body))
 for r in json.loads((p/'skin-loop-relocations.json').read_text()):
  assert r['kind']=='absolute';value=(addr+64 if r['target']=='code' else 0x69fa05)+r['value'];struct.pack_into('<I',body,r['offset'],value);pe.absolute(pos+64+r['offset'])
 # Preserve original registers while calling the checked batch kernel. On
 # success the original loop leaves EDI at end and ESI at last vertex*12.
 d=bytearray.fromhex('60575355e80000000083c40c85c0610f84000000008b7df88b75e46bf60ce900000000')
 struct.pack_into('<i',d,5,64-9);struct.pack_into('<i',d,17,fallback-(addr+21));struct.pack_into('<i',d,31,0x69f3a6-(addr+35))
 pe.put(pos,d+b'\x90'*(64-len(d))+body);pe.hooks.pop();pe.hook(entry,jump(entry,fallback),addr,'skin-batch')
def lighting(pe):
 previous=next(h for h in pe.hooks if h['name']=='light');fallback=int(previous['target'],16);entry=int(previous['entry'],16)
 body=bytearray((p/'light-loop.bin').read_bytes());pos,addr=pe.reserve(64+len(body))
 for r in json.loads((p/'light-loop-relocations.json').read_text()):
  assert r['kind']=='absolute';value=(addr+64 if r['target']=='code' else 0x684092)+r['value'];struct.pack_into('<I',body,r['offset'],value);pe.absolute(pos+64+r['offset'])
 d=bytearray.fromhex('60565755e80000000083c40c85c0610f84000000006bf60c01f731f6e900000000')
 struct.pack_into('<i',d,5,64-9);struct.pack_into('<i',d,17,fallback-(addr+21));struct.pack_into('<i',d,29,0x6a119a-(addr+33))
 pe.put(pos,d+b'\x90'*(64-len(d))+body);pe.hooks.remove(previous);pe.hook(entry,jump(entry,fallback),addr,'light-batch')
def raybox(pe):
 body=bytearray((p/'raybox-sse.bin').read_bytes());orig=(p/'raybox-original.bin').read_bytes();oldoff=align(len(body),16);pos,addr=pe.reserve(oldoff+len(orig))
 for r in json.loads((p/'raybox-sse-relocations.json').read_text()):
  assert r['kind']=='absolute';struct.pack_into('<I',body,r['offset'],(addr if r['target']=='code' else addr+oldoff)+r['value']);pe.absolute(pos+r['offset'])
 for r in json.loads((p/'raybox-original-relocations.json').read_text()):pe.absolute(pos+oldoff+r['offset'])
 pe.put(pos,body+b'\x90'*(oldoff-len(body))+orig);pe.hook(0x64a770,orig,addr,'ray-box-intersection')
ds=PE(game/'DSLOA.exe');dll=PE(game/'D3DImm.dll')
cache(dll,'inverse',dll.base+0x6e9b,16+136*4096);simple(dll,'matmul',dll.base+0x6e44)
if level in ['copy','copy-skin-last','lighting','raybox']:
 simple(dll,'transpose',dll.base+0x6d65,p);simple(dll,'transpose2',dll.base+0x6de5,p)

if level in ['last','skin-last','copy-skin-last']:
 saved_support=support;support=p/'last-payload';cache(ds,'slerp',0x69fa05,16+60*8193,7);support=saved_support
else:cache(ds,'slerp',0x69fa05,16+60*8192,7)
light(ds);blend(ds);cache(ds,'slerp2',0x41adf4,16+60*8192,6);simple(ds,'vec3',0x43e774)
if level!='eight':
 frustum(ds);simple(ds,'qmul',0x5361ef,p);simple(ds,'ortho',0x43e82d,p,'ortho-sse-relocations.json')
if level in ['all','last','skin','skin-last','copy','copy-skin-last','lighting','raybox']:scope(ds)
if level in ['skin','skin-last','copy-skin-last']:skin(ds)
if level in ['lighting','raybox']:lighting(ds)
if level=='raybox':raybox(ds)
manifest={'level':level,'method':'Static isolated-file patches; RX code and RW zero-initialized cache sections; preserved and extended PE base relocations','files':[ds.finish(out/'DSLOA.exe'),dll.finish(out/'D3DImm.dll')]};(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
