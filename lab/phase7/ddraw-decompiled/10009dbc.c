
undefined4 focus_10009dbc(void)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint unaff_EDI;
  
  while (DAT_10026c1b == '\0') {
    if (DAT_10026c74 == '\0') {
      iVar2 = (*DAT_1002107c)(DAT_10026c6c,1000);
      if ((iVar2 == 0) && (iVar2 = (*DAT_10021064)(PTR_DAT_10026c58), iVar2 != 0)) {
        uVar3 = 0;
        if (unaff_EDI < DAT_10026c4c) {
          do {
            uVar1 = *(uint *)(*(int *)(DAT_10026c48 + uVar3 * 4) + 0x210);
            if (uVar1 != unaff_EDI) {
              (*DAT_1002122c)(uVar1,0x404,0x44454745);
            }
            uVar3 = uVar3 + 1;
          } while (uVar3 < DAT_10026c4c);
        }
        (*DAT_10021128)(PTR_DAT_10026c58);
      }
    }
    else {
      (*DAT_10021088)(1);
    }
  }
  (*DAT_10021078)();
  DAT_10026c70 = unaff_EDI;
  return 0;
}

