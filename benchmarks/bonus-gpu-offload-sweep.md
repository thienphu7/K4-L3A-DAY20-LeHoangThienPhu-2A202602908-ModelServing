# Bonus - GPU offload sweep

Host `Windows-AMD64` · backend(s) `nvidia_cuda, vulkan` ·
llama.cpp `b10488` · `threads=6` · metric `tg128`

| -ngl | tg128 (tok/s) | vs -ngl 0 | vs best |
|:--|--:|--:|--:|
| 0 | 9.1 | 1.00x | 18% |
| 8 | 10.2 | 1.12x | 20% |
| 16 | 11.9 | 1.31x | 24% |
| 24 | 24.8 | 2.72x | 49% |
| 32 | 26.0 | 2.85x | 51% |
| 99 | 50.6 | 5.55x | 100% |

Best: `-ngl 99` at 50.6 tok/s
-- 5.55x faster than CPU-only.

Where the curve flattens tells you the model ran out of layers to move. Where it
*peaks below* full offload tells you something did not fit and the accelerator
started paying to fetch weights it could not hold.

## Your finding

Với threads=6, Q4 và tg128, ngl=0 đạt 9.12 tok/s; ngl=99 đạt 50.60 tok/s, speedup 5.55x. Full offload tốt nhất trong grid đã đo. Partial offload cải thiện không đều: 16 lên 24 layer tăng 11.95 lên 24.82 tok/s, nhưng 24 lên 32 chỉ tăng lên 26.01. Chưa profiling nên không khẳng định PCIe hay một nhóm layer cụ thể tạo ra bước nhảy.

Giả thuyết là chuyển nhiều tính toán và đọc weights sang GPU giảm phần CPU trên đường decode. Full offload tránh phần tính toán CPU còn lại của partial offload; đây là giải thích phù hợp, chưa có timing từng backend để tách đóng góp. Không thấy lỗi OOM hoặc peak dưới full offload trong sweep. Điều này không đảm bảo đủ VRAM khi context/batch/parallel lớn hơn. ngl=99 là yêu cầu offload tối đa, không phải model có 99 layer. Backend list nvidia_cuda,vulkan là phần cứng được phát hiện; runtime thực tải là CUDA, không phải thí nghiệm CUDA so Vulkan.

50.60 tok/s khác 57.38 tok/s của tune trước: hai lần chạy khác thời điểm, có thể khác nhiệt độ/tải nền. So sánh before/after bonus chỉ dùng các điểm trong chính sweep này. Chưa đo VRAM/RSS hoặc bandwidth nên không gán mọi khác biệt cho memory bandwidth.
