typedef unsigned U;
#define F(off) (*(float*)(frame+(off)))
#define I(off) (*(U*)(frame+(off)))
typedef void (*Slerp)(U*,const U*,U);
static __attribute__((always_inline)) int overlap(U a,U na,U b,U nb){return a<b+nb && b<a+na;}
U skin_loop(char *frame,char *object,U *weights) {
 unsigned short cw;__asm__ volatile("fnstcw %0":"=m"(cw));if((cw&0x300)!=0x200 || (cw&63)!=63)return 0;
 U *end=(U*)I(-8);if(weights>=end)return 0;U max=0;for(U *it=weights;it<end;it+=2)if(it[0]>max)max=it[0];if(max>1048576)return 0;
 U vin=I(-16),vout=I(-36),normal=I(-68),vs=(max+1)*12,ns=(max+1)*16,ws=(U)end-(U)weights;
 if(vin+vs<vin || vout+vs<vout || normal+ns<normal)return 0;
 if(overlap(vin,vs,(U)frame-256,288)||overlap(vout,vs,(U)frame-256,288)||overlap(vout,vs,(U)weights,ws))return 0;
 if(*(int*)(object+240)<=0 && (overlap(normal,ns,vin,vs)||overlap(normal,ns,vout,vs)||overlap(normal,ns,(U)weights,ws)||overlap(normal,ns,(U)frame-256,288)))return 0;
 U old,csr;__asm__ volatile("stmxcsr %0":"=m"(old));csr=(old&0xffff1fbfu)|((cw<<3)&0x6000);__asm__ volatile("ldmxcsr %0"::"m"(csr));
 double qx=F(-172),qy=F(-168),qz=F(-164),qw=F(-160),w2=qw+qw,factor=w2*qw-1.0;
 double tx=F(-104),ty=F(-100),tz=F(-96);
 for(U *it=weights;it<end;it+=2) {
  U index=it[0];float weight=*(float*)(it+1);float *v=(float*)vin+index*3,*o=(float*)vout+index*3;double x=v[0],y=v[1],z=v[2];
  double dot=(z*qz+y*qy)+x*qx;dot=dot+dot;
  float rx=((z*qy-y*qz)*w2+factor*x)+dot*qx;
  float ry=((x*qz-z*qx)*w2+factor*y)+dot*qy;
  float rz=((y*qx-x*qy)*w2+factor*z)+dot*qz;
  float bx=((double)rx+tx)*(double)weight;
  float by=((double)ry+ty)*(double)weight;
  float pre_z=(double)rz+tz;float bz=(double)pre_z*(double)weight;
  o[0]=(double)bx+(double)o[0];o[1]=(double)by+(double)o[1];o[2]=(double)bz+(double)o[2];
  I(-28)=index;F(-88)=weight;F(-80)=bx;F(-76)=by;F(-72)=bz;
 }
 if(*(int*)(object+240)<=0)for(U *it=weights;it<end;it+=2)((Slerp)0x22334455)((U*)normal+it[0]*4,(const U*)(frame-172),it[1]);
 __asm__ volatile("ldmxcsr %0"::"m"(old));return 1;
}
