typedef unsigned U;
typedef unsigned char B;
extern B original_triangle(const float*,const float*,const float*,const float*,const float*,float*,float*,float*);
static int finite(float f) { union {float f;U u;} x={f};return (x.u&0x7f800000)!=0x7f800000; }
static int bounded(float f) { union {float f;U u;} x={f};return (x.u&0x7fffffff)<=0x501502f9u; } /* abs <= 1e10f */
static int overlap(const void *a,U na,const void *b,U nb) {return (U)a<(U)b+nb && (U)b<(U)a+na;}
static void cross(float *o,const float *a,const float *b) {
 o[0]=(double)b[2]*a[1]-(double)b[1]*a[2];
 o[1]=(double)b[0]*a[2]-(double)b[2]*a[0];
 o[2]=(double)b[1]*a[0]-(double)b[0]*a[1];
}
static double dot(const float *a,const float *b) {return ((double)a[2]*b[2]+(double)a[1]*b[1])+(double)a[0]*b[0];}
B triangle_fast(const float *origin,const float *dir,const float *a,const float *b,const float *c,float *distance,float *u,float *v) {
 unsigned short cw;__asm__ volatile("fnstcw %0":"=m"(cw));
 if((cw&0x300)!=0x200 || (cw&63)!=63)goto fallback;
 const float *inputs[5]={origin,dir,a,b,c};float *outputs[3]={distance,u,v};
 for(U i=0;i<5;i++) {
  for(U j=0;j<3;j++)if(!bounded(inputs[i][j]))goto fallback;
  for(U j=0;j<3;j++)if(overlap(inputs[i],12,outputs[j],4))goto fallback;
 }
 if(overlap(distance,4,u,4)||overlap(distance,4,v,4)||overlap(u,4,v,4))goto fallback;
 U old,csr;__asm__ volatile("stmxcsr %0":"=m"(old));csr=(old&0xffff1fbfu)|0x1f80u|((cw<<3)&0x6000);__asm__ volatile("ldmxcsr %0"::"m"(csr));
 float e1[3],e2[3],p[3],t[3],q[3];
 for(U i=0;i<3;i++){e1[i]=(double)b[i]-a[i];e2[i]=(double)c[i]-a[i];}
 cross(p,dir,e2);
 for(U i=0;i<3;i++)if(!finite(e1[i])||!finite(e2[i])||!finite(p[i]))goto restore_fallback;
 double determinant=dot(e1,p);
 if(__builtin_fabs(determinant)<(double)0.00001f)goto restore_fallback;
 float inverse=1.0/determinant;
 for(U i=0;i<3;i++)t[i]=(double)origin[i]-a[i];
 double uf=dot(t,p)*(double)inverse;
 if(!finite((float)uf))goto restore_fallback;
 *u=uf;
 B result=0;
 if(uf<(double)-0.001f || uf-1.0>(double)0.001f){*distance=0;goto done;}
 cross(q,t,e1);
 double vf=dot(q,dir)*(double)inverse;
 *v=vf;
 if(vf<(double)-0.001f || (vf+(double)*u)-1.0>(double)0.001f){*distance=0;goto done;}
 *distance=dot(e2,q)*(double)inverse;result=1;
done:
 __asm__ volatile("ldmxcsr %0"::"m"(old));return result;
restore_fallback:
 __asm__ volatile("ldmxcsr %0"::"m"(old));
fallback:
 return original_triangle(origin,dir,a,b,c,distance,u,v);
}
