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
 if((cw&0xf3f)==0x3f) return 0;
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
extern "C" int WIN apply_transform(void* renderer,const float* object) {
 void* device=*(void**)((char*)renderer+0x600);void** vt=*(void***)device;
 Transform get=(Transform)vt[12],set=(Transform)vt[11];
 float before[16],result[16];
 if(get(device,1,before)<0 || !compose(result,before,object))return 0;
 check_hresult(set(device,1,result));return 1;
}
