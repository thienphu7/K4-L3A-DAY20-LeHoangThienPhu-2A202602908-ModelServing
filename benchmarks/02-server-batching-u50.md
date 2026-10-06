# 02 - Continuous batching under load (u50)



Host `Windows-AMD64` · `--parallel 4` · 15 samples over

60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`



| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.52 of 4 slots (88%) |
| `requests_processing` | 4 |
| `requests_deferred` | 46 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 11533 |



Highest sampled value was **3.52 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means

requests were served one at a time -- either the load was too light to overlap, or

they arrived too far apart. A peak approaching `--parallel` means the scheduler was

genuinely packing concurrent requests into shared decode steps.

`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.



## Your observation

Highest sampled average busy slots 3.52/4 (88%), processing peak 4 và deferred peak 46 hỗ trợ continuous batching cùng queueing. Gauge là average theo decode step, không phải instantaneous batch width hoặc GPU utilization. Effective concurrency 37.4 gồm request chờ và xử lý, khác phạm vi 3.52 đang decode nên không cần bằng nhau. Dùng gauge server cho batching, Little's Law cho occupancy ước lượng. Mẫu processing=0 ở cuối cho thấy có khoảng idle; không coi toàn bộ thời gian scrape đều có tải.
