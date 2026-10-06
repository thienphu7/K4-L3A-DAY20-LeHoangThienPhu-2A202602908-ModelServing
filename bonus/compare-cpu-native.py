"""C7: compare two Release CPU builds, with native detection ON and OFF."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib'))
import labkit


def main() -> int:
    model = str(ROOT / labkit.load_active()['primary_model'])
    build_root = ROOT / 'bonus' / 'llama.cpp'
    binaries = {
        'OFF': build_root / 'build-zbaseline' / 'bin' / 'llama-bench.exe',
        'ON': build_root / 'build' / 'bin' / 'llama-bench.exe',
    }
    flags = {}
    for key, binary in binaries.items():
        if not binary.exists():
            raise FileNotFoundError(binary)
        cache = (binary.parents[1] / 'CMakeCache.txt').read_text(encoding='utf-8')
        assert 'CMAKE_BUILD_TYPE:STRING=Release' in cache
        assert f'GGML_NATIVE:BOOL={key}' in cache
        flags[key] = [line for line in cache.splitlines()
                      if line.startswith(('GGML_NATIVE:', 'GGML_AVX', 'GGML_FMA:',
                                          'GGML_F16C:', 'GGML_BMI2:', 'CMAKE_BUILD_TYPE:'))]
    revision = subprocess.check_output(
        ['git', '-C', str(build_root), 'rev-parse', 'HEAD'], text=True).strip()
    rows = []
    # Reverse the second pair to reduce a simple run-order bias.
    for trial, order in enumerate((('OFF', 'ON'), ('ON', 'OFF')), 1):
        for key in order:
            command = [str(binaries[key]), '-m', model, '-t', '6', '-ngl', '0',
                       '-p', '0', '-n', '128', '-r', '3']
            print(f'Trial {trial}, GGML_NATIVE={key}, CPU tg128, 3 reps', flush=True)
            result = subprocess.run(command, capture_output=True, text=True, timeout=1800)
            raw = result.stdout + result.stderr
            log_name = f'bonus-c7-native-{key.lower()}-trial-{trial}.txt'
            (ROOT / 'benchmarks' / log_name).write_text(raw, encoding='utf-8')
            if result.returncode:
                raise RuntimeError(f'{log_name}: exit {result.returncode}')
            rate = labkit.bench_metric(raw, 'tg128')
            if rate <= 0:
                raise RuntimeError(f'No positive throughput in {log_name}')
            rows.append({'trial': trial, 'native': key, 'tok_s': rate, 'raw_log': log_name})
            print(f'  {rate:.2f} tok/s', flush=True)
    averages = {key: sum(r['tok_s'] for r in rows if r['native'] == key) / 2
                for key in binaries}
    ratio = averages['ON'] / averages['OFF']
    table = labkit.md_table(['Pair', 'GGML_NATIVE', 'tg128 (tok/s)'],
                           [[r['trial'], r['native'], f"{r['tok_s']:.2f}"] for r in rows])
    text = f'''# Bonus C7 - Native CPU detection ON vs OFF

Source: b10488, commit `{revision}`. MSVC Release x64, CUDA/Vulkan OFF.
Same Q4 model, 6 CPU threads, ngl=0, tg128, 3 repetitions per invocation.
Two paired invocations per setting; second pair reverses run order.

{table}

Mean of invocation means: OFF {averages['OFF']:.3f}, ON {averages['ON']:.3f} tok/s.
Native/baseline ratio: {ratio:.3f}x. These are measurements, not a guaranteed speedup.

## Build settings recorded

```text
ON:
{chr(10).join(flags['ON'])}

OFF:
{chr(10).join(flags['OFF'])}
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
'''
    labkit.write_report('bonus-c7-native-compare.md', text,
                        {'revision': revision, 'rows': rows, 'means': averages,
                         'native_over_baseline': ratio, 'flags': flags})
    print(text, flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
