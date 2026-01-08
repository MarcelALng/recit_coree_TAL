# Topic Modeling Performance Comparison

Generated: 2025-12-13 22:45:18

## Performance Metrics

| Metric | LDA (CPU) | LSA CPU | LSA GPU |
|--------|-----------|---------|----------|
| Nb_Discours | 9984 | 9984 | 9984 |
| Nb_Presidents | 12 | 12 | 12 |
| Nb_Paragraphs | 345491 | 345491 | 345491 |
| Nb_Topics | 15 | 15 | 15 |
| Execution_Time_Sec | 325.60 | 9.92 | 10.22 |
| CPU_Usage_Percent | 0.00 | 0.00 | 0.00 |
| Memory_Usage_Percent | 2.66 | 3.00 | 10.09 |
| GPU_Usage_Percent | 0.00 | 0.00 | 40.00 |
| GPU_Power_Watts | 10.16 | 10.15 | 32.76 |

## Analysis Details

- **LDA**: Latent Dirichlet Allocation using sklearn (CPU-based)
- **LSA CPU**: Latent Semantic Analysis with K-means clustering using sklearn (CPU)
- **LSA GPU**: Latent Semantic Analysis with K-means clustering using PyTorch (GPU-accelerated)

All analyses performed on the complete corpus of presidential speeches.
