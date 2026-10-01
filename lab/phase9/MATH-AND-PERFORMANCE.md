# Dungeon Siege: mathematical and performance changes

6 September 2026. Installed release: `phase9/13-transform-cache`, SHA-256 `9c00538f1bea22d9a70d5806d2025d409e3919c087c6ff94e245084a811e9545`. Object detail remains **100%**. DXVK's presentation cap is configured at **120 FPS**. The game and private tests have been closed at the user's request.

This is a collection of small patches to the existing x86 executable and renderer. Ghidra supplied partial C++ reconstruction; we do not have the complete original source. Wine, dgVoodoo, DXVK and MoltenVK remain the rendering stack. SSE/SSE2 instructions still run through the Mac's x86 translation environment; these changes do not move animation or collision work onto the GPU.

## Mathematical changes that are installed

Here `fl32` means rounding/storing a result as a 32-bit float. Equations describe the operation; the implementations retain the original ordering and intermediate stores where required. A mathematically equivalent rearrangement can produce different floating-point bits, so equivalence testing matters.

### 1. Quaternion rotation of vertices and normals

For quaternion `q = (u, w)` and vector `v`, the existing rotation expression is:

`v' = (2w² − 1)v + 2(u·v)u + 2w(u × v)`.

The replacement uses SSE register arithmetic instead of the x87 floating-point stack. Separate supported precision paths preserve the original rounding behavior, with the old path retained for unsupported modes. This speeds repeated vertex and normal rotation without reducing animation detail. The original leaf and its scoped variant each passed 108,000 byte-exact comparisons across nine floating-point modes.

Sources: `../quat-sse.s`, `../phase2/quat-scoped.s`, `../quat-validation.json`.

### 2. Matrix-vector transforms and weighted skinning

Matrix-vector multiplication still evaluates each component as a row/column dot product. Skinning still performs the original sequence equivalent to `destination += weight × (rotated_position + translation)`, including its intermediate float stores. SSE/SSE2 reduces x87 stack traffic and repeated loads; it does not simplify the skeleton or skip bones.

The installed loop also establishes the SSE rounding mode once around a group of vertices instead of repeating that setup per vertex. The later normal-loop patch applies the same idea to indexed normals. The incoming floating-point controls are restored afterward.

Validation: 72,000 matrix-vector comparisons; 108,000 blend comparisons; 9,000 complete scoped skinning-loop comparisons; 14,400 complete indexed normal-loop comparisons. The whole-loop C rewrite and quaternion-to-matrix cache experiments are not part of this release.

Sources: `../vec3-sse.s`, `../blend-sse.s`, `../phase2/scope-prefix.s`, `../phase2/build-static-patches.py`, `../phase8/build-normal-scope.py`.

### 3. Quaternion multiplication and orthonormal bases

Quaternion composition retains the Hamilton product. For `q1 = (u1,w1)` and `q2 = (u2,w2)`:

`vector = w1u2 + w2u1 + u1 × u2`, `scalar = w1w2 − u1·u2`.

The basis routine retains normalization `v / sqrt(v·v)` and its original cross-product sequence. These use SSE2 double arithmetic, original operation order and float stores, with precision/exception guards and fallback. They are not approximate reciprocal-square-root substitutions.

Validation: 80,000 exact quaternion-product comparisons and 144,000 exact basis comparisons, including aliasing and zero-vector handling.

Sources: `../phase2/qmul-sse.c`, `../phase2/ortho-sse.c`.

### 4. Faster quaternion interpolation — the deliberate approximation

Animation uses shortest-path spherical interpolation:

`q(t) = q0 sin((1−t)θ)/sin(θ) + q1 sin(tθ)/sin(θ)`.

A negative dot product flips the second quaternion's contribution so interpolation follows the shorter arc. The fast path computes `θ = 2 asin(sqrt((1−|q0·q1|)/2))`, with a 24-term arcsine series, a sine polynomial through degree 17 and SSE2 square roots/arithmetic. This replaces expensive legacy transcendental work for the supported inputs.

It applies only with masked x87 exceptions, `t` in `[0,1]`, distinct input addresses, both squared quaternion norms in `(0.98,1.02)`, and absolute dot product below `0.9989`. Other cases retain the earlier original/cached interpolation path. A separate second interpolation function retains exact-result caching rather than this approximation.

Validation: 140,000 comparisons, maximum observed quaternion-component error **3.5762786865234375e-7**, below the test tolerance of `3e-6`; 22,470 fallback comparisons were exact. This is an observed test bound, not a formal bound for every possible input. The earlier exact interpolation caches passed 50,000 and 90,000 comparisons respectively.

Source: `../phase6/slerp-fast.c`; results: `../phase6/08-slerp/validation.json`.

### 5. Renderer matrices

The 4×4 product still computes `C[i,j] = Σ A[i,k]B[k,j]` in the original addition order. The replacement uses SSE2 double intermediates and float outputs with matching rounding. Transposition uses register loads/stores/shuffles instead of x87 conversions. Matrix inversion reuses a previous exact result when its cache key matches, retaining original computation on a miss.

Validation: 75,000 exact product comparisons including aliases and return pointers; 72,000 exact transpose comparisons including arbitrary float bits and overlapping layouts; 101,760 exact inverse-cache comparisons including contention.

Sources: `../matmul-sse.s`, `../phase2/transpose-sse.s`; associated validation JSON files are under `../` and `../phase2/`.

### 6. Object transform submission and caching — latest addition

An object previously submitted translation, rotation and uniform scale separately. With current world matrix `W`, the measured order is:

`A = fl32(T × W)`; `B = fl32(R × A)`; `result = fl32(S × B)`.

The new path gets the current world matrix, calculates that same three-step result and submits it once. It deliberately keeps both intermediate float matrices; blindly replacing the sequence with `(S×R×T)×W` could change rounding. It also does not assume `W` is identity: only about 1.7% of the diagnostic calls started with identity.

A fixed 1,024-entry cache, 196,624 bytes including metadata, reuses the result only when the object address, all 16 current-world float words, all 12 rotation/translation words and scale match exactly. Collisions recompute the result. Supported calls run on one owning render thread; state-block recording, unsupported floating-point modes, failed matrix reads and nonfinite/extreme inputs retain the original instruction path. Each successful call still submits the final matrix, even on a cache hit.

This reduces renderer calls and repeated arithmetic. Two live runs reused approximately **96.5–98.0%** of transform calculations. The main measured improvement is for the combined submission/cache change; we cannot isolate a reliable extra FPS contribution from the cache alone.

Validation: 370,186 live original transform sequences matched the derived scalar calculation; 36,000 kernel comparisons across 12 floating-point modes matched output bits; 8,004 cache/output comparisons exercised changing every input word, address reuse, hash collisions and fallbacks. Test comparisons are evidence, not a proof for every renderer state.

Sources: `transform-cache.cpp`, `transform-fallback.s`, `build-transform.py`, `13-transform-cache/*validation.json`. The COM layout was checked against the [Wine IDirect3DDevice7 declaration](https://raw.githubusercontent.com/wine-mirror/wine/master/include/d3d.h) and the installed renderer's disassembly.

### 7. Bounds and visibility

Mesh bounds still perform the same ordered per-axis tests: extend the upper bound when `value > upper`; otherwise extend the lower bound when `value < lower`. SSE comparisons replace x87 comparison/status-word handling in two hot loops. The branch behavior preserves unordered NaN comparisons and signed-zero behavior; this is not an unchecked min/max substitution. **50,000** full-buffer comparisons matched.

Frustum culling retains all six camera-plane dot-product tests, thresholds and visibility-mask bits. Their arithmetic and repeated setup were streamlined; visibility was not made more aggressive. **60,000** exact mask comparisons covered four rounding modes and unusual inputs.

Sources: `../phase6/13-bounds/bounds.s`, `../phase2/frustum-sse.c`.

### 8. Lighting

For a positive light/normal dot product, the loop still computes the equivalent of `255 × min(1, scale × (light_direction·normal))`, then applies the original rounding and color routine. It loads shared light values and establishes floating-point mode once around the vertex group. No light count or lighting detail is reduced.

Validation: 144,000 exact scalar lighting comparisons and 9,000 complete-loop comparisons with identical color bytes.

Source: `../phase2/light-loop.c`.

### 9. Picking and intersection tests

Ray/box intersection retains its candidate-boundary calculation `(boundary − origin)/direction`, selects the original entry candidate and checks the other axes. The ordinary ray/triangle case retains the Möller–Trumbore dot/cross-product calculation, determinant threshold `1e-5` and barycentric tolerances `±0.001`. Register arithmetic replaces x87 work and helper-call overhead.

Unsupported precision, exceptional inputs, overlapping output/input storage and degenerate cases use the original path as appropriate. These improve CPU work involved in picking and related geometric queries; they do not change hitboxes or skip collision checks.

Validation: 90,000 exact ray/box comparisons and 180,000 exact ray/triangle boolean/full-buffer comparisons.

Sources: `../phase2/raybox-sse.c`, `../phase4/triangle-safe.c`.

## Other performance and input changes

The native Mac arrow alone did not remove the old software cursor's background save/restore work. Profiling located the input/display thread holding the shared renderer lock while those surface copies ran. The later patch exits before those copies while preserving the coordination guards. This removed the large cursor-related lock stalls in the measured routes. It does not establish that every streaming or simulation hitch is gone.

The held-click correction and camera-mode tracking retain absolute pointer positioning for gameplay, hide the native cursor for relative middle-button camera movement and restore it on release. These address the center-snap bug. The native arrow replaces the game's contextual cursor artwork.

The release uses checked static EXE/DLL hooks with preserved relocations, separate code/data sections and hashes for five binaries. No frame timer, stack sampler or experimental runtime lock hook is installed. Avoiding diagnostic overhead preserves normal performance but is not a separately quantified engine gain.

`dxgi.maxFrameRate = 120` is configured in the normal and private `dxvk.conf`. The installed DXVK version accepts this option, confirmed by the private launch's effective configuration. The normal launcher successfully loaded Test OP after installation; its 100% detail preference and protected files were checked. The cap is a ceiling, not a promise that dense scenes sustain 120 FPS. DXVK asynchronous rendering was not enabled in this round.

## Measured gains and their limits

| Controlled comparison | Before | After | Interpretation |
|---|---:|---:|---|
| Earlier demanding stationary view: SLERP stage | 57.62 FPS | 83.92 FPS | Large gain in the animation-heavy view |
| Same stage with bounds added | 83.92 FPS | 89.74 FPS | Further improvement; combined change about 55.7% over 57.62 |
| Scoped normal-loop setup, two runs each | 90.93 FPS | 93.72 FPS | About 3.1% average improvement |
| Latest object transform change, two runs each | 91.94 FPS | 95.68 FPS | About 4.1% average improvement |
| Latest prescribed moving route | 84.31 FPS | 85.62 FPS | Small difference; combat/path variation prevents a strong causal claim |

The latest stationary runs were baseline **93.08 / 90.80** and candidate **97.51 / 93.86**. Each starts from the same private checkpoint with 40 seconds of warmup; first runs measured 15 seconds, repeats measured 30. The table uses the arithmetic mean of each build's two run means. These gains are from successive comparisons; percentages should not be added or treated as one controlled vanilla-to-current measurement.

The earlier cursor-copy fix changed a 35-second route's worst frame from **118.82 ms** to **53.17 / 45.76 ms**, and frames above 80 ms from **3** to **0 / 0**. Average cadence changed from **79.56** to **83.68 / 82.49 FPS**. In the latest moving comparison, the worst frame was **47.60 ms** before versus **55.02 ms** after; both had zero frames above 80 ms. The new transform change therefore is not claimed to improve the single worst moving hitch.

Measurements are CPU render-entry cadence paired with active gameplay screenshots, not direct GPU execution timing. Tests used an **800×600 client**, **100% object detail**, existing shadows-off settings and game audio enabled. The stale 1920×1080 INI values do not describe the tested client size. No sustained 110 FPS claim is made for the demanding forest. The user accepted the result and asked to stop further optimization.

A coarse diagnostic attributed roughly 66% of measured main-thread elapsed time to rendering, including about 16% skinning and 18% drawing/transform submission. It includes probe overhead and waits, and is not a complete source-level CPU profile or GPU breakdown. A short memory check found roughly 347–354 MiB RSS; that did not establish RAM exhaustion or rule out every long-session leak.

## Rejected or separate changes

The exact squared-length rewrite passed 180,000 comparisons but did not add a measurable gain when combined with this release, so it is not installed. The streaming sleep reduction from 100 ms to 1 ms was rejected; the original sleep remains. Lower object detail was explicitly declined and was not applied. More rare loot, vendors and the used-school-only XP/1.35 main-attribute modifications remain installed, but are gameplay mods rather than performance optimizations.

Rollback executable and support files: `release-before/`. The pre-cap configurations are `normal-dxvk-before.conf` and `private-dxvk-before.conf`. Installed evidence: `installed-release.json`; normal launch evidence: `23-normal-launch/`; closed-process/protected-file check: `closed-game-and-tests.json`.
