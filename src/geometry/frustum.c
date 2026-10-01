/* Six exact culling-plane tests; keep original code for unsupported precision. */
typedef unsigned U;
U frustum_mask(const float *camera,const float *p,float threshold) {
 unsigned short cw;U oldcsr,csr,mask=0;
 __asm__ volatile("fnstcw %0":"=m"(cw));
 if((cw&0x300)!=0x200 || (cw&63)!=63)return ~0u;
 __asm__ volatile("stmxcsr %0":"=m"(oldcsr));
 csr=(oldcsr&0xffff1fbfu)|((cw<<3)&0x6000);
 __asm__ volatile("ldmxcsr %0"::"m"(csr));
 {
  double x=((double)p[0]-(double)camera[13]);
  double y=((double)p[1]-(double)camera[14]);
  double z=((double)p[2]-(double)camera[15]);
  double dot=(x*(double)camera[37]+z*(double)camera[39])+y*(double)camera[38];
  if(dot>(double)threshold)mask|=8;
 }
 {
  double x=(float)((double)p[0]-(double)camera[7]);
  double y=(float)((double)p[1]-(double)camera[8]);
  double z=(float)((double)p[2]-(double)camera[9]);
  double dot=(x*(double)camera[31]+z*(double)camera[33])+y*(double)camera[32];
  if(dot>(double)threshold)mask|=4;
 }
 {
  double x=(float)((double)p[0]-(double)camera[7]);
  double y=(float)((double)p[1]-(double)camera[8]);
  double z=(float)((double)p[2]-(double)camera[9]);
  double dot=(x*(double)camera[43]+z*(double)camera[45])+y*(double)camera[44];
  if(dot>(double)threshold)mask|=1;
 }
 {
  double x=(float)((double)p[0]-(double)camera[19]);
  double y=(float)((double)p[1]-(double)camera[20]);
  double z=(float)((double)p[2]-(double)camera[21]);
  double dot=(z*(double)camera[48]+y*(double)camera[47])+x*(double)camera[46];
  if(dot>(double)threshold)mask|=2;
 }
 {
  double x=(float)((double)p[0]-(double)camera[16]);
  double y=(float)((double)p[1]-(double)camera[17]);
  double z=(float)((double)p[2]-(double)camera[18]);
  double dot=(z*(double)camera[42]+y*(double)camera[41])+x*(double)camera[40];
  if(dot>(double)threshold)mask|=16;
 }
 {
  double x=(float)((double)p[0]-(double)camera[10]);
  double y=(float)((double)p[1]-(double)camera[11]);
  double z=(float)((double)p[2]-(double)camera[12]);
  double dot=(z*(double)camera[36]+y*(double)camera[35])+x*(double)camera[34];
  if(dot>(double)threshold)mask|=32;
 }
 __asm__ volatile("ldmxcsr %0"::"m"(oldcsr));
 return mask;
}
