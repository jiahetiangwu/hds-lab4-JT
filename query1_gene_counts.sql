-- Query 1: one row per patient and target gene.
-- Expected rows: 566 patients * 5 genes = 2830.
-- Include non-Silent classifications present in the supplied database.
WITH target_genes(gene_symbol) AS (
    VALUES ('TP53'), ('KRAS'), ('EGFR'), ('STK11'), ('KEAP1')
)
SELECT
    p.patient_id,
    g.gene_symbol,
    COUNT(m.mutation_id) AS mutation_count
FROM patients AS p
CROSS JOIN target_genes AS g
LEFT JOIN samples AS s
    ON s.patient_id = p.patient_id
LEFT JOIN mutations AS m
    ON m.sample_id = s.sample_id
    AND m.gene_symbol = g.gene_symbol
    AND m.variant_classification <> 'Silent'
GROUP BY p.patient_id, g.gene_symbol
ORDER BY p.patient_id, g.gene_symbol;
