# Bonus C9 / B5 — Embedding serving

Nguồn số liệu: output thật trong submission/screenshots/11-bonus-embedding.png. Transcribe từ ảnh, không chạy lại hay suy diễn số đo mới. Script embedding-serving.py không tự ghi report.

Hardware: i7-9750H, GTX 1650 4 GB, RAM 15.9 GB. Runtime lab CUDA b10488; model lab Gemma 4 E2B chat GGUF ở pooling mode, không phải dedicated embedding model. Endpoint http://localhost:8081/v1/embeddings; vector dim=1536, corpus=8 documents. Không chạy offline.

| Batch texts | Latency (ms) | Throughput (texts/s) |
|--:|--:|--:|
| 1 | 2340.3 | 0.4 |
| 2 | 2458.0 | 0.8 |
| 4 | 2573.1 | 1.6 |
| 8 | 2892.7 | 2.8 |
| 16 | 3362.2 | 4.8 |

Top cosine scores: 0.839 (embedding regime), 0.786 (RadixAttention), 0.737 (speculative decoding). Đây là similarity trên toy corpus, không phải accuracy/hit rate.

## Analysis

Batch 1 lên 16 tăng latency khoảng 1.44x nhưng xử lý 16 texts. Từ latency chưa làm tròn throughput, throughput ratio = 16*2340.3/3362.2 = 11.14x. Cột texts/s chỉ một chữ số thập phân, không lấy 4.8/0.4 để tuyên bố ratio chính xác. Đây là một lần đo mỗi batch, chưa có repetitions/error bars; batch lớn chứa documents lặp trong corpus 8 nên không đại diện mọi production workload.

Embedding xuất vector qua forward/pooling, không lặp sinh token như chat. Gộp texts có thể tận dụng tính toán song song và phân bổ overhead HTTP trên nhiều texts. Chat decode cần scheduler cho request gia nhập/rời theo từng token; khi tăng users 10 lên 50, throughput chat chỉ tăng 1.09x nhưng P95 tăng 3.67x. Không so trực tiếp texts/s với requests/s: input lengths và công việc khác nhau.

Server này vẫn có scheduling slots; cách demo gom texts là batching ở API, không chứng minh mọi text chạy trong một kernel batch hay server không dùng cấu trúc KV nội bộ. Chat-model embeddings chưa được đánh giá retrieval quality. Production nên tách queue/SLO và điều khiển batch theo token cho embedding với decode scheduling của chat; đó là đề xuất, chưa thử autoscaler. Những teaching notes FP8 trong console không phải số đo trên máy này.
