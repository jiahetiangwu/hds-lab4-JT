# Feature table data dictionary

`feature_table.tsv` has 566 patient rows and the following 11 columns. SQL NULL values are written as the literal string `NA`.

| Column | Meaning / derivation | Units | Source | Missing-value coding |
|---|---|---|---|---|
| patient_id | Unique patient identifier; one row per patient | Identifier | patients.patient_id | Not missing; must be unique |
| sex | Recorded sex; original labels preserved | Category | patients.sex | NA for SQL NULL; 52 missing |
| age_at_diagnosis | Recorded age at diagnosis; copied without recalculation or rounding | Years | patients.age_at_diagnosis | NA for SQL NULL; 71 missing |
| stage | Recorded tumor stage; broad stages and substages retained as distinct labels | Category | patients.stage | NA for SQL NULL; 54 missing |
| tissue_source_site | Tissue source site for the patient's single tumor sample | Category | samples.tissue_source_site via samples.patient_id | NA for SQL NULL; none missing in this dataset |
| tmb_nonsynonymous | Recorded nonsynonymous tumor mutation burden; copied without recalculation | Mutations per megabase | samples.tmb_nonsynonymous via samples.patient_id | NA for SQL NULL; none missing in this dataset |
| TP53 | Number of non-Silent mutation records in TP53 across the patient's samples | Mutation records (nonnegative integer) | mutations via samples.sample_id and samples.patient_id | 0 when no qualifying record exists; no NA in this dataset |
| KRAS | Number of non-Silent mutation records in KRAS across the patient's samples | Mutation records (nonnegative integer) | mutations via samples.sample_id and samples.patient_id | 0 when no qualifying record exists; no NA in this dataset |
| EGFR | Number of non-Silent mutation records in EGFR across the patient's samples | Mutation records (nonnegative integer) | mutations via samples.sample_id and samples.patient_id | 0 when no qualifying record exists; no NA in this dataset |
| STK11 | Number of non-Silent mutation records in STK11 across the patient's samples | Mutation records (nonnegative integer) | mutations via samples.sample_id and samples.patient_id | 0 when no qualifying record exists; no NA in this dataset |
| KEAP1 | Number of non-Silent mutation records in KEAP1 across the patient's samples | Mutation records (nonnegative integer) | mutations via samples.sample_id and samples.patient_id | 0 when no qualifying record exists; no NA in this dataset |

## Mutation counting rule

For each gene column, `mutations.mutation_id` is counted after joining mutations to patients through `samples`. The gene symbol must match the column, and `variant_classification = 'Silent'` is excluded. The retained classifications present in the supplied database are: Frame_Shift_Del, Frame_Shift_Ins, In_Frame_Del, In_Frame_Ins, Missense_Mutation, Nonsense_Mutation, Nonstop_Mutation, Splice_Site, Translation_Start_Site. There are no NULL classification values. Records are counted as stored; there is no additional deduplication of variants.

A count of 0 means no qualifying mutation record in this database. It is distinct from an unrecorded clinical value (`NA`). The four samples with no mutation records receive zero counts under this definition; these zeros do not establish biological absence or adequate sequencing coverage.

Each patient has exactly one sample in the supplied database, so sample-level site and TMB map unambiguously to a patient. Execution stops if multiple samples per patient are encountered.
