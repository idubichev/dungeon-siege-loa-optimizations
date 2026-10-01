"""Read per-thread CPU counters without suspending threads or reading register context."""
import ctypes as c,time,sys,json,re
from pathlib import Path
lib=c.CDLL('/usr/lib/libproc.dylib',use_errno=True)
lib.proc_pidinfo.argtypes=[c.c_int,c.c_int,c.c_uint64,c.c_void_p,c.c_int]
lib.proc_pidinfo.restype=c.c_int
class Info(c.Structure):
 _fields_=[('user',c.c_uint64),('system',c.c_uint64)]+[(x,c.c_int32) for x in ['cpu','policy','state','flags','sleep','curpri','pri','maxpri']]+[('name',c.c_char*64)]
def read(pid):
 ids=sorted({int(x) for x in re.findall(r'Thread_(\d+)',Path(sys.argv[4]).read_text())});r={}
 for tid in ids:
  v=Info();got=lib.proc_pidinfo(pid,15,tid,c.byref(v),c.sizeof(v))
  if got==0 and c.get_errno()==3:continue
  assert got==c.sizeof(v),(got,c.get_errno(),tid)
  r[tid]={'user':v.user,'system':v.system,'name':v.name.decode(errors='replace'),'state':v.state}
 return r
pid=int(sys.argv[1]);a=read(pid);t=time.monotonic_ns();time.sleep(float(sys.argv[2]));b=read(pid);dt=time.monotonic_ns()-t
rows=[]
for tid in a.keys()&b.keys():
 u=(b[tid]['user']-a[tid]['user'])/dt*100;s=(b[tid]['system']-a[tid]['system'])/dt*100
 rows.append({'thread':tid,'name':b[tid]['name'],'cpu_percent_one_core':u+s,'user_percent':u,'system_percent':s})
rows.sort(key=lambda v:-v['cpu_percent_one_core']);out={'pid':pid,'seconds':dt/1e9,'thread_id_source':sys.argv[4],'total_cpu_percent':sum(r['cpu_percent_one_core'] for r in rows),'threads':rows};Path(sys.argv[3]).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
