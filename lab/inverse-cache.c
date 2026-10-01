/* Game-local cache for dgVoodoo 2.53's pure 4x4 inverse routine.
 * Both magic addresses are filled by the test/installation helper.
 * Exact input bits, transpose mode, and x87 control word form the key.
 * Contended calls, infinities, NaNs, and singular results use the original.
 */
typedef unsigned U;
typedef struct { U mode, valid, input[16], output[16]; } Entry;
typedef struct { volatile U lock; U hits, misses, reserved; Entry entries[4096]; } Store;
typedef U (__attribute__((regparm(1))) *Original)(const U *, U *, U);

U __attribute__((regparm(1))) inverse_cache(const U *input, U *output, U transpose) {
    Store *store=(Store *)0x11223344;
    Original original=(Original)0x22334455;
    unsigned short cw;
    __asm__ volatile("fnstcw %0":"=m"(cw));
    U mode=cw | ((transpose & 255 ? 1u:0u)<<16);
    U hash=2166136261u;
    for(U i=0;i<16;i++) {
        U word=input[i];
        if((word & 0x7f800000u)==0x7f800000u) return original(input,output,transpose);
        hash=(hash^word)*16777619u;
    }
    hash^=mode; hash^=hash>>16; hash*=0x85ebca6bu;
    hash^=hash>>13; hash*=0xc2b2ae35u; hash^=hash>>16;
    if(!__sync_bool_compare_and_swap(&store->lock,0,1)) return original(input,output,transpose);
    Entry *entry=&store->entries[hash&4095];
    if(entry->valid && entry->mode==mode) {
        U same=1;
        for(U i=0;i<16;i++) if(input[i]!=entry->input[i]) { same=0; break; }
        if(same) {
            for(U i=0;i<16;i++) output[i]=entry->output[i];
            store->hits++;
            __sync_lock_release(&store->lock);
            return (((U)output+64)&0xffffff00u)|1;
        }
    }
    store->misses++;
    entry->valid=0; entry->mode=mode;
    for(U i=0;i<16;i++) entry->input[i]=input[i];
    U result=original(input,output,transpose);
    if((result&255)==1) {
        for(U i=0;i<16;i++) entry->output[i]=output[i];
        entry->valid=1;
    }
    __sync_lock_release(&store->lock);
    return result;
}
