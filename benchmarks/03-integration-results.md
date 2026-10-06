# 03 - Integrate: RAG pipeline run



Host `Windows-AMD64` · llama.cpp `b10488` ·

retrieval backend: **keyword overlap** · 3 queries



| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.0 | 3243.8 | 3243.9 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 3043.4 | 3043.5 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.2 | 3040.1 | 3040.3 |



Mean per stage (ms): embed **0.0** · retrieve **0.1** ·

llm **3109.1** · total **3109.2**

Dominant stage: **llm** (100% of total)



## Answers returned



**Why is goodput more useful than raw throughput?**



> Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.



**What problem does PagedAttention actually solve?**



> PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.



**When does splitting prefill and decode help?**



> Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.





## Which N16-N19 pieces are real

N16: stub/chưa tích hợp, chạy localhost không IaC. N17: stub, TOY_DOCS viết sẵn không ingestion. N18: stub, danh sách Python trong RAM không lakehouse. N19: stub, keyword overlap không embedding model/vector index. N20: real, HTTP tới llama-server và inference GGUF. Embed 0.0 ms vì không có embedding endpoint, không phải embedding thật miễn phí. Retrieval 0.1 ms trên toy corpus nên LLM 3109.1/3109.2 ms chiếm khoảng 100%. Muốn giảm tổng latency 2x cần kiểm tra HTTP/client overhead so với server timings và tối ưu prompt/decode kèm đánh giá chất lượng; tối ưu retrieval không đủ. Chưa có phép đo bật/tắt prefix cache. Kết quả không đại diện RAG production; câu trả lời model là output, không phải kiểm chứng độc lập nội dung toy context.
