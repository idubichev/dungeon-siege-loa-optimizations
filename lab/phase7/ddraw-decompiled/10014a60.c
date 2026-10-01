
void __thiscall FUN_100149da(void *this,int param_1,int param_2,undefined4 param_3,char param_4)

{
  bool bVar1;
  int iVar2;
  uint *unaff_EBX;
  int unaff_ESI;
  longlong lVar3;
  undefined8 uVar4;
  int *local_14 [4];
  
  local_14[0] = FUN_10013c19(this,param_1);
  if (local_14[0] != (int *)0x0) {
    (*DAT_10021124)(*(int *)((int)this + 0x10) + 0x17c);
    FUN_1001d246((int)this);
    FUN_1001354f(unaff_EBX);
    if ((param_4 != '\0') && (*(char *)(*(int *)((int)this + 4) + 0x5b) != '\0')) {
      FUN_100138ac((int)this);
    }
    if (param_2 == 0) {
      iVar2 = 0;
    }
    else {
      iVar2 = param_2 + -0xb9c;
    }
    bVar1 = FUN_1001b7da(*(int **)(*(int *)(iVar2 + 0xbbc) + 0x3c6c),
                         *(undefined4 *)(*(int *)(iVar2 + 0xbbc) + 0x3c74),param_3,
                         *(int *)(*(int *)((int)this + 4) + 0x14),
                         *(float *)(*(int *)((int)this + 4) + 0x18));
    FUN_1001d25a();
    if (!bVar1) {
      iVar2 = (*DAT_10021098)(local_14);
      if (iVar2 != 0) {
        iVar2 = *(int *)(unaff_ESI + 4) * 0xc18;
        lVar3 = __allmul(*(uint *)(iVar2 + 0xf50 + (int)this),*(int *)(iVar2 + 0xf54 + (int)this),
                         1000,0);
        uVar4 = __alldiv((uint)lVar3,(uint)((ulonglong)lVar3 >> 0x20),(uint)unaff_EBX,
                         (uint)local_14[0]);
        (*DAT_10021088)((int)uVar4);
      }
    }
  }
  return;
}

