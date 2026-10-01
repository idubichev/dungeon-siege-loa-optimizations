typedef unsigned U;typedef unsigned char B;
typedef B (*Original)(const float*,const float*,const float*,const float*,float*);
B raybox(const float *lo,const float *hi,const float *o,const float *dir,float *out) {
 unsigned short cw;__asm__ volatile("fnstcw %0":"=m"(cw));
 if((cw&0x300)!=0x200 || (cw&63)!=63)goto fallback;
 const float *inputs[4]={lo,hi,o,dir};
 for(U j=0;j<4;j++) {
  U a=(U)inputs[j],b=(U)out;if(a<b+12 && b<a+12)goto fallback;
  for(U i=0;i<3;i++)if((((const U*)inputs[j])[i]&0x7f800000)==0x7f800000)goto fallback;
 }
 U old,csr;__asm__ volatile("stmxcsr %0":"=m"(old));csr=(old&0xffff1fbfu)|((cw<<3)&0x6000);__asm__ volatile("ldmxcsr %0"::"m"(csr));
 float candidate[3]={0,0,0},max_t[3];U outside[3]={0,0,0},inside=1;B result=0;
 for(U i=0;i<3;i++) {
  if(o[i]<lo[i]){outside[i]=1;candidate[i]=lo[i];inside=0;}
  else if(o[i]>hi[i]){outside[i]=1;candidate[i]=hi[i];inside=0;}
 }
 if(inside){out[0]=o[0];out[1]=o[1];out[2]=o[2];result=1;goto done;}
 for(U i=0;i<3;i++)max_t[i]=outside[i] && dir[i]!=0.0f ? ((double)candidate[i]-(double)o[i])/(double)dir[i] : -1.0f;
 U best=0;if(max_t[best]<max_t[1])best=1;if(max_t[best]<max_t[2])best=2;
 if(max_t[best]<0.0f)goto done;
 for(U i=0;i<3;i++) {
  if(i==best)out[i]=candidate[i];
  else {double v=(double)max_t[best]*(double)dir[i]+(double)o[i];out[i]=v;if(v<(double)lo[i] || v>(double)hi[i])goto done;}
 }
 result=1;
done:__asm__ volatile("ldmxcsr %0"::"m"(old));return result;
fallback:return ((Original)0x22334455)(lo,hi,o,dir,out);
}
