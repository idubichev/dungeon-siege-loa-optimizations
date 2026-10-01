"""Copy a save, changing only serialized attribute growth coefficients."""
from pathlib import Path
import hashlib,json,re,struct,sys
sys.path.insert(0,str(Path(__file__).parent/'tools'))
from tank import Tank,write_tank
source,dest=map(Path,sys.argv[1:3]);assert source.resolve()!=dest.resolve() and not dest.exists()
tank=Tank(source);files={name:tank.read(name)for name in tank.files};world=bytearray(files['world.xdat']);before=bytes(world);edits=[]
pattern=re.compile(rb'm_sname\x00(Melee|Ranged|Nature Magic|Combat Magic)\x00m_sclass\x00[^\x00]{1,30}\x00m_strinfluence\x00(.{4})m_dexinfluence\x00(.{4})m_intinfluence\x00(.{4})m_xp\x00',re.S)
for m in pattern.finditer(before):
 school=m[1].decode();major={'Melee':0,'Ranged':1,'Nature Magic':2,'Combat Magic':2}[school]
 for i in range(3):
  value=1.35 if i==major else 1.0;old=struct.unpack('<f',m[i+2])[0];assert 0<=old<=2
  at=m.start(i+2);new=struct.pack('<f',value);world[at:at+4]=new
  if new!=m[i+2]:edits.append({'school':school,'attribute':('strength','dexterity','intelligence')[i],'offset':at,'before':old,'after':value})
assert edits and len(world)==len(before)
check=bytearray(world)
for e in edits:check[e['offset']:e['offset']+4]=before[e['offset']:e['offset']+4]
assert bytes(check)==before
files['world.xdat']=bytes(world);write_tank(dest,files,source,'OP attributes - original progress preserved')
output=Tank(dest)
for name,old in files.items():assert output.read(name)==old
report={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'destination':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'changes':len(edits),'party_gas_xp_and_levels_unchanged':output.read('party.gas')==tank.read('party.gas'),'all_other_archive_members_unchanged':True,'edits':edits}
dest.with_suffix('.migration.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items()if k!='edits'})
