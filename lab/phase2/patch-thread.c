typedef unsigned U;
#define W __attribute__((stdcall))
typedef U (W *Open)(U,U,U);typedef U (W *Unary)(U);typedef U (W *Context)(U,U*);typedef U (W *Protect)(void*,U,U,U*);typedef U (W *Flush)(U,void*,U);
typedef struct {U tid,addr,len,result;Open open;Unary suspend,resume;Context context;Unary sleep,close;Protect protect;Flush flush;unsigned char expected[32],replacement[32];} State;
U W patch_thread(State *s) {
 s->result=2;if(s->len>32)return 2;U h=s->open(0x5a,0,s->tid);if(!h)return 2;
 for(U attempt=0;attempt<100;attempt++) {
  U ctx[179];for(U i=0;i<179;i++)ctx[i]=0;ctx[0]=0x10003;
  if(s->suspend(h)==~0u)break;
  U ok=s->context(h,ctx);
  if(!ok){s->resume(h);break;}
  if(ctx[46]>=s->addr && ctx[46]<s->addr+s->len){s->resume(h);s->sleep(1);s->result=3;continue;}
  unsigned char *dest=(unsigned char*)s->addr;U same=1;
  for(U i=0;i<s->len;i++)if(dest[i]!=s->expected[i])same=0;
  if(!same){s->result=1;s->resume(h);break;}
  U prev=0,ignored=0;
  if(s->protect(dest,s->len,0x40,&prev)){
   for(U i=0;i<s->len;i++)dest[i]=s->replacement[i];
   U flushed=s->flush(~0u,dest,s->len);U restored=s->protect(dest,s->len,prev,&ignored);s->result=flushed&&restored?0:4;
  }
  s->resume(h);break;
 }
 s->close(h);return s->result;
}
