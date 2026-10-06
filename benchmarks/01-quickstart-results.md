# 01 - Measure: latency baseline



Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488`

Settings: `threads=6` `ngl=999` `ctx=2048`

`max_tokens=64` · warm-up discarded

Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10



| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 65195 | 113 / 27129 | 18.2 / 18.4 | 1257 / 28277 / 28277 | 54.9 |
| UD-Q2_K_XL | 2.24 | 4639 | 129 / 66057 | 18.5 / 19.5 | 1298 / 67235 / 67235 | 54.0 |



- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.

- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.

- `UD-Q2_K_XL` and `UD-Q4_K_XL` decode within 2% of each other here, for 0.73 GB difference on disk.



## Your observation

Q2 giảm 0.73 GB (24.6%) nhưng decode 54.0 thay vì 54.9 tok/s, chậm hơn khoảng 1.6%; TPOT P50 18.5 thay vì 18.2 ms. Giữ Q4 vì máy đủ RAM và Q2 chưa cho lợi ích tốc độ. Hai response mới được lưu trong submission/quality-Q4.txt và quality-Q2.txt, có ảnh launcher đúng GGUF. Cùng prompt, temperature=0, seed=42, max_tokens=512; cả hai finish_reason=stop và trả lời đúng RAM hệ thống, VRAM GPU, không cộng thành 20 GB VRAM. Chưa thấy suy giảm chất lượng Q2 rõ trong câu hỏi này. Cách mô tả VRAM chỉ dành đồ họa còn đơn giản hóa: GPU cũng dùng VRAM cho inference. Một prompt chưa chứng minh chất lượng tổng quát hoặc tương đương trên tác vụ khó. Request đầu là outlier TTFT ở cả hai quantization. Chỉ 10 mẫu nên P95/P99 nhạy với outlier; nguyên nhân khởi tạo/cache là giả thuyết, chưa profiling xác nhận.
