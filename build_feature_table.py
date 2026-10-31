"""Construct and validate the patient feature table from cohort.db."""
import argparse
import csv
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GENES = ('TP53', 'KRAS', 'EGFR', 'STK11', 'KEAP1')
PATIENT_COLUMNS = (
    'patient_id', 'sex', 'age_at_diagnosis', 'stage',
    'tissue_source_site', 'tmb_nonsynonymous',
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def write_tsv(path, columns, rows):
    # Encode SQL NULL as NA and preserve numeric zeros.
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter='\t')
        writer.writeheader()
        for row in rows:
            writer.writerow({column: 'NA' if row[column] is None else row[column]
                             for column in columns})


def build(database, output_directory):
    require(database.is_file(), f'Database not found: {database}')
    with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as connection:
        connection.row_factory = sqlite3.Row
        patient_count = connection.execute('SELECT COUNT(*) FROM patients').fetchone()[0]
        require(patient_count == 566, f'Expected 566 patients, found {patient_count}')
        # Require one sample per patient for sample-level features.
        multiple_samples = connection.execute('''
            SELECT patient_id FROM samples
            GROUP BY patient_id HAVING COUNT(*) > 1
        ''').fetchall()
        require(not multiple_samples, 'Multiple samples per patient require an explicit selection rule')
        patients = [dict(row) for row in connection.execute('''
            SELECT p.patient_id, p.sex, p.age_at_diagnosis, p.stage,
                   s.tissue_source_site, s.tmb_nonsynonymous
            FROM patients AS p
            LEFT JOIN samples AS s ON s.patient_id = p.patient_id
            ORDER BY p.patient_id
        ''')]
        require(len(patients) == patient_count, 'Patient-sample join changed row count')
        require(len({row['patient_id'] for row in patients}) == patient_count,
                'Patient-sample join produced duplicate patient IDs')

        counts = connection.execute((ROOT / 'query1_gene_counts.sql').read_text()).fetchall()
        require(len(counts) == patient_count * len(GENES), 'Unexpected Query 1 row count')
        # Reshape patient-gene counts to wide format in Python.
        wide_counts = {row['patient_id']: {} for row in patients}
        for row in counts:
            patient, gene, count = row['patient_id'], row['gene_symbol'], row['mutation_count']
            require(patient in wide_counts and gene in GENES, 'Unexpected patient or gene')
            require(gene not in wide_counts[patient], 'Duplicate patient-gene pair')
            require(isinstance(count, int) and count >= 0, 'Invalid mutation count')
            wide_counts[patient][gene] = count
        require(all(set(values) == set(GENES) for values in wide_counts.values()),
                'A patient is missing a target-gene result')
        features = [{**row, **wide_counts[row['patient_id']]} for row in patients]
        require(len(features) == patient_count, 'Final feature table changed patient count')

        # Check gene totals against a separate query of mutation records.
        direct_totals = dict(connection.execute('''
            SELECT gene_symbol, COUNT(*) FROM mutations
            WHERE gene_symbol IN ('TP53', 'KRAS', 'EGFR', 'STK11', 'KEAP1')
              AND variant_classification <> 'Silent'
            GROUP BY gene_symbol
        '''))
        for gene in GENES:
            require(sum(row[gene] for row in features) == direct_totals.get(gene, 0),
                    f'Mutation total mismatch for {gene}')

        site_stage_counts = [dict(row) for row in connection.execute(
            (ROOT / 'query2_site_stage_counts.sql').read_text())]
        expected_groups = Counter((row['tissue_source_site'], row['stage']) for row in patients)
        actual_groups = {(row['tissue_source_site'], row['stage']): row['patient_count']
                         for row in site_stage_counts}
        require(actual_groups == dict(expected_groups), 'Site-stage aggregation mismatch')
        require(sum(row['patient_count'] for row in site_stage_counts) == patient_count,
                'Site-stage grouping lost or duplicated patients')

    output_directory.mkdir(parents=True, exist_ok=True)
    write_tsv(output_directory / 'feature_table.tsv', PATIENT_COLUMNS + GENES, features)
    write_tsv(output_directory / 'site_stage_counts.tsv',
              ('tissue_source_site', 'stage', 'patient_count'), site_stage_counts)
    print(f'Patients before join: {patient_count}')
    print(f'Patients after sample join: {len(patients)}')
    print(f'Query 1 rows: expected {patient_count * len(GENES)}, actual {len(counts)}')
    print(f'Query 2 groups: expected {len(expected_groups)}, actual {len(site_stage_counts)}')
    print(f'Final feature table: {len(features)} rows, {len(PATIENT_COLUMNS) + len(GENES)} columns')
    for column in PATIENT_COLUMNS[1:]:
        print(f'Missing {column}: {sum(row[column] is None for row in features)}')
    print('All five gene totals match direct mutation counts.')
    print(f'Outputs saved in: {output_directory.resolve()}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=ROOT / 'data/raw/cohort.db')
    parser.add_argument('--output-dir', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        build(args.db, args.output_dir)
    except (ValueError, sqlite3.Error, OSError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
