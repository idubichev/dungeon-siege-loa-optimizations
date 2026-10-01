typedef unsigned U;
#define W __attribute__((stdcall))
typedef U (W *DllMain)(U,U,U);typedef U (W *GetModule)(const char*);typedef U (W *GetProc)(U,const char*);typedef U (W *Protect)(void*,U,U,U*);typedef U (W *Flush)(U,void*,U);
static __attribute__((always_inline)) U install(unsigned char *target,U prefix,U displacement,Protect protect,Flush flush) {
 if(*(U*)target!=prefix || target[4]!=0xec)return 0;
 U old,ignored;if(!protect(target,5,0x40,&old))return 0;
 target[0]=0xe9;*(U*)(target+1)=displacement;
 U ok=flush(~0u,target,5);U restored=protect(target,5,old,&ignored);return ok&&restored;
}
U W renderer_init(U module,U reason,U reserved) {
 U result=((DllMain)0x33330000)(module,reason,reserved);
 if(!result || reason!=1)return result;
 U kernel=(*(GetModule*)0x11110000)("KERNEL32.DLL");if(!kernel)return 0;
 Protect protect=(Protect)(*(GetProc*)0x22220000)(kernel,"VirtualProtect");
 Flush flush=(Flush)(*(GetProc*)0x22220000)(kernel,"FlushInstructionCache");
 if(!protect || !flush)return 0;
 if(!install((unsigned char*)0x44440000,0x83ec8b55,0x66660000,protect,flush))return 0;
 /* Matrix multiplication begins push ebp; mov ebp,esp; push ecx; push ecx. */
 unsigned char *target=(unsigned char*)0x55550000;if(*(U*)target!=0x51ec8b55 || target[4]!=0x51)return 0;
 U old,ignored;if(!protect(target,5,0x40,&old))return 0;
 target[0]=0xe9;*(U*)(target+1)=0x77770000;U ok=flush(~0u,target,5);U restored=protect(target,5,old,&ignored);
 return ok&&restored?result:0;
}
