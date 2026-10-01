/* Cache identical quaternion interpolation inputs; retain original arithmetic. */
typedef unsigned U;
typedef struct { U mode,valid,key[9],output[4]; } Entry;
typedef struct { volatile U lock; U hits,misses,reserved; Entry entries[8192]; } Store;
typedef void (*Original)(U *,const U *,const U *,U);
void slerp2_cache(U *out,const U *a,const U *b,U weight) {
    Store *store=(Store *)0x11223344; Original original=(Original)0x22334455;
    unsigned short cw; __asm__ volatile("fnstcw %0":"=m"(cw));
    if((cw&63)!=63) { original(out,a,b,weight); return; }
    if((U)out-(U)a<16 || (U)a-(U)out<16 || (U)out-(U)b<16 || (U)b-(U)out<16) { original(out,a,b,weight);return; }
    U key[9],hash=2166136261u;
    for(U i=0;i<4;i++) { key[i]=a[i];key[i+4]=b[i]; } key[8]=weight;
    for(U i=0;i<9;i++) {
        if((key[i]&0x7f800000u)==0x7f800000u) { original(out,a,b,weight); return; }
        hash=(hash^key[i])*16777619u;
    }
    hash^=cw;hash^=hash>>16;hash*=0x85ebca6bu;hash^=hash>>13;hash*=0xc2b2ae35u;hash^=hash>>16;
    if(!__sync_bool_compare_and_swap(&store->lock,0,1)) { original(out,a,b,weight);return; }
    Entry *e=&store->entries[hash&8191];
    if(e->valid && e->mode==cw) {
        U same=1;for(U i=0;i<9;i++) if(e->key[i]!=key[i]) {same=0;break;}
        if(same) {
            for(U i=0;i<4;i++) out[i]=e->output[i];
            store->hits++;__sync_lock_release(&store->lock);return;
        }
    }
    e->valid=0;e->mode=cw;for(U i=0;i<9;i++) e->key[i]=key[i];
    original(out,a,b,weight);
    for(U i=0;i<4;i++)e->output[i]=out[i];
    e->valid=1;store->misses++;__sync_lock_release(&store->lock);
}
