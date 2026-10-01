# Tests

Each patch was tested by running the game's original routine and the replacement side by side on the same inputs, then comparing the outputs bit for bit.

- `harness/` has one script per patch. They run under 32-bit Windows Python inside Wine, load both routines into executable memory with `VirtualAlloc`, call them through `ctypes`, and sweep random values, random bit patterns, NaN, infinity, signed zeros, subnormals and overlapping buffers across every x87 precision and rounding mode.
- `results/` has the output of each run: case counts, modes covered, and any mismatches.

The harnesses expect two inputs next to them: the original routine's bytes, extracted from your own `DSLOA.exe` (or `D3DImm.dll`) at the hook address, and the compiled patch. The original bytes are game code and aren't included here, so the scripts document the method rather than running from a fresh clone.

| Patch | Result | Cases |
|---|---|---:|
| Bone rotation | [quat-rotate.json](results/quat-rotate.json) | 108,000 |
| Bone rotation, loop variant | [quat-rotate-scoped.json](results/quat-rotate-scoped.json) | 108,000 |
| Weighted blend | [blend.json](results/blend.json) | 108,000 |
| Weighted blend, loop variant | [blend-scoped.json](results/blend-scoped.json) | 108,000 |
| Full skinning loop | [skinning-loop.json](results/skinning-loop.json) | 9,000 |
| Full normal loop | [normal-loop.json](results/normal-loop.json) | 14,400 |
| SLERP fast path | [slerp-fast.json](results/slerp-fast.json) | 140,000 |
| SLERP cache, in place | [slerp-cache.json](results/slerp-cache.json) | 50,000 |
| SLERP cache, four arguments | [slerp2-cache.json](results/slerp2-cache.json) | 90,000 |
| Strided transform | [vec3-transform.json](results/vec3-transform.json) | 72,000 |
| Quaternion multiply | [quat-multiply.json](results/quat-multiply.json) | 80,000 |
| Orthonormal basis | [orthonormal-basis.json](results/orthonormal-basis.json) | 144,000 |
| Frustum culling | [frustum.json](results/frustum.json) | 60,000 |
| Bounding boxes | [bounds.json](results/bounds.json) | 50,000 |
| Lighting, single vertex | [light.json](results/light.json) | 144,000 |
| Lighting, full loop | [light-loop.json](results/light-loop.json) | 9,000 |
| Ray/box | [ray-box.json](results/ray-box.json) | 90,000 |
| Ray/triangle | [ray-triangle.json](results/ray-triangle.json) | 180,000 |
| Transform kernel | [transform-kernel.json](results/transform-kernel.json) | 36,000 |
| Transform cache | [transform-cache.json](results/transform-cache.json) | 8,004 |
| dgVoodoo inverse cache | [matrix-inverse-cache.json](results/matrix-inverse-cache.json) | 101,760 |
| dgVoodoo multiply | [matrix-multiply.json](results/matrix-multiply.json) | 75,000 |
| dgVoodoo transpose | [matrix-transpose.json](results/matrix-transpose.json) | 72,000 |
| Cursor behaviour (in game) | [cursor.json](results/cursor.json) | |

The transform kernel was also checked against 370,186 transform sequences recorded from live play.
