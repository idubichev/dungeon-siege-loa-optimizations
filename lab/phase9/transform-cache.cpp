// Combine consecutive object transforms, retaining each rounded intermediate.
// Interface slots verified against Wine's IDirect3DDevice7 declaration.
#include <emmintrin.h>
typedef unsigned int u32;
#define WIN __attribute__((stdcall))
#define THIS __attribute__((thiscall))
typedef int (WIN *Transform)(void*,u32,float*);
static __m128d pair(const float* p) {
 return _mm_cvtps_pd(_mm_castsi128_ps(_mm_loadl_epi64((const __m128i*)p)));
}
static void mul(float* d,const float* a,const float* b) {
 for(u32 r=0;r<4;r++)for(u32 c=0;c<4;c+=2) {
  __m128d x=_mm_mul_pd(_mm_set1_pd((double)a[r*4]),pair(b+c));
  x=_mm_add_pd(x,_mm_mul_pd(_mm_set1_pd((double)a[r*4+1]),pair(b+4+c)));
  x=_mm_add_pd(x,_mm_mul_pd(_mm_set1_pd((double)a[r*4+2]),pair(b+8+c)));
  x=_mm_add_pd(x,_mm_mul_pd(_mm_set1_pd((double)a[r*4+3]),pair(b+12+c)));
  _mm_storel_epi64((__m128i*)(d+r*4+c),_mm_castps_si128(_mm_cvtpd_ps(x)));
 }
}
extern "C" void check_hresult(int);
extern "C" int WIN compose(float* result,const float* before,const float* object) {
 unsigned short cw;__asm__ volatile("fnstcw %0":"=m"(cw));
 // The wrapper retains 24-bit nearest mode in this one case; use its path.
 if((cw&0x3f)!=0x3f || (cw&0xf3f)==0x3f || (_mm_getcsr()&0x1f80)!=0x1f80) return 0;
 for(u32 i=0;i<16;i++)if((((const u32*)before)[i]&0x7fffffff)>0x501502f9)return 0;
 for(u32 i=4;i<16;i++)if((((const u32*)object)[i]&0x7fffffff)>0x501502f9)return 0;
 if((((const u32*)object)[38]&0x7fffffff)>0x501502f9)return 0;
 u32 csr=_mm_getcsr();_mm_setcsr((csr&0xffff1fbf)|0x1f80);
 float t[16]={},r[16]={},s[16]={},a[16],b[16];
 t[0]=t[5]=t[10]=t[15]=r[15]=s[15]=1.0f;
 t[12]=object[13];t[13]=object[14];t[14]=object[15];
 for(u32 i=0;i<3;i++)for(u32 j=0;j<3;j++)r[4*i+j]=object[4+3*j+i];
 s[0]=s[5]=s[10]=object[38];
 mul(a,t,before);mul(b,r,a);mul(result,s,b);
 _mm_setcsr(csr);return 1;
}
struct alignas(16) Entry { const float* object; float before[16]; float key[13]; float result[16]; };
static_assert(sizeof(Entry)==192,"cache entry layout");
struct Cache { u32 owner,hits,misses,fallbacks; Entry entries[1024]; };
static bool matches(const Entry* e,const float* before,const float* object) {
 if(e->object!=object || ((const u32*)e->key)[12]!=((const u32*)object)[38])return false;
 __m128i delta=_mm_setzero_si128();
 for(u32 i=0;i<16;i+=4)delta=_mm_or_si128(delta,_mm_xor_si128(_mm_loadu_si128((const __m128i*)(e->before+i)),_mm_loadu_si128((const __m128i*)(before+i))));
 for(u32 i=0;i<12;i+=4)delta=_mm_or_si128(delta,_mm_xor_si128(_mm_loadu_si128((const __m128i*)(e->key+i)),_mm_loadu_si128((const __m128i*)(object+4+i))));
 return _mm_movemask_epi8(_mm_cmpeq_epi8(delta,_mm_setzero_si128()))==0xffff;
}
extern "C" int WIN apply_cached(void* renderer,const float* object,Cache* cache) {
 u32 tid;__asm__ volatile("movl %%fs:0x24,%0":"=r"(tid));
 if(!cache->owner)__sync_val_compare_and_swap(&cache->owner,0,tid);
 if(cache->owner!=tid)return 0;
 unsigned short cw;__asm__ volatile("fnstcw %0":"=m"(cw));
 if((cw&0x3f)!=0x3f || (cw&0xf3f)==0x3f || (_mm_getcsr()&0x1f80)!=0x1f80){cache->fallbacks++;return 0;}
 void* device=*(void**)((char*)renderer+0x600);void** vt=*(void***)device;
 // dgVoodoo 2.53's state-block recording flag. The pinned DLL layout is required.
 void* inner=*(void**)((char*)device+4);
 if(*(unsigned char*)((char*)inner+0x3d0)){cache->fallbacks++;return 0;}
 Transform get=(Transform)vt[12],set=(Transform)vt[11];float before[16];
 if(get(device,1,before)<0){cache->fallbacks++;return 0;}
 Entry* e=&cache->entries[((u32)object>>4)&1023];
 if(matches(e,before,object))cache->hits++;
 else {
  float result[16];if(!compose(result,before,object)){cache->fallbacks++;return 0;}
  cache->misses++;
  for(u32 i=0;i<16;i++){e->before[i]=before[i];e->result[i]=result[i];}
  for(u32 i=0;i<12;i++)e->key[i]=object[4+i];e->key[12]=object[38];e->object=object;
 }
 check_hresult(set(device,1,e->result));return 1;
}
