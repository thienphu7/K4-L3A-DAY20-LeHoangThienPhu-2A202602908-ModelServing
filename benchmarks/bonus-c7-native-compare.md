# Bonus C7 - Native CPU detection ON vs OFF

Source: b10488, commit `9d77fa17254e1dee4b9e92504c91611a60b1359f`. MSVC Release x64, CUDA/Vulkan OFF.
Same Q4 model, 6 CPU threads, ngl=0, tg128, 3 repetitions per invocation.
Two paired invocations per setting; second pair reverses run order.

| Pair | GGML_NATIVE | tg128 (tok/s) |
|:--|--:|--:|
| 1 | OFF | 10.54 |
| 1 | ON | 10.60 |
| 2 | ON | 10.59 |
| 2 | OFF | 10.45 |

Mean of invocation means: OFF 10.495, ON 10.595 tok/s.
Native/baseline ratio: 1.010x. These are measurements, not a guaranteed speedup.

## Build settings recorded

```text
ON:
CMAKE_BUILD_TYPE:STRING=Release
GGML_AVX:BOOL=OFF
GGML_AVX2:BOOL=OFF
GGML_AVX512:BOOL=OFF
GGML_AVX512_BF16:BOOL=OFF
GGML_AVX512_VBMI:BOOL=OFF
GGML_AVX512_VNNI:BOOL=OFF
GGML_AVX_VNNI:BOOL=OFF
GGML_BMI2:BOOL=OFF
GGML_NATIVE:BOOL=ON

OFF:
CMAKE_BUILD_TYPE:STRING=Release
GGML_AVX:BOOL=ON
GGML_AVX2:BOOL=ON
GGML_AVX512:BOOL=OFF
GGML_AVX512_BF16:BOOL=OFF
GGML_AVX512_VBMI:BOOL=OFF
GGML_AVX512_VNNI:BOOL=OFF
GGML_AVX_VNNI:BOOL=OFF
GGML_BMI2:BOOL=ON
GGML_NATIVE:BOOL=OFF
```

## Interpretation

The native configure log detects AVX2/FMA/F16C and rejects AVX-512 on this host.
The OFF configure log also enables /arch:AVX2 by default, plus BMI2 definitions.
Therefore OFF does not mean scalar-only, and this experiment does not isolate AVX2
on versus off. The two settings choose similar vector paths; runtime dispatch,
memory traffic and thermal/run-order variation can make results close or make OFF
win. Cache flags alone do not describe all effective flags after native detection;
the configure logs record the effective backend definitions.

This tests the requested C7 native-detection choice, not Debug versus Release or
CPU versus CUDA. A non-speedup is a valid finding. Without hardware profiling,
throughput alone cannot prove bandwidth saturation or attribute a gap to one ISA.
Raw benchmark logs are retained for every invocation. Means of two invocations
are descriptive; no confidence interval or statistical significance is claimed.

## Observed result and provenance

The mean ON/OFF ratio is 1.00953x, about 0.95% higher for native; the two native invocation means were 10.60 and 10.59 tok/s, OFF 10.54 and 10.45. This small difference does not establish a practically significant optimization. Native wins in these pairs, but repetitions and thermal control are too limited for a general conclusion.

Raw benchmark output reports CPU backend on both binaries and build commit 9d77fa1. The displayed build number (1) comes from the shallow source checkout history; the checked-out tag is b10488 and the full commit is retained in metadata. Neither binary is a Debug build. Effective compiler commands are in bonus-c7-build-compile-flags.json and bonus-c7-build-zbaseline-compile-flags.json; configure/build logs are also retained. A standalone CPU feature counter or profiler was not used. Compare the two C7 builds within this session; do not substitute the separate B1 measurement as a C7 baseline.

### Reproduction on this Windows host

```powershell
powershell -ExecutionPolicy Bypass -File bonus/build-cpu-windows.ps1 -Native ON
powershell -ExecutionPolicy Bypass -File bonus/build-cpu-windows.ps1 -Native OFF
$env:PYTHONUTF8 = '1'
$env:LAB_N_THREADS = '6'
.\.venv\Scripts\python.exe bonus/compare-cpu-native.py
```

Both build scripts must finish, and lab servers should be stopped, before benchmarking. Compiler paths in the helper match this host's installed Visual Studio Build Tools.
