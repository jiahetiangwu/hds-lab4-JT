# Lab 4: Database-Driven Feature Table

A patient-level feature table was constructed from the supplied TCGA Lung Adenocarcinoma PanCancer Atlas SQLite database. Non-Silent mutations in five genes were counted with SQL and reshaped in Python. All 566 patients were retained. A second query summarizes patient counts by tissue source site and tumor stage.

## Requirements

Python 3.10 or later. All scripts use the Python standard library; no third-party packages are required. An optional Conda environment is defined in `environment.yml`:

```bash
conda env create -f environment.yml
conda activate hds-lab4
```

## Input and data source

Use the course-provided `cohort.db` from [the course repository](https://github.com/gwcbi/applied-computing-HDS/blob/main/data/raw/lab4-cbioportal-luad/cohort.db). The course identifies the source as the TCGA Lung Adenocarcinoma PanCancer Atlas study, available through [cBioPortal](https://www.cbioportal.org/study/summary?id=luad_tcga_pan_can_atlas_2018).

Download the database and place it at `data/raw/cohort.db`. Alternatively, from the repository root:

```bash
mkdir -p data/raw
curl -fL "https://raw.githubusercontent.com/gwcbi/applied-computing-HDS/main/data/raw/lab4-cbioportal-luad/cohort.db" -o data/raw/cohort.db
```

The downloaded database is a local input cache and is excluded by `.gitignore`. Do not rebuild it from the original study: the assignment uses the supplied 566-patient database. Internet access is needed only for downloading the input, not for table construction.

## Run

From the repository root, rebuild both outputs with one command:

```bash
python3 build_feature_table.py
```

The script expects `data/raw/cohort.db` and the two SQL files. It opens the database read-only and writes (or replaces) these outputs at the repository root:

| Output | Grain | Rows | Columns |
|---|---|---:|---:|
| `feature_table.tsv` | One patient | 566 | 11 |
| `site_stage_counts.tsv` | One observed site-stage combination | 142 | 3 |

The feature table contains patient ID, sex, age at diagnosis, stage, tissue source site, TMB, and the TP53, KRAS, EGFR, STK11, and KEAP1 mutation counts. Both output TSVs are included in the submission.

Optional input and output locations:

```bash
python3 build_feature_table.py --db data/raw/cohort.db --output-dir .
```

To repeat the schema inspection:

```bash
python3 inspect_database.py
```

## Repository files

| File | Purpose |
|---|---|
| `build_feature_table.py` | Query, reshape in Python, validate, and export both TSVs |
| `inspect_database.py` | Inspect schema, row counts, relationships, and missing values |
| `query1_gene_counts.sql` | One row per patient and target gene; excludes Silent mutations |
| `query2_site_stage_counts.sql` | Distinct patient counts by site and stage, including NULL stage |
| `SCHEMA.md` | All tables, columns, primary keys, foreign keys, and observed relationships |
| `DATA_DICTIONARY.md` | Definitions, units, sources, and missing-value coding for all 11 feature columns |
| `AI_USAGE.md` | AI use and verification methods |
| `environment.yml` | Optional Python environment |

## Schema and construction

The four tables are `patients`, `samples`, `mutations`, and `genes`. See [SCHEMA.md](SCHEMA.md) for the full schema write-up. Mutations connect to patients through samples and to genes through gene symbols. The schema allows multiple samples per patient, but the supplied dataset has exactly one per patient. Execution stops if multiple samples per patient are found; no sample-selection rule is applied.

Query 1 creates all patient-gene combinations, then left joins samples and mutations. Matching-gene and non-Silent filters are in `ON`, preserving combinations with no qualifying mutations. `COUNT(m.mutation_id)` returns zero for unmatched combinations. SQL establishes the patient-gene grain first; Python dictionaries then reshape the long results into five gene columns. Patient/sample features are left joined in SQL and merged with the wide counts in Python. No SQL pivot is used.

Query 2 counts distinct patient IDs without joining mutations, avoiding multiplication by mutation records. NULL stages remain in their site-specific groups. Only observed site-stage combinations are output; original stage labels are preserved.

## Missing data handling

| Feature | Missing values | Handling |
|---|---:|---|
| Sex | 52 | Preserve SQL NULL as NA |
| Age at diagnosis | 71 | Preserve SQL NULL as NA; no imputation |
| Stage | 54 | Preserve SQL NULL as NA; retain in site-stage grouping |
| Tissue source site | 0 | Copy recorded value; would encode NULL as NA |
| TMB | 0 | Copy recorded value; would encode NULL as NA |
| Each target-gene count | 0 missing | 0 means no matching non-Silent mutation record |

All patients are retained, including those with missing clinical values or no mutation records. The four samples with no mutation records receive zero gene counts, meaning no qualifying records in this database; these values do not demonstrate biological absence or complete mutation ascertainment. Clinical NA values are never replaced with zero. See [DATA_DICTIONARY.md](DATA_DICTIONARY.md) for precise definitions.

## Validation

| Check | Expected | Observed |
|---|---:|---:|
| Query 1 patient-gene rows | 566 x 5 = 2,830 | 2,830 |
| Distinct patients in Query 1 | 566 | 566 |
| Query 2 site-stage groups | 142 | 142 |
| Patients summed across Query 2 groups | 566 | 566 |
| Patients with missing stage retained in Query 2 | 54 | 54 |
| Patients before / after the sample join | 566 / 566 | 566 / 566 |
| Final feature rows / columns | 566 / 11 | 566 / 11 |

For Query 2, the expected 142 groups were calculated in Python from the distinct site-stage pairs before SQL aggregation. Every SQL group count matched the Python result. The observed stage labels, including broad stages such as `I` and substages such as `IA`, were retained separately.

Query 1 contains 2,130 zero-count patient-gene pairs. Twelve target-gene mutation records classified as `Silent` were excluded. The five gene symbols were confirmed in `genes`, and no NULL mutation classifications were found. The retained mutation classifications are listed in [DATA_DICTIONARY.md](DATA_DICTIONARY.md).

### Aggregate check

Gene totals after reshaping were compared with direct counts from `mutations`, without the patient-gene grid.

| Gene | Sum of patient counts | Direct mutation count |
|---|---:|---:|
| TP53 | 305 | 305 |
| KRAS | 172 | 172 |
| EGFR | 85 | 85 |
| STK11 | 81 | 81 |
| KEAP1 | 103 | 103 |

### Record-level check

The source EGFR records for patient `TCGA-78-7147` were inspected in SQLite and compared with the query result.

| Mutation ID | Classification | Protein change |
|---|---|---|
| 139795 | Missense_Mutation | p.L387M |
| 139796 | Missense_Mutation | p.L861Q |
| 139797 | Frame_Shift_Del | p.D1083Efs*11 |

All three records satisfy the non-Silent filter, matching the EGFR count of 3. The row-count and source-record queries were also run manually in the SQLite command-line tool. A subsequent run of the construction script reproduced the reported dimensions and missing-value counts.

The exported TSVs were read back and checked against the database: all patient IDs were retained, the example EGFR count remained 3, and missing-value counts were unchanged. Verification methods and AI involvement are documented in [AI_USAGE.md](AI_USAGE.md).
