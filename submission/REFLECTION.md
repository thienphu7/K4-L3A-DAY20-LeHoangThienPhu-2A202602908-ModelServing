# Reflection — Day 20 Lab (Personal Report)

**Họ Tên:** Lê Hoàng Thiên Phú
**MSSV:** 2A202602908
**Cohort:** K4 (theo tên repo)
**Ngày hoàn thiện báo cáo:** 2026-10-06, UTC+7; chưa xác nhận ngày nộp LMS.

## 1. Hardware & runtime

- OS: Windows 10 x64 theo probe; Python 3.11.16.
- CPU: Intel Core i7-9750H @ 2.60 GHz; 6 physical / 12 logical cores.
- CPU extensions: hardware probe chưa ghi flags. Bonus native configure phát hiện AVX2/FMA/F16C và kiểm tra AVX-512 không đạt; compiler commands thực dùng /arch:AVX2. Không tự sửa hardware.json.
- RAM: 15.9 GB; GPU: GTX 1650, 4096 MiB VRAM; CUDA offload ACTIVE trong screenshot probe.
- Runtime: llama.cpp b10488, llama-b10488-bin-win-cuda-12.4-x64.zip.
- Model: Gemma 4 E2B, LAB_MODEL=gemma4-e2b; primary UD-Q4_K_XL, compare UD-Q2_K_XL.
- Chạy ở đâu: laptop local, không cloud.
- Baseline: threads=6, ngl=999, ctx=2048, max_tokens=64; serve 4 slots. Load report ghi ngl=99. 99/999 yêu cầu full offload, không phải số layer thực tế.

**Setup story:** Dùng lab.ps1 thay make trên PowerShell. Sửa ký tự Unicode gây lỗi encoding runner. Download CUDA timeout một lần, sau đó runtime CUDA và hai GGUF tải thành công. Conda labs cung cấp Python để tạo .venv; runner dùng Python trong .venv.

## 2. Đo lường

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 65195 | 113 / 27129 | 18.2 / 18.4 | 1257 / 28277 / 28277 | 54.9 |
| UD-Q2_K_XL | 2.24 | 4639 | 129 / 66057 | 18.5 / 19.5 | 1298 / 67235 / 67235 | 54.0 |

**Quan sát:** Q2 nhỏ hơn 24.6% nhưng chậm hơn khoảng 1.6%; giữ Q4. Cùng prompt RAM/VRAM và cấu hình, hai response mới đều stop, trả lời đúng ba ý; chưa thấy Q2 giảm chất lượng trên ví dụ này. Một prompt chưa đủ kết luận tổng quát. Với 10 mẫu và outlier request đầu, percentile đuôi chưa ổn định.

## 3. Serving under load

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 1.48 | 5200 | 9000 | 13000 | 8.2 | 0.0% |
| 50 | 1.61 | 28000 | 33000 | 35000 | 37.4 | 0.0% |

- Users tăng 5x; throughput thực tăng 1.09x; P95 tăng 3.67x.
- Effective concurrency 37.4 so với 4 slots; gồm cả request chờ.
- Highest sampled average busy slots 3.52/4; processing peak 4, deferred peak 46.
- Smoke có completion; tokens_predicted_total=532, tăng 20.

**Saturation reading:** RPS gần plateau, P95 tăng mạnh và deferred=46 hỗ trợ queueing. Bão hòa ở hoặc trước 50 users, chưa biết knee chính xác. SLO P95 E2E 10s: 10 users đạt, 50 không đạt. Thử giới hạn concurrency/admission để giảm queue trước. Aggregate CSV không đủ tính goodput@10s chính xác; cần đo mới để chứng minh cải thiện.

**Giới hạn:** CSV ghi 86/94 request còn console cuối 88/96; có thể khác thời điểm flush/shutdown, chưa xác nhận. Report theo CSV nhất quán. Thí nghiệm 60s mixed short/long khiến Little's Law chỉ là ước lượng occupancy. Users tăng không đồng nghĩa arrival rate tăng đúng 5x.

## 4. Integration

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | Localhost, không provision IaC | stub/chưa tích hợp |
| N17 Data pipeline | TOY_DOCS viết sẵn | stub |
| N18 Lakehouse | Danh sách Python trong RAM | stub |
| N19 Vector + features | Keyword overlap, không vector index | stub |
| N20 Serving | HTTP llama-server, inference Gemma | real |

Mean của 3 query: embed 0.0 ms; retrieve 0.1 ms; llm 3109.1 ms; total 3109.2 ms. LLM khoảng 100% sau làm tròn. Cả ba query có context và answer.

**Reflection:** Embedding chưa chạy, retrieval toy nhẹ nên LLM chiếm toàn bộ thời gian. Giảm latency 2x cần kiểm tra HTTP overhead/server timings rồi tối ưu prompt/decode kèm đánh giá chất lượng. Tối ưu retrieve 0.1 ms không đủ. Kết quả không đại diện pipeline RAG production.

## 5. The single change that mattered most

**Change đã đo:** tăng CPU threads từ 1 lên 6, Q4 với CUDA offload, llama-bench tg128.

```text
before: 57.32 tok/s (-t 1)
after: 57.38 tok/s (-t 6)
speedup: 1.0010x (khoảng 0.10%; làm tròn 1.00x)
```

Curve 1/3/6/12/24 threads gần như phẳng. Chưa có thay đổi base nào cho speedup lớn hoặc chắc chắn có ý nghĩa. Giữ 6 thread; so với mặc định best là 1.00x. Không coi chênh lệch 0.10% là tối ưu thành công.

Giả thuyết phù hợp là CUDA offload khiến GPU chi phối decode nên CPU threads ít tác động. Chưa profiling nên không khẳng định bandwidth CPU/GPU bão hòa; khác biệt có thể là nhiễu. CPU-only thread sweep hoặc layer-offload sweep có thể kiểm chứng. Không so tg128 với HTTP bench vì workload khác nhau.

## 6. Bonus

**Đã thực hiện:** B1 source build + prebuilt comparison; B2 GPU-offload sweep; B3 before/after của bonus; B4 challenge C7 native CPU ON/OFF; B5 C9 embedding-serving. C9 không tính B4.

**B1:** build MSVC 19.44.35229.0, x64 Release CPU, GGML_NATIVE=ON tại b10488 (commit 9d77fa17254e1dee4b9e92504c91611a60b1359f). Prebuilt 8.5 tok/s, source native 9.0 tok/s, ratio JSON 1.059 (report 1.06x), cùng Q4, 6 threads, ngl=0, tg128 và 3 repetitions. Hai binaries khác GPU availability nhưng đều chạy CPU. CPU codegen/runtime dispatch có thể góp phần, chưa cô lập toolchain upstream hoặc thermal/order bias nên không quy toàn bộ 5.9% cho AVX2. Chứng cứ: bonus-build-compare-tg128.md/.json, bonus-b1-console.txt, metadata và log build.

**B4/C7:** build thêm cùng source/MSVC Release với GGML_NATIVE=OFF, CUDA/Vulkan OFF. Hai cặp đo 3 reps/invocation theo thứ tự OFF-ON rồi ON-OFF: OFF 10.54/10.45, ON 10.60/10.59 tok/s. Trung bình OFF 10.495, ON 10.595, ratio 1.00953x (0.95%). Curve gần tương đương; chưa kết luận cải thiện có ý nghĩa. Cả hai effective flags đều /arch:AVX2/FMA/F16C, OFF có thêm BMI2 definitions; OFF không phải scalar-only. Compiler command và configure logs được lưu. Đây là khảo sát native detection thực, không Debug/Release hoặc CPU/GPU. Chứng cứ: bonus-c7-native-compare.md/.json và 4 raw logs. Không so số C7 với B1 khác thời điểm để suy ra compiler speedup.

```text
before: 9.12 tok/s, ngl=0, threads=6, Q4, tg128
after: 50.60 tok/s, ngl=99, cùng sweep/workload
speedup: 5.55x
```

Full offload tốt nhất trong grid 0/8/16/24/32/99, không thấy OOM. Chuyển phần decode từ CPU lên GPU là giả thuyết phù hợp cho speedup; chưa đo bandwidth hoặc profiling layer để khẳng định cơ chế chi tiết. Không coi khả năng chạy tg128 là bảo đảm VRAM đủ cho context/parallel lớn. Không so với tune 57.38 tok/s ở lần chạy trước.

C9: batch 1/2/4/8/16 có latency 2340.3/2458.0/2573.1/2892.7/3362.2 ms; throughput hiển thị 0.4/0.8/1.6/2.8/4.8 texts/s. Tính từ latency, batch 16 throughput khoảng 11.14x batch 1, latency 1.44x. Đây là một mẫu mỗi batch, Gemma chat-model pooling, 1536 dimensions, toy corpus 8 docs; chưa chứng minh retrieval quality. Embedding gộp forward passes khác chat decode scheduling; texts/s không so trực tiếp với chat RPS. Số được chép từ screenshot thật vì demo không tự tạo report.

Reports: benchmarks/bonus-gpu-offload-sweep.md và benchmarks/bonus-embedding-serving.md. Screenshots: 09-bonus-gpu-sweep.png, 11-bonus-embedding.png, 11a-bonus-embedding-server.png.

## 7. Điều làm tôi ngạc nhiên nhất

Q2 nhỏ hơn nhưng không nhanh hơn. Tăng CPU threads cũng gần như không ảnh hưởng decode khi CUDA offload.

## 8. Self-check trước khi push

- Đã có reports base và 26 ảnh; nội dung 5 bằng chứng bắt buộc đã được kiểm tra.
- GitHub API xác nhận repo hiện Public khi rà soát. Bài làm mới đang stage, chưa commit/push; chưa xác nhận nộp LMS.
- Tên GitHub cần K4-L3-DAY20-LeHoangThienPhu-2A202602908-ModelServing; thư mục local đang L3A.
- Không commit GGUF, runtime, .venv, .env hoặc secrets.
- Chạy lab.ps1 verify sau stage; commit/push và paste URL LMS trước deadline coach hoặc mặc định 23:59 UTC+7 ngày làm lab.

## 9. Khai báo sử dụng AI

Dùng ChatGPT/Codex để đọc hướng dẫn, debug PowerShell/timeout, sắp xếp screenshots, đối chiếu artifacts và hỗ trợ soạn reports/reflection từ dữ liệu thực. AI không tạo số liệu giả hoặc screenshots. Codex trực tiếp chạy compile và benchmark B1/C7 trên máy local, giữ raw logs/metadata và dùng số đo đó cho báo cáo. Đây là bản hỗ trợ soạn thảo: người nộp cần đọc, kiểm chứng và giải thích được lập luận theo RULES.md trước khi nộp. Đã đối chiếu hai response đầy đủ và ảnh model Q4/Q2; đánh giá chỉ giới hạn một prompt.
