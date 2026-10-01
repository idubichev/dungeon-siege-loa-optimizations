typedef unsigned U;typedef unsigned long long Q;typedef void *H;
#define W __attribute__((stdcall))
#define SLOTS 262144
typedef H(W *Module)(const char*);typedef H(W *Proc)(H,const char*);
typedef int(W *Counter)(Q*);typedef U(W *ThreadID)(void);
typedef struct {Q start,end;U id,thread,caller,serial;} Event;
typedef struct {Counter counter;ThreadID thread;Q hz;U ready,next;Event events[SLOTS];} State;
void W enter_log(Event *e,U id,U caller,State *s,Module module,Proc proc){
 if(!s->ready){H k=module("kernel32.dll");if(!k)return;
  Counter c=(Counter)proc(k,"QueryPerformanceCounter"),f=(Counter)proc(k,"QueryPerformanceFrequency");
  ThreadID t=(ThreadID)proc(k,"GetCurrentThreadId");if(!c||!f||!t||!f(&s->hz))return;
  s->counter=c;s->thread=t;__sync_synchronize();s->ready=1;
 }
 e->serial=0;e->end=0;e->id=id;e->thread=s->thread();e->caller=caller;s->counter(&e->start);
}
void W exit_log(Event *local,State *s){
 if(!s->ready)return;Q now;s->counter(&now);
 if(local->id>=DG_FIRST && (now-local->start)*500<s->hz)return;
 U ticket=__sync_fetch_and_add(&s->next,1);Event *e=&s->events[ticket&(SLOTS-1)];
 e->serial=0;e->start=local->start;e->end=now;e->id=local->id;e->thread=local->thread;e->caller=local->caller;
 __sync_synchronize();e->serial=ticket+1;
}
