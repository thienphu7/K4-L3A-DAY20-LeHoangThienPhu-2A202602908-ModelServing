# Bonus B1 - Prebuilt vs source build

Host `Windows-AMD64` · CPU `Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz`
Vector extensions detected: none
llama.cpp `b10488` both sides · `threads=6` ·
**both pinned to `ngl=0`** to compare CPU builds without GPU offload ·
metric `tg128`, 3 repetitions

> **Backend mismatch, handled.** The prebuilt binary sees
> `['CUDA0: NVIDIA GeForce GTX 1650 (4095 MiB, 3292 MiB free)']` and your source build sees `(no devices)`.
> Left at `-ngl 99` this comparison would have measured the accelerator and printed
> it under a compiler headline, so both sides were pinned to `-ngl 0`.

| Binary | Built for | tg128 (tok/s) | Relative |
|:--|--:|--:|--:|
| prebuilt release | runtime CPU dispatch | 8.5 | 1.00x |
| your source build | this CPU (`-DGGML_NATIVE=ON`) | 9.0 | 1.06x |

On this machine, the source build is **1.06x faster**.

before: 8.5 tok/s (prebuilt release)
after:  9.0 tok/s (source build, -DGGML_NATIVE=ON)
speedup: 1.06x

Same source revision, model, CPU execution and ngl; this compares prebuilt and local source builds. Upstream compiler options/toolchain are not fully controlled, so a single-flag causal interpretation is not justified.



## Your explanation

Source CPU Release MSVC 19.44.35229.0 được build tại revision b10488 (9d77fa17254e1dee4b9e92504c91611a60b1359f), GGML_NATIVE=ON, CUDA/Vulkan OFF. Configure log phát hiện AVX2/FMA/F16C và AVX-512 không đạt. Dòng generated "Vector extensions detected: none" chỉ phản ánh hardware.json thiếu trường extensions trên Windows, không phải CPU không hỗ trợ SIMD. Lệnh benchmark được ghi trong bonus-b1-console.txt; hai phía cùng Q4, 6 threads, ngl=0 và tg128, 3 repetitions. Source build target llama-bench đã compile thành công; không cần server source cho phép đo này.

Bản native 9.0 tok/s so với prebuilt 8.5 cho ratio 1.059 trong JSON, khoảng 5.9% (report làm tròn 1.06x). Điều này phù hợp giả thuyết codegen/backend CPU của source build khác release và có lợi cho workload này. Không chứng minh AVX2 riêng lẻ tạo ra 5.9% vì prebuilt có CPU runtime dispatch, toolchain upstream chưa được kiểm soát, và chưa đo bandwidth/counters. Đây là so sánh hai bản phân phối/build cùng revision, không thí nghiệm một compiler flag hoàn toàn cô lập. Thermal, load nền và thứ tự prebuilt trước có thể gây lệch; không có confidence interval.

Giữ số thực kể cả mức tăng nhỏ. Phép đo ghim CPU tránh nhầm speedup GPU 5.55x trong sweep trước với speedup build 1.06x. Challenge C7 tiếp theo so hai source builds cùng MSVC, Release và backend, ON/OFF native detection, để kiểm tra hẹp hơn tác động cấu hình CPU. CMake flags và log compile được lưu; build artifacts nằm trong gitignore. Benchmark không hỗ trợ --version ở revision này, nên dòng usage trong console không dùng làm chứng cứ version; source revision và release manifest được dùng thay.
