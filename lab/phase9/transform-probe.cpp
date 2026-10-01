// Diagnostic reconstruction of the three consecutive object transform calls.
// Interface slots verified against Wine's IDirect3DDevice7 declaration.
#include <xmmintrin.h>
typedef unsigned int u32;
#define WIN __attribute__((stdcall))
#define THIS __attribute__((thiscall))
extern "C" void THIS translation(void*,const float*);
extern "C" void THIS rotation(void*,const float*);
extern "C" void THIS scale(void*,const float*);
typedef int (WIN *Transform)(void*,u32,float*);
struct State { u32 seq,calls,get_failed,identity,left_match,right_match,neither; float before[16],after[16],left[16],right[16],object[40]; };
static void mul(float* d,const float* a,const float* b) {
 for(u32 r=0;r<4;r++) for(u32 c=0;c<4;c++) {
  double x=(double)a[r*4]*(double)b[c];
  x=x+(double)a[r*4+1]*(double)b[4+c];
  x=x+(double)a[r*4+2]*(double)b[8+c];
  x=x+(double)a[r*4+3]*(double)b[12+c];d[r*4+c]=(float)x;
 }
}
static bool equal(const float* a,const float* b) {for(u32 i=0;i<16;i++)if(((const u32*)a)[i]!=((const u32*)b)[i])return false;return true;}
extern "C" void WIN probe(void* renderer,float* object,State* state) {
 void* device=*(void**)((char*)renderer+0x600);void** vt=*(void***)device;
 Transform get=(Transform)vt[12];float before[16],after[16];int hr=get(device,1,before);
 float s[3]={object[38],object[38],object[38]};
 translation(renderer,object+13);rotation(renderer,object+4);scale(renderer,s);
 state->seq++;
 if(hr<0 || get(device,1,after)<0){state->get_failed++;state->seq++;return;}
 u32 csr=_mm_getcsr();_mm_setcsr((csr&0xffff1fbf)|0x1f80);
 float t[16]={},r[16]={},z[16]={},a[16],b[16],left[16],right[16];
 t[0]=t[5]=t[10]=t[15]=r[15]=z[15]=1.0f;t[12]=object[13];t[13]=object[14];t[14]=object[15];
 for(u32 i=0;i<3;i++)for(u32 j=0;j<3;j++)r[4*i+j]=object[4+3*j+i];
 z[0]=z[5]=z[10]=s[0];
 mul(a,t,before);mul(b,r,a);mul(left,z,b);
 mul(a,before,t);mul(b,a,r);mul(right,b,z);
 bool identity=true;for(u32 i=0;i<16;i++)if(before[i]!=(i%5==0?1.0f:0.0f))identity=false;
 bool le=equal(after,left),ri=equal(after,right);
 state->calls++;state->identity+=identity;state->left_match+=le;state->right_match+=ri;state->neither+=!le&&!ri;
 if(state->calls==1 || (!le&&!ri)){
  for(u32 i=0;i<16;i++){state->before[i]=before[i];state->after[i]=after[i];state->left[i]=left[i];state->right[i]=right[i];}
  for(u32 i=0;i<40;i++)state->object[i]=object[i];
 }
 _mm_setcsr(csr);state->seq++;
}
