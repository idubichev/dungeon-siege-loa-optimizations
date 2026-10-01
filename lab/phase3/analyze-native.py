"""Leaf-only sample accounting; offline direct-branch CFG labels Rosetta helper code."""
from pathlib import Path
import re,json,struct,collections,sys,capstone
base=Path(__file__).parent
b=Path('/Library/Apple/usr/libexec/oah/libRosettaRuntime').read_bytes()
exports=json.loads((base/'rosetta-helper-exports.json').read_text())
cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);cs.detail=True;cs.skipdata=True
ins={i.address:i for i in cs.disasm(b[0x1a20:0x50000],0x1a20)}
def reachable(roots):
 seen=set();pending=list(roots)
 while pending:
  addr=pending.pop()
  if addr in seen or addr not in ins:continue
  seen.add(addr);i=ins[addr];m=i.mnemonic
  if i.id==0:continue
  targets=[o.imm for o in i.operands if o.type==capstone.arm64.ARM64_OP_IMM]
  if m in ('ret','br'):continue
  if m=='b':pending+=targets[-1:];continue
  if m=='bl' or m.startswith('b.') or m in ('cbz','cbnz','tbz','tbnz'):pending+=targets[-1:]
  pending.append(addr+4)
 return seen
x87=reachable([a for a,n in exports if '::x87_' in n]);trans=reachable([a for a,n in exports if '::translator_' in n or '::ir_create' in n]);other=reachable([a for a,n in exports if '::x87_' not in n and '::translator_' not in n and '::ir_create' not in n])
res={'source':sys.argv[1],'method':'Non-overlapping leaf counts per thread. Static x87/translator classification follows direct branches only; indirect branches are unresolved. Counts are wall samples including waits, not pure CPU cost or native-vs-emulated overhead.','threads':[]}
s=Path(sys.argv[1]).read_text();s=s[s.index('Call graph:'):s.index('Total number in stack')]
for seg in re.split(r'(?=^    \d+ Thread_)',s,flags=re.M)[1:]:
 header=seg.splitlines()[0];ls=[];stack=[];cats=collections.Counter();hot=collections.Counter();waits=collections.Counter()
 for l in seg.splitlines()[1:]:
  m=re.match(r'^([ +!:|]*)(\d+) (.*)',l)
  if m:ls.append((len(m[1]),int(m[2]),m[3]))
 for idx,(dep,n,label) in enumerate(ls):
  while stack and stack[-1][0]>=dep:stack.pop()
  if idx+1==len(ls) or ls[idx+1][0]<=dep:
   if 'libRosettaRuntime' in label:
    off=int(re.search(r'\+ (0x[0-9a-f]+)',label)[1],16);hot[hex(off)]+=n
    if off in x87 and off not in trans:cat='x87 emulation helpers'
    elif off in trans and off not in x87:cat='translation compiler helpers'
    elif off in trans and off in x87:cat='shared compiler/emulation helpers'
    else:cat='unclassified Rosetta library helpers'
   elif 'Rosetta JIT' in label:cat='translated code execution'
   elif 'Rosetta Runtime Routines' in label:cat='Rosetta runtime stubs'
   elif '(in runtime)' in label and ' + 0x3ea0 ' in label:cat='Rosetta exception server waiting in mach_msg2_trap'
   elif '(in runtime)' in label:cat='Rosetta runtime'
   elif any(k in '\n'.join([t[1] for t in stack]+[label]) for k in ['__ulock_wait','__psynch_cvwait','semaphore_wait_trap','mach_msg2_trap','kevent','poll  (in','__select','nanosleep']):
    cat='OS wait / synchronization';parents=[t[1] for t in stack if not t[1].startswith('__wine_syscall_dispatcher')];waits[' → '.join(parents[-4:])]+=n
   elif 'unknown binary' in label:cat='unresolved native leaf'
   elif '(in ntdll.so)' in label:cat='Wine native API work'
   else:cat='other native work'
   cats[cat]+=n
  stack.append((dep,label))
 total=sum(cats.values());r={'thread':header.strip(),'samples':total,'categories':dict(cats),'percent':{k:round(v*100/total,2) for k,v in cats.items()},'hot_rosetta_library_offsets':hot.most_common(12),'wait_paths':waits.most_common(6)};res['threads'].append(r)
 if cats['x87 emulation helpers']>10 or 'exceptionserver' in header:print(json.dumps(r,indent=2))
output=Path(sys.argv[1]).with_suffix('.json');output.write_text(json.dumps(res,indent=2));print('Saved',output)
(base/'rosetta-cfg-metadata.json').write_text(json.dumps({'x87_reachable_instructions':len(x87),'translator_reachable_instructions':len(trans),'hot_offsets':{hex(a):{'x87':a in x87,'translator':a in trans} for a in [0x10508,0x177ac,0x18714,0x16a00,0x10d94]},'library_sha256':__import__('hashlib').sha256(b).hexdigest()},indent=2))
