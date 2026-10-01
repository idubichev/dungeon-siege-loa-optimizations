
/* WARNING: Restarted to delay deadcode elimination for space: stack */

undefined4 FUN_1000c029(int param_1,uint param_2,uint param_3)

{
  uint uVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  void *this;
  uint uVar7;
  undefined4 uVar8;
  byte bVar9;
  ushort in_FPUControlWord;
  
  iVar3 = param_1;
  FUN_10005099((int)&param_2 + 3);
  uVar8 = 0x80070057;
  if (((param_3 & 0xf8ffffc0) == 0) && (((byte)param_3 & 0x21) != 0x21)) {
    uVar7 = 1;
    param_1 = 1;
    bVar9 = (param_3 & 0x2000000) != 0;
    if ((bool)bVar9) {
      param_1 = 2;
    }
    if ((param_3 & 0x3000000) != 0) {
      param_1 = 3;
      bVar9 = bVar9 + 1;
    }
    if ((param_3 & 0x4000000) != 0) {
      param_1 = 4;
      bVar9 = bVar9 + 1;
    }
    if ((param_3 & 8) != 0) {
      param_1 = 0;
      bVar9 = bVar9 + 1;
    }
    if (((bVar9 < 2) && (uVar8 = 0x80004001, (param_3 & 6) == 0)) &&
       (uVar8 = 0x887600e1, (*(uint *)(*(int *)(iVar3 + 0x2a4) + 0x218) >> 4 & 1) != 0)) {
      uVar6 = *(uint *)(iVar3 + 0x2b8);
      uVar8 = 0x88760246;
      if (((*(byte *)(iVar3 + 0x3dc) & 0x20) != 0) && (uVar1 = param_2, uVar6 != 0)) {
        while ((uVar1 != 0 && (param_2 != uVar6))) {
          uVar7 = uVar7 + 1;
          uVar6 = *(uint *)(uVar6 + 0x2b8);
          uVar1 = uVar6;
        }
        if (uVar6 != 0) {
          FUN_1000fbdf();
          if (*(char *)(iVar3 + 0x419) != '\0') {
            uVar6 = *(uint *)(iVar3 + 0x38c);
            if (uVar6 == 0) {
              uVar6 = 0x3c;
            }
            (*DAT_10021088)((int)(1000 / (ulonglong)uVar6));
          }
          uVar8 = 0x887601c2;
          if (*(char *)(iVar3 + 0x419) == '\0') {
            uVar8 = 0x887601ae;
            iVar4 = iVar3;
            do {
              if (*(int *)(iVar4 + 0x408) != 0) goto LAB_1000c2f1;
              iVar4 = *(int *)(iVar4 + 0x2b8);
              uVar6 = param_3;
            } while (iVar4 != 0);
            while (param_3 = uVar7, param_3 != 0) {
              uVar8 = *(undefined4 *)(iVar3 + 8);
              uVar5 = *(undefined4 *)(iVar3 + 0x88);
              for (iVar4 = *(int *)(iVar3 + 0x2b8); iVar4 != 0; iVar4 = *(int *)(iVar4 + 0x2b8)) {
                FUN_1000e03b();
                bVar9 = *(byte *)(*(int *)(iVar4 + 0x2b4) + 0xac);
                FUN_1000326a((void *)(uint)bVar9,bVar9);
                (**(code **)(**(int **)(*(int *)(iVar4 + 0x2b4) + 8) + 0x2c))(0,0,1);
                *(undefined4 *)(*(int *)(iVar4 + 0x2b4) + 8) = *(undefined4 *)(iVar4 + 8);
                *(undefined1 *)(*(int *)(iVar4 + 0x2b4) + 0x418) = 1;
                piVar2 = DAT_10026c78;
                *(undefined4 *)(iVar3 + 0x88) = *(undefined4 *)(iVar4 + 0x88);
                if (piVar2 != (int *)0x0) {
                  (**(code **)(*piVar2 + 0x28))
                            (*(undefined4 *)(*(int *)(iVar3 + 0x2a4) + 0xc),
                             *(undefined4 *)(iVar4 + 0x2b4));
                }
                if (*(int *)(iVar4 + 0x2b8) == 0) {
                  FUN_1000e03b();
                  FUN_1000326a(this,*(char *)(iVar4 + 0xac));
                  (**(code **)(**(int **)(iVar4 + 8) + 0x2c))(0,0,1);
                  piVar2 = DAT_10026c78;
                  *(undefined4 *)(iVar4 + 8) = uVar8;
                  *(undefined1 *)(iVar4 + 0x418) = 1;
                  *(undefined4 *)(iVar4 + 0x88) = uVar5;
                  if (piVar2 != (int *)0x0) {
                    (**(code **)(*piVar2 + 0x28))
                              (*(undefined4 *)(*(int *)(iVar3 + 0x2a4) + 0xc),iVar4);
                  }
                }
              }
              uVar6 = param_3 - 1;
              uVar7 = param_3 - 1;
            }
            param_3 = CONCAT22((short)(uVar6 >> 0x10),in_FPUControlWord);
            param_2 = in_FPUControlWord | 0x80000000;
            if ((in_FPUControlWord & 0xf3f) != 0x3f) {
              param_2 = (uint)in_FPUControlWord;
              param_3 = in_FPUControlWord & 0xf0ff | 0x23f;
            }
            uVar8 = 0x80004005;
            uVar5 = FUN_1000f4c1(iVar3,*(int *)(iVar3 + 0x18),*(undefined1 **)(iVar3 + 0x1c),param_1
                                );
            if ((char)uVar5 != '\0') {
              uVar8 = 0;
            }
          }
        }
      }
    }
  }
LAB_1000c2f1:
  FUN_100050d6();
  return uVar8;
}

