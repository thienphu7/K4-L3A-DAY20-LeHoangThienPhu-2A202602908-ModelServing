# Bonus evidence checklist

| Rubric | Evidence | Completed experiment |
|---|---|---|
| B1 | benchmarks/bonus-build-compare-tg128.md, .json, bonus-build-metadata.json, build logs | Native CPU Release source b10488 vs pinned prebuilt CPU, same Q4/ngl=0/tg128 |
| B2 | benchmarks/bonus-gpu-offload-sweep.md, .json; screenshot 09 | ngl 0/8/16/24/32/99 |
| B3 | submission/REFLECTION.md section 6 | CPU 9.12 to GPU 50.60 tok/s, 5.55x in the same sweep; B1 separately 1.059x |
| B4 | benchmarks/bonus-c7-native-compare.md, .json; four raw logs; compiler flags | C7, GGML_NATIVE ON/OFF, same MSVC Release source and CPU workload |
| B5 | benchmarks/bonus-embedding-serving.md; screenshot 11 | C9 live embedding endpoint and batch 1/2/4/8/16, comparison with chat regime |

All five rubric criteria have experimental evidence; the grader assesses the correctness and understanding of the interpretation. C9 is B5 evidence, not B4. Source/build binaries are intentionally ignored and must not be forced into Git. Logs and reports are the submitted evidence. Bonus screenshots are optional per submission/screenshots/README.md; B1/C7 here retain textual raw logs, not fabricated images.

Read and understand the AI-assisted interpretation before submitting, as required by docs/RULES.md. Final submission still requires committing, pushing to a Public correctly named repository, and pasting its URL into the LMS before the applicable deadline.
