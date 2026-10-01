# General CPU and rendering check

The inspected program is the current Wine10 release, SHA-256 `3b222ce4f8214a182112ef65db869cfe1132f4b3b4ff80999eaefabeb704c919`. Ghidra provides partial reconstruction, not original source. Tests run in the isolated Profile wrapper at the same dense forest checkpoint, 800×600, 100% object detail. Normal saves are not used for automated travel.

## Current-build attribution

A 15-second diagnostic with six coarse wrappers produced 1,234 frames (82.3 CPU render entries/s), no dropped records and no timer nesting errors. These are **main-thread elapsed-time shares**, including instrumentation and any waits inside a function. They are not GPU execution percentages. The release with only one timestamp per frame initially measured 91.55 FPS, so the coarse probe has material overhead.

| Exclusive category | Approximate share of measured wall time |
|---|---:|
| Rendering work outside the instrumented children | 21.13% |
| Object preparation outside skinning and lighting | 7.57% |
| Skinning / animation mesh transforms | 15.59% |
| Lighting | 4.16% |
| Draw path, including transform submission | 17.94% |
| Game update outside rendering | 24.21% |
| Outside the game-update wrapper | 9.40% |

Rendering totals 66.39%; it is the parent of the first five rows, not an additional cost. Inclusive and exclusive values are retained in `03-coarse-profile/timing.json`. The 15-second native sample on the uninstrumented current release independently found repeated stacks returning from quaternion normal transforms at `0x69f7b2` and the blend/SLERP loop at `0xaafa32`. Native unwinding under Wine/Rosetta is incomplete; sample addresses are leads, not complete or exact leaf CPU percentages.

Process RSS was approximately 347–354 MiB on fresh checkpoint loads. During the native sample it went from 347.36 to 344.34 MiB. This short check does not establish absence of a longer-term leak; it supplies no evidence that RAM capacity explains the steady dense-scene cost.

## Normal-loop candidate

`build-normal-scope.py` rebases on the current cursor-fixed release. The indexed loop at `0x69f76f–0x69f7bb` calls the quaternion transform once per normal. The existing optimized leaf saves MXCSR, reconciles rounding with x87, and restores MXCSR on every call. The candidate performs that setup and restoration once per nonempty loop and reuses the already validated scoped leaf. No cache, changed model detail, new allocation or approximation is introduced. The x87 precision fallback remains.

Validation (`05-normal-scope/validation.json`): 14,400 complete-loop comparisons, 1–64 indexed normals, duplicate indices, 12 x87 precision/rounding combinations, differing incoming MXCSR modes and flags, and 3,600 arbitrary-bit cases including NaN/infinity/subnormal values. All output buffer bits and loop counters match the current implementation. MXCSR and the x87 control word are preserved.

The first short pair measured 91.55 versus 95.43 FPS, but nearby combat timing differed. It is exploratory evidence only. The settled-scene repeats (40-second warmup, then 15 seconds of measurement) measured baseline 90.91 / 90.95 FPS and candidate 92.12 / 95.32 FPS: an average 3.06% improvement, with run-to-run variability. The matching screenshots show the same forest view. Runs 08 and 09 completed their timing and screenshots but the optional post-timing scene-count helper used an incorrect path; that helper path was corrected for subsequent runs. This failure does not affect the already collected timestamp arrays. The candidate was subsequently installed after the validation and moving checks below.

## Draw-path findings and next targets

Ghidra exports under `decompiled/` show `0x67901a` submitting translation (`0x65fd3b`), rotation (`0x65fd97`) and scale (`0x65fe08`) separately for each object. Each constructs a 4×4 matrix and invokes the renderer interface through vtable offset `0x38`. These routines have renderer-state side effects; they are not pure math functions eligible for a simple result cache.

The next larger investigation is to identify the exact transform-interface operation, measure the three submissions separately, and evaluate whether the consecutive operations can be combined while retaining the original multiplication order, precision, error behavior and final renderer state. This has not been implemented or claimed as a speedup.

Draw batching also requires mapping material, transparency and ordering constraints. Visibility work requires proving that skipped objects cannot affect shadows, animation state, picking or later passes. Neither should be changed solely because an object appears offscreen. GPU presentation timing remains unmeasured.

The additional C++ analysis exports are in `recovered-cpp/`. Class and method names are explicitly inferred; calling conventions and parameter storage were retained in Ghidra.

## Moving check

The baseline and first candidate 35-second walks measured 82.23 and 81.80 FPS, respectively; neither recorded a frame above 80 ms. The candidate's 99th-percentile frame was 16.94 ms versus 18.83 ms, while its single worst frame was 53.27 versus 48.67 ms. These walks reach different positions because of combat and path timing, as the after-images show. They are useful regression/behavior checks, but do not demonstrate an overall moving-FPS gain or a controlled tail-latency improvement.

The live virtual-method lookup resolved the transform submission entry to `D3DImm.DLL+0x1cb13`. Its small wrapper forwards to `D3DImm.DLL+0x119a4`. This lookup reads memory only; no DLL patch or runtime import hook was used.

The second candidate walk measured 83.63 FPS, p99 17.45 ms and one 86.84 ms frame. The remaining hitch is recorded explicitly; this change does not claim stutter-free travel.

## Installed result

The numerically validated candidate is installed in the normal launcher. DSLOA.exe SHA-256: `0e33eaf33112467da7cafc26cb33600c0526f8b56f65fd5312c3f29433a49f3c`. The release has 22 jump hooks (18 EXE, 4 renderer) and one direct cursor patch. No timing wrapper or frame logger is installed. The private wrapper was restored to the same unprofiled executable. The previous normal release and support manifests are backed up under `release-before/`.

The normal launcher cold-started, loaded the preserved `Test OP` save and was left paused. Original saves and the original executable matched their protected hashes; both OP packages and all four renderer DLLs remain unchanged. See `14-normal-launch/` and `installed-release.json`.
