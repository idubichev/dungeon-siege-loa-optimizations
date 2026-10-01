# Combat XP at 135%

Installed in the optimized DS1 / Legends of Aranna executable for its next launch. The game session that was running during installation was not modified or closed. Save normally and relaunch through Dungeon Siege Optimized.app to activate it.

The native Rules::CalculateExperience return value is multiplied by 1.35 once, after the original damage-based XP calculation and its limits. Enemy XP bookkeeping is unchanged. It works for existing saves and already-spawned enemies without save migration. Previously earned XP is not changed. Direct support-spell casting awards and scripted quest XP are not multiplied by this hook.

The existing used-school-only and attribute rules remain. An action that normally awards 100 Melee XP will award 135 Melee XP, 182.25 Strength XP, 135 Dexterity XP and 135 Intelligence XP before normal storage precision. Other attack schools receive none of that action's school XP.

## Implementation and verification

`build.py` verifies the prior executable hash and six original epilogue bytes. It redirects the shared return at VA 0x5b699d into 23 bytes of unused padding in the existing RX optimization section. The hook multiplies x87 ST(0) by a double-precision 1.35 constant, restores the stack, and executes the original return sequence. It has no absolute addresses and needs no new relocations. Only the hook bytes, the reserved padding, and that section's virtual-size field change.

`verify.py` passed 16 Unicorn x86 emulator cases: zero, fractional and large XP values, original and relocated addresses, preserved caller registers and flags, x87 stack balance, and exact return-stack cleanup. These are isolated code checks, not an in-game gameplay test.

`install.py` atomically replaced the on-disk executable, preserving the running process's old mapped file. It updated both optimized-build manifests, then passed the existing install checker. It did not modify loot, attributes, renderer files, cursor helpers, settings, saves or the live process.

The exact hashes and changed ranges are in `patch.json`; emulator results are in `validation.json`; installation status is in `installed.json`. `backup/` holds the previous DSLOA.exe and both manifests. To revert this installation, close the game and restore those three files together, provided no subsequent binary changes have been installed. Reverting affects future XP, not XP already earned.
