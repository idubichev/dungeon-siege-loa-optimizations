typedef unsigned int U;typedef unsigned long long Q;typedef void *H;
#define WIN __attribute__((stdcall))
typedef H (WIN *Module)(const char*);typedef H (WIN *Proc)(H,const char*);typedef int (WIN *Counter)(Q*);
typedef struct {Counter counter;U ready;Q hz;U seq,index;Q ticks[16384];} Clock;
void WIN frame_tick(Clock *s,Module module,Proc proc) {
 if(!s->ready) {
  H k=module("kernel32.dll");if(!k)return;
  Counter c=(Counter)proc(k,"QueryPerformanceCounter"),f=(Counter)proc(k,"QueryPerformanceFrequency");
  if(!c||!f||!f(&s->hz)||!s->hz)return;
  s->counter=c;s->ready=1;
 }
 Q now;s->counter(&now);s->seq++;s->ticks[s->index&16383]=now;s->index++;s->seq++;
}
