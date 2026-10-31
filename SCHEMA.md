# Database schema

The supplied `cohort.db` was inspected using SQLite metadata, integrity checks, foreign key checks, and row-count queries. Run `python3 inspect_database.py` from the repository root to repeat the inspection. The database is opened read-only.

## Tables and columns

| Table | Grain | Rows | Primary key | Columns |
|---|---|---:|---|---|
| patients | One patient | 566 | patient_id | patient_id, sex, age_at_diagnosis, stage, vital_status, followup_months |
| samples | One tumor sample | 566 | sample_id | sample_id, patient_id, tissue_source_site, tmb_nonsynonymous, aneuploidy_score, msi_mantis_score |
| mutations | One somatic mutation record in one sample | 200789 | mutation_id | mutation_id, sample_id, gene_symbol, variant_classification, variant_type, protein_change, chromosome, start_pos, end_pos, t_ref_count, t_alt_count |
| genes | One gene | 17756 | gene_symbol | gene_symbol, entrez_gene_id, chromosome |

## Foreign keys and relationships

- `samples.patient_id` references `patients.patient_id`. The schema permits multiple samples per patient because `samples.patient_id` is not unique. Exactly one sample per patient was observed in this dataset.
- `mutations.sample_id` references `samples.sample_id`. A sample can have multiple mutation records; four samples have no mutation records.
- `mutations.gene_symbol` references `genes.gene_symbol`. A gene can be referenced by multiple mutation records; genes need not have a mutation record.

Each mutation record belongs to one sample and one gene. Patient-level mutation counts are obtained through `mutations` to `samples` to `patients`.

## Initial validation

- SQLite integrity check: `ok`.
- Foreign key violations: 0.
- Patient count: 566; sample count: 566.
- NULL patient values: sex = 52; age_at_diagnosis = 71; stage = 54.
- Four samples have no mutation records. Their patients are retained with `LEFT JOIN`; zero counts indicate no qualifying records in the database.

The schema does not enforce a unique sample per patient.
