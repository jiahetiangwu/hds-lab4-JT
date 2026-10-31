# AI usage

## Model and scope

OpenAI Codex (GPT-6-based) was used to draft the SQL queries, Python scripts, and reorganize/polish documentation, including README.md, SCHEMA.md, and this AI_USAGE.md. Guidance was provided on joins, table grain, missing values, and verification. 

## Interaction 1: SQL development and result inspection

### Request and response

SQL development was requested for patient-level mutation counts in TP53, KRAS, EGFR, STK11, and KEAP1, excluding `Silent` records. Codex proposed a patient-gene grid with `LEFT JOIN` through `samples`, mutation filters in `ON`, and `COUNT(m.mutation_id)` to preserve zero counts. A second query was drafted to count distinct patients by tissue source site and stage, including missing stage.

Clarification was then requested on how to inspect the SQL results and enter SQLite. Instructions were provided for checking result dimensions and examining a patient's source mutation records. This was a result-verification interaction; no SQL execution error was reported, and an error-explanation-before-fix sequence is not claimed.

### Actual output

The Query 1 validation query was run manually in SQLite:

```text
result_rows  patient_count
-----------  -------------
2830         566
```

Source EGFR records for patient `TCGA-78-7147` were also inspected. The relevant output columns were:

```text
mutation_id  gene_symbol  variant_classification  protein_change
-----------  -----------  ----------------------  --------------
139795       EGFR         Missense_Mutation       p.L387M
139796       EGFR         Missense_Mutation       p.L861Q
139797       EGFR         Frame_Shift_Del         p.D1083Efs*11
```

### Verification

Before comparison with the output, the expected Query 1 size was established as 566 patients multiplied by five genes, or 2,830 rows. The manual row-count query confirmed that dimension and retention of all 566 patients. The three EGFR source records were non-Silent, matching the query result of 3.

Through Codex, all 2,830 patient-gene counts were additionally compared with a separate Python aggregation of the source mutation records. Query 2 was checked against Python counts for every site-stage group: 142 groups, 566 total patients, and all 54 patients with missing stage. These automated checks supplemented the manual source-record inspection.


## Interaction 2: Feature-table construction and local execution

### Request and response

A Python script was requested to combine patient and sample information with the SQL mutation counts. Codex generated a script that reshapes the long-format counts using Python dictionaries and exports TSV files. Checks were included for patient retention, unique patient-gene pairs, mutation totals, and site-stage counts.

### Actual output

The script was run locally:

```bash
python3 build_feature_table.py
```

The terminal returned:

```text
Patients before join: 566
Patients after sample join: 566
Query 1 rows: expected 2830, actual 2830
Query 2 groups: expected 142, actual 142
Final feature table: 566 rows, 11 columns
Missing sex: 52
Missing age_at_diagnosis: 71
Missing stage: 54
Missing tissue_source_site: 0
Missing tmb_nonsynonymous: 0
All five gene totals match direct mutation counts.
```

### Verification and limitations

The expected dimensions and missing-value counts had been established from the database inspection. Local execution reproduced those counts without losing patients. The validation code was AI-generated, so execution was supplemented by the manual SQLite checks described above.

Additional checks were executed through Codex: the exported TSVs were read back and compared with the database; a clean Python 3.13.5 virtual environment reproduced identical outputs; and the README download command retrieved a database with the same SHA-256 hash as the local input. Rebuilding from the downloaded copy also produced identical TSVs. This tested a Python virtual environment, not creation of the Conda environment. No execution failure or resulting fix was reported for this interaction.

