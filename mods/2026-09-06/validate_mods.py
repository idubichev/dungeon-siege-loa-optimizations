from pathlib import Path
import json,hashlib,re,sys
sys.path.insert(0,str(Path(__file__).parent/'tools'))
from tank import Tank
from gas import blocks,fields
p=Path(__file__).resolve().parent;m=json.loads((p/'build/manifest.json').read_text());a=json.loads((p/'analysis.json').read_text())
seen=set();count=0
for entry in m['packages']:
 t=Tank(p/'build'/entry['file'])
 assert t.priority==0x4001 and t.index_size==len(t.data)-t.dirs_at
 assert hashlib.sha256(t.data).hexdigest()==entry['sha256']
 for path in t.files:
  assert path not in seen;seen.add(path)
  raw=t.read(path);assert raw==(p/'source'/entry['file'].split('_')[2]/path).read_bytes()
  blocks(raw.decode('cp1252'),tolerant=True);count+=1
formula='world/global/formula/formulas.gas'
old=(p/a['effective'][formula]).read_text(encoding='cp1252');new=(p/'source/Attributes'/formula).read_text(encoding='cp1252')
pattern=r'((?:str|dex|int)_influence\s*=\s*)[^;]+'
assert re.sub(pattern,r'\1VALUE',old)==re.sub(pattern,r'\1VALUE',new)
attrs=[]
for b in blocks(new)[1]:
 f=dict((k,v.strip('"'))for k,v,*_ in fields(new,b))
 if f.get('name') in ['Melee','Ranged','Nature Magic','Combat Magic']:
  values=[float(f[k])for k in ['str_influence','dex_influence','int_influence']];assert sorted(values)==[1,1,1.35];attrs.append((f['name'],values))
assert len(attrs)==4
for c in m['changes']:
 if c['kind'] in ['rare_drop','unique_drop']:assert 0<=float(c['before'])<float(c['after'])<=1
r={'archives':len(m['packages']),'resource_crc_and_structure_checks':count,'priority':0x4001,'no_package_path_conflicts':True,'formula_only_changes_12_attribute_influences':True,'attributes':attrs,'existing_ikkyo_sources_preserved':all('ikkyo' in a['effective'][x] for x in ['world/contentdb/templates/regular/actors/good/npc/npc_fb_based.gas','world/contentdb/templates/regular/actors/good/npc/npc_pmo_based.gas'])}
(p/'build/validation.json').write_text(json.dumps(r,indent=2));print(r)
