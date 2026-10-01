typedef unsigned int u32;
typedef unsigned long long u64;
#ifndef FUNCTION_COUNT
#define FUNCTION_COUNT 4
#endif
typedef void *Handle;
#define WIN __attribute__((stdcall))
typedef Handle (WIN *GetModule)(const char*);
typedef Handle (WIN *GetProc)(Handle,const char*);
typedef int (WIN *QPC)(u64*);
typedef u32 (WIN *ThreadID)(void);
typedef struct { u64 calls,total,self,maximum; } Stat;
typedef struct { u64 start,child; u32 id,reserved; } Frame;
typedef struct { u32 id,depth,seq,dropped; Stat stats[FUNCTION_COUNT]; Frame frames[128]; } Thread;
typedef struct { QPC counter; ThreadID thread_id; u64 frequency; u32 ready,errors; Thread threads[8]; } State;
static Thread *thread(State *s) {
    u32 id=s->thread_id();
    for (u32 i=0;i<8;i++) {
        Thread *t=&s->threads[i];
        if (t->id==id) return t;
        if (!t->id && __sync_val_compare_and_swap(&t->id,0,id)==0) return t;
    }
    return 0;
}
int WIN profile_enter(u32 id,State *s,GetModule module,GetProc proc) {
    if (!s->ready) {
        Handle k=module("kernel32.dll");
        if (!k) return 0;
        QPC counter=(QPC)proc(k,"QueryPerformanceCounter");
        QPC frequency=(QPC)proc(k,"QueryPerformanceFrequency");
        ThreadID tid=(ThreadID)proc(k,"GetCurrentThreadId");
        if (!counter || !frequency || !tid) return 0;
        u64 hz;
        if (!frequency(&hz) || !hz) return 0;
        s->counter=counter;s->thread_id=tid;s->frequency=hz;
        __sync_synchronize();s->ready=1;
    }
    Thread *t=thread(s);
    if (!t) return 0;
    if (t->depth>=128) { t->dropped++;return 0; }
    Frame *f=&t->frames[t->depth++];
    f->id=id;f->child=0;
    s->counter(&f->start);
    return 1;
}
void WIN profile_exit(u32 id,State *s) {
    u64 end;
    s->counter(&end);
    Thread *t=thread(s);
    if (!t || !t->depth) { s->errors++;return; }
    Frame *f=&t->frames[t->depth-1];
    if (f->id!=id) { s->errors++;t->depth=0;return; }
    u64 elapsed=end-f->start;
    t->seq++;
    Stat *v=&t->stats[id];v->calls++;v->total+=elapsed;
    v->self+=elapsed>=f->child?elapsed-f->child:0;
    if (elapsed>v->maximum)v->maximum=elapsed;
    t->depth--;
    if (t->depth)t->frames[t->depth-1].child+=elapsed;
    t->seq++;
}
