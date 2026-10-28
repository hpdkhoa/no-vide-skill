# Planned configurations

| id | model | quant | gpu layers |
|---|---|---|---|
| run1 | qwen2.5-7b | q4_k_m | all |
| run2 | qwen2.5-7b | q8_0 | all |
| run3 | qwen2.5-7b | q4_k_m | 20 |
| run4 | qwen2.5-7b | q8_0 | 20 |
| run5 | qwen2.5-7b | f16 | all |

Raw results land in `runs/<id>.json` when a run finishes.
