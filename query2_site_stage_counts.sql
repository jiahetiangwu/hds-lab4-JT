-- Query 2: one row per observed tissue-source-site and stage combination.
-- Expected rows: 142 observed combinations, including NULL stages.
-- Each patient has exactly one sample in the supplied database (verified).
SELECT
    s.tissue_source_site,
    p.stage,
    COUNT(DISTINCT p.patient_id) AS patient_count
FROM patients AS p
LEFT JOIN samples AS s
    ON s.patient_id = p.patient_id
GROUP BY s.tissue_source_site, p.stage
ORDER BY s.tissue_source_site, p.stage;
