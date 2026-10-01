/* Shortest-path quaternion interpolation, with SSE2 scalar polynomial math. */
#include <emmintrin.h>
extern void original_slerp(float *,const float *,float);
static double root(double x) { return _mm_cvtsd_f64(_mm_sqrt_sd(_mm_setzero_pd(),_mm_set_sd(x))); }
/* asin on [0,sqrt(.5)]; 24 terms leave < 2e-10 radians truncation error. */
static double arcsine(double x) {
    double x2=x*x,term=x,sum=x;
    for (int n=1;n<24;n++) {
        double m=2*n-1;
        term*=x2*m*m/((2*n)*(2*n+1.0));sum+=term;
    }
    return sum;
}
static double sine(double x) {
    double z=x*x;
    return x*(1+z*(-1.0/6+z*(1.0/120+z*(-1.0/5040+z*(1.0/362880+z*(-1.0/39916800+z*(1.0/6227020800+z*(-1.0/1307674368000+z/355687428096000.0))))))));
}
void slerp_fast(float *a,const float *b,float t) {
    unsigned short cw;__asm__ volatile("fnstcw %0":"=m"(cw));
    if ((cw&63)!=63 || !(t>=0 && t<=1) || a==b) goto fallback;
    double av[4],bv[4],na=0,nb=0;
    for (int i=0;i<4;i++) { av[i]=a[i];bv[i]=b[i];na+=av[i]*av[i];nb+=bv[i]*bv[i]; }
    if (!(na>.98 && na<1.02 && nb>.98 && nb<1.02)) goto fallback;
    double dot=((av[0]*bv[0]+av[3]*bv[3])+av[2]*bv[2])+av[1]*bv[1];
    double sign=1;if (dot<0) {dot=-dot;sign=-1;}
    if (!(dot<.9989)) goto fallback;
    double angle=2*arcsine(root((1-dot)*.5));
    double denominator=root(1-dot*dot);
    double wa=sine((1-(double)t)*angle)/denominator;
    double wb=sign*sine((double)t*angle)/denominator;
    for (int i=0;i<4;i++) a[i]=(float)(av[i]*wa+bv[i]*wb);
    return;
fallback:original_slerp(a,b,t);
}
