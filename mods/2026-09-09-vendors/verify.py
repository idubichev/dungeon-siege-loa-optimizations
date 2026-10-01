"""Validate archive coverage and emulate the native hook with instrumented engine calls."""
from pathlib import Path
import json
import re
import struct
import sys
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import *

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent/'2026-09-06/tools'))
from tank import Tank
from gas import blocks, fields, ancestors
meta = json.loads((ROOT/'patch.json').read_text())
resources = json.loads((ROOT/'resources.json').read_text())
archive = Tank(ROOT/'DS_OP_LootVendors_v2.dsres')
for path in archive.files:
    archive.read(path) # decompression/CRC check

def stores(text):
    _, nodes = blocks(text, tolerant=True)
    return {next(a.name for a in ancestors(b) if 't:template' in a.name): b for b in nodes if b.name=='store_pcontent'}

def quantities(text, store):
    chunk=text[store.start:store.end+1];_,nodes=blocks(chunk)
    return [sum(float(re.match(r'[\d.]+',v)[0]) for b in nodes for k,v,*_ in fields(chunk,b)
                if k==key and re.match(r'[\d.]+',v)) for key in ['min','max']]

def without_stock(text):
    for b in sorted(stores(text).values(), key=lambda b:b.start, reverse=True):
        text=text[:b.start]+'STOCK'+text[b.end+1:]
    return text

for path in {row['path'] for row in resources['changes']}:
    before=(ROOT/'before'/path).read_text(encoding='cp1252')
    after=archive.read(path).decode('cp1252').replace('\r\n','\n')
    assert without_stock(before)==without_stock(after), ('outside-store change',path)
    old, new=stores(before),stores(after)
    for name in old:
        assert quantities(before,old[name])==quantities(after,new[name]),(path,name)
jonn=next(row for row in resources['changes'] if row['template']=='t:template,n:jonn')
assert {'body','gloves','helm','boots','shield','melee','ranged'} <= {r['category'] for r in jonn['rolls']}
assert sum(r['rare']+r['unique'] for r in jonn['rolls'])==139

results=[]
for relocation in [0,0x1000000]:
    for scenario in ['normal','buyback','equipped','other_shopper','no_owner','no_inventory','no_config','no_query','empty_query','empty_stock','all_buyback','remove_failed']:
        u=Uc(UC_ARCH_X86,UC_MODE_32)
        entry=int(meta['entry'],16)+relocation;target=int(meta['target'],16)+relocation
        engine={int(row['address'],16)+relocation for row in meta['calls']}
        for page in {a&~4095 for a in [entry,target,*engine]}:
            u.mem_map(page,4096)
        u.mem_map(0x2000000,0x10000)
        store,owner,inv,config=0x2001000,0x2002000,0x2003000,0x2004000
        vec,stack=0x2005000,0x200e000
        items=[0x2006000+i*256 for i in range(4)] if scenario!='empty_stock' else []
        sold=set(items[:2]) if scenario=='buyback' else set(items) if scenario=='all_buyback' else set()
        equipped=set(items[:1]) if scenario=='equipped' else set()
        calls=[];removed=[];deleted=[]
        def put(address,*values):u.mem_write(address,struct.pack('<'+'I'*len(values),*values))
        def read(address):return struct.unpack('<I',bytes(u.mem_read(address,4)))[0]
        put(store+4,0 if scenario=='no_owner' else owner)
        put(store+0x24,0x2004100)
        put(store+0x68,vec,vec+4)
        put(owner+0x2c,0 if scenario=='no_inventory' else inv)
        put(inv+8,0 if scenario=='no_config' else config)
        put(vec,*items)
        for item in items:put(item+0x4c,item+0x80)
        put(stack,vec) # original vector-erase argument
        u.mem_write(entry,bytes.fromhex(meta['patch']))
        u.mem_write(target,bytes.fromhex(meta['code']))
        registers={UC_X86_REG_EAX:0x12345,UC_X86_REG_EBX:0x23456,UC_X86_REG_ECX:store+0x68,
                   UC_X86_REG_EDX:0x34567,UC_X86_REG_ESI:0x45678,UC_X86_REG_EDI:0x56789,
                   UC_X86_REG_EBP:0x67890,UC_X86_REG_ESP:stack}
        for reg,val in registers.items():u.reg_write(reg,val)
        u.reg_write(UC_X86_REG_EFLAGS,0x246)
        def intercept(uc,address,size,_):
            if address not in engine:return
            fn=address-relocation;esp=uc.reg_read(UC_X86_REG_ESP);this=uc.reg_read(UC_X86_REG_ECX)
            arg=lambda n:read(esp+4+4*n)
            calls.append(hex(fn));cleanup=0;answer=0
            if fn==0x63d36d:
                assert this==store+0x68 and arg(0)==vec
                put(store+0x6c,vec+4 if scenario=='other_shopper' else vec);cleanup=4
                answer=0x12345
            elif fn==0x5357b0:
                assert this==config and bytes(uc.mem_read(arg(1),15))==b'store_pcontent\0'
                put(arg(0),0 if scenario=='no_query' else config,0);cleanup=8
            elif fn==0x43a760:answer=int(scenario=='empty_query')
            elif fn==0x573ab5:
                assert this==inv and arg(0)==0x15
                put(arg(1),vec,vec+len(items)*4,vec+len(items)*4);cleanup=8;answer=1
            elif fn==0x573108:
                assert this==inv
                answer=0 if arg(0) in equipped else 0xd;cleanup=4
            elif fn==0x4ac4f4:
                assert this==store+0x20
                item=arg(1)-0x4c
                put(arg(0),0x2004200 if item in sold else read(store+0x24));cleanup=8
            elif fn==0x5764ec:
                assert this==inv and [arg(i) for i in range(1,4)]==[0,0,1]
                assert arg(0) not in sold|equipped
                answer=int(scenario!='remove_failed')
                if answer:removed.append(arg(0))
                cleanup=16
            elif fn==0x492570:answer=0x2004300
            elif fn==0x471544:
                assert this==0x2004300 and arg(0) in removed
                deleted.append(arg(0));cleanup=4
            elif fn==0x43a8e0:
                put(this,read(arg(0)),read(arg(0)+4));cleanup=4
            elif fn==0x57d6fa:
                assert this==inv and arg(0)==config
                assert removed==[x for x in items if x not in sold|equipped]
                cleanup=8
            elif fn==0x5e6418:assert this==store
            elif fn not in [0x654027,0x43a747]:raise AssertionError(hex(fn))
            uc.reg_write(UC_X86_REG_EAX,answer)
            uc.reg_write(UC_X86_REG_EIP,read(esp));uc.reg_write(UC_X86_REG_ESP,esp+4+cleanup)
        u.hook_add(UC_HOOK_CODE,intercept)
        u.emu_start(entry,entry+5,count=5000)
        assert u.reg_read(UC_X86_REG_ESP)==stack+4
        for reg,val in registers.items():
            if reg!=UC_X86_REG_ESP:assert u.reg_read(reg)==val,(scenario,reg)
        assert u.reg_read(UC_X86_REG_EFLAGS)==0x246
        assert removed==deleted
        should_reroll=scenario in ['normal','buyback','equipped','empty_stock','all_buyback']
        assert calls.count('0x57d6fa')==int(should_reroll),(scenario,calls)
        results.append(dict(scenario=scenario,relocation=hex(relocation),removed=len(removed),rerolled=should_reroll))
report=dict(status='passed',native_cases=results,resource_crc_checks=len(archive.files),stores=resources['stores'],
            jonn_targeted_rolls=139,jonn_total_rolls=196,engine_calls_instrumented=True,in_game_test=False)
(ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'Passed {len(results)} native control-flow cases; {resources["stores"]} stock budgets; {len(archive.files)} CRC checks.')
