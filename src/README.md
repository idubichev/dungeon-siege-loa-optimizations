# Patch sources

Every routine compiled into the release, grouped by what it does in the game. Addresses are virtual addresses in `DSLOA.exe` (image base `0x400000`) unless the path says `dgvoodoo/`, which means dgVoodoo 2.53's `D3DImm.dll` (image base `0x10000000`). The main [README](../README.md) explains each patch in depth.

| File | Hook site | What it replaces |
|---|---|---|
| [animation/quat-rotate.s](animation/quat-rotate.s) | `0x535f3b` | Quaternion rotation of a vertex or normal |
| [animation/quat-rotate-scoped.s](animation/quat-rotate-scoped.s) | called from the loops below | Same rotation without its own MXCSR setup |
| [animation/fpu-scope-prefix.s](animation/fpu-scope-prefix.s) | `0x69f2ff`, `0x69f76f` | Copies the x87 rounding mode into MXCSR once per loop |
| [animation/blend.s](animation/blend.s) | `0x69f325` | Weighted skinning blend |
| [animation/blend-scoped.s](animation/blend-scoped.s) | inside the skinning loop at `0x69f2ff` | Same blend, loop-scoped |
| [animation/slerp-fast.c](animation/slerp-fast.c) | `0x69fa05` | SLERP without `fsin` or `acos` |
| [animation/slerp-cache.c](animation/slerp-cache.c) | behind `0x69fa05` | Exact-result cache for in-place SLERP |
| [animation/slerp2-cache.c](animation/slerp2-cache.c) | `0x41adf4` | Exact-result cache for four-argument SLERP |
| [animation/quat-multiply.c](animation/quat-multiply.c) | `0x5361ef` | Hamilton product |
| [geometry/bounds.s](geometry/bounds.s) | `0x69f6ed`, `0x69f81a` | Bounding-box growth with `ucomiss` |
| [geometry/frustum.c](geometry/frustum.c) | `0x684d7f` | Six-plane view-frustum test |
| [geometry/vec3-transform.s](geometry/vec3-transform.s) | `0x43e774` | Strided 3×3 transform |
| [geometry/orthonormal-basis.c](geometry/orthonormal-basis.c) | `0x43e82d` | Basis from forward and up vectors |
| [lighting/light-loop.c](lighting/light-loop.c) | `0x6a1132` | Per-vertex diffuse lighting loop |
| [lighting/light.s](lighting/light.s) | fallback inside `0x6a1132` | Single-vertex lighting |
| [picking/ray-box.c](picking/ray-box.c) | `0x64a770` | Slab-method ray/box test |
| [picking/ray-triangle.c](picking/ray-triangle.c) | `0x728343` | Möller–Trumbore ray/triangle test |
| [renderer/transform-cache.cpp](renderer/transform-cache.cpp) | `0x67907e` | One `SetTransform` per object, with a matrix cache |
| [renderer/transform-hook.s](renderer/transform-hook.s) | `0x67907e` | Entry shim and the original three-call fallback |
| [renderer/dgvoodoo/matrix-inverse-cache.c](renderer/dgvoodoo/matrix-inverse-cache.c) | `0x10006e9b` | Exact cache for 4×4 inverse |
| [renderer/dgvoodoo/matrix-multiply.s](renderer/dgvoodoo/matrix-multiply.s) | `0x10006e44` | 4×4 multiply |
| [renderer/dgvoodoo/matrix-transpose.s](renderer/dgvoodoo/matrix-transpose.s) | `0x10006d65`, `0x10006de5` | 4×4 transpose |
| [renderer/dgvoodoo/load-time-hooks.c](renderer/dgvoodoo/load-time-hooks.c) | DLL entry point | Installs the four hooks after the packed DLL unpacks |
| [cursor/cursor-hooks.s](cursor/cursor-hooks.s) | `0x6633ae`, `0x415274` | Cursor draw and window-message entry shims |
| [cursor/native-arrow.c](cursor/native-arrow.c) | called from the shims | Native arrow through `LoadCursor` / `SetCursor` |
| [cursor/surface-copy-skip.s](cursor/surface-copy-skip.s) | `0x662a12` | Skips the software cursor's locked surface copies |

## Conventions

Every patch begins with the same checks: read the x87 control word with `fnstcw`, require all exceptions masked, pick the 24-bit or 53-bit path from the precision field, and copy the rounding mode into MXCSR. Anything it can't reproduce exactly goes to the original code. The constants `0x11223344`, `0x22334455` and `0x55443322` in the sources are placeholders that the build step replaces with real addresses (state blocks in `.dsdata`, the relocated original function, or a return address).

C and C++ files were compiled with:

```
clang -target i686-w64-windows-gnu -O2 -msse2 -mfpmath=sse -ffp-contract=off \
      -fno-vectorize -fno-slp-vectorize -ffreestanding -fno-builtin -fno-stack-protector
```

and assembly files with `clang -target i686-w64-windows-gnu -c`.

## How they were linked into the binaries

A Python PE writer appended a code section (`.dsopt`) and a zeroed data section (`.dsdata`), placed each object file there with a small COFF linker, rebuilt the relocation table, and wrote a 5-byte `jmp` at each hook site after checking the original bytes. Each development phase built on the previous phase's output, so the finished `DSLOA.exe` has one `.dsopt`/`.dsdata` pair per phase. The released result is captured exactly by the BPS files in [`../patches`](../patches).

The phase-by-phase build scripts, the profiling tools and the full working notes are preserved at the [`lab-archive`](https://github.com/idubichev/dungeon-siege-loa-optimizations/tree/lab-archive/lab) tag. The core of the PE writer is [`build-static-patches.py`](https://github.com/idubichev/dungeon-siege-loa-optimizations/blob/lab-archive/lab/phase2/build-static-patches.py), and the COFF linker is [`coff-reference.py`](https://github.com/idubichev/dungeon-siege-loa-optimizations/blob/lab-archive/lab/phase4/coff-reference.py).
