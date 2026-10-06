# 01 - Tune: thread-count sweep



Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · host `Windows-AMD64` · llama.cpp `b10488`

CPU: **6 physical · 12 logical** cores · `ngl=999` · metric `tg128`



| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 57.3 | 100% |
| 3 | 57.3 | 100% |
| 6 | 57.4 | 100% |
| 12 | 57.3 | 100% |
| 24 | 57.4 | 100% |



**Best**: `-t 6` at 57.4 tok/s

**Slowest tested**: `-t 1` at 57.3 tok/s (1.00x spread)

**Against the physical-core default** (`-t 6`, 57.4 tok/s): 1.00x



Use this in your run:



```bash

LAB_N_THREADS=6 make bench

```



## Your explanation

JSON gốc ở 1/3/6/12/24 thread ghi 57.32/57.34/57.38/57.32/57.37 tok/s. Đổi 1 lên 6 cho 1.0010x, khoảng 0.10%, làm tròn thành 1.00x. Curve phẳng, không có knee rõ và chưa có speedup đáng kể. CUDA offload ngl=999 có thể khiến GPU chi phối decode nên tăng CPU threads ít tác động; chưa đo bandwidth để khẳng định bottleneck. Chênh lệch nhỏ có thể là nhiễu. Giữ 6 thread; kiểm chứng tiếp bằng CPU-only hoặc GPU offload sweep. Không so tg128 trực tiếp với HTTP benchmark khác workload.
