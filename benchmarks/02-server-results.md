# 02 - Serve: load test + saturation reading



Host `Windows-AMD64` · llama.cpp `b10488` ·

`--parallel 4` · `ctx=2048` · `threads=6` ·

`ngl=99`



| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 86 | 1.48 | 5200 | 9000 | 13000 | 8.2 | 0.0% |
| 50 | 94 | 1.61 | 28000 | 33000 | 35000 | 37.4 | 0.0% |



*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were

really in flight, regardless of how many users locust simulated. It counts queued requests

too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not

utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*



## What these two runs say



| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **1.09x** (22% of linear) |
| P95 latency | **3.67x** |
| Effective concurrency at 50 users | 37.4 vs `--parallel 4` slots (occupancy/slot ratio 9.34) |



**Saturated.** Throughput delivered only 1.09x for 5x the offered load, and effective concurrency (37.4) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.



Throughput moved 1.09x while P95 moved 3.67x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)



## Your reading

Tăng users 5x chỉ tăng RPS 1.09x, P95 tăng 3.67x. Processing=4, deferred peak=46 hỗ trợ phần latency tăng chủ yếu do queue. Bão hòa ở hoặc trước 50 users; hai mức tải chưa tìm được knee chính xác. Users tăng 5x không đảm bảo arrival rate tăng 5x trong closed-loop Locust. Chọn SLO P95 E2E 10s: load-10 đạt 9s, load-50 không đạt với 33s. Aggregate CSV chưa đủ tính chính xác goodput@10s. Thử admission control/giới hạn concurrency trước để giảm queue; tăng parallel cần kiểm tra VRAM và đo lại. Giảm queue không tự tăng capacity. CSV ghi 86/94 request, console screenshot 88/96; có thể khác thời điểm flush/shutdown nhưng chưa xác nhận. Giữ CSV làm nguồn report, không sửa số theo ảnh. Little's Law trong 60s là ước lượng, không tách queue/compute từng request.
