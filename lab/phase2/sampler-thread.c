typedef unsigned U;
#define W __attribute__((stdcall))
typedef U (W *Open)(U,U,U);
typedef U (W *Unary)(U);
typedef U (W *Context)(U,U*);
typedef U (W *Error)(void);
typedef struct {U eip,esp,ebp,eax,ecx,stack[16];} Sample;
typedef struct {U tid,limit,delay;volatile U count,error,done;Open open;Unary suspend,resume;Context context;Unary sleep,close;Error errorfn;Sample samples[256];} State;
U W sample_thread(State *s) {
 U h=s->open(0x5a,0,s->tid);if(!h){s->error=s->errorfn();s->done=1;return 1;}
 for(U i=0;i<s->limit && i<256;i++){
  volatile U ctx[179];for(U j=0;j<179;j++)ctx[j]=0;ctx[0]=0x10003;
  if(s->suspend(h)==~0u){s->error=s->errorfn();break;}
  U ok=s->context(h,(U*)ctx);if(!ok)s->error=s->errorfn();
  if(ok){
   Sample *v=&s->samples[i];v->eip=ctx[46];v->esp=ctx[49];v->ebp=ctx[45];v->eax=ctx[44];v->ecx=ctx[43];
   for(U j=0;j<16;j++)v->stack[j]=((U*)ctx[49])[j];
   s->count=i+1;
  }
  s->resume(h);if(!ok)break;s->sleep(s->delay);
 }
 s->close(h);s->done=1;return 0;
}
