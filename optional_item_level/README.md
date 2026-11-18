# Optional respondent-level EMS sensitivity analysis (data not included)

These scripts were prepared before access to either author's participant-level data. They
are **not a replication of either original study**, and the included JSON files are **column-name templates**, not evidence of the authors' original variable names. No synthetic data or author-owned microdata are included.

Only run if you have permission to use de-identified author data; edit the templates to map actual columns and verify recoding/exclusions before interpreting numerical outputs. Install additional dependencies with:

```bash
python -m pip install pandas statsmodels
```

Then, from this subdirectory:

```bash
python analyze_ems.py --input /private/path/selmer.csv --config config_selmer.template.json --output results_selmer
python analyze_ems.py --input /private/path/alexander.csv --config config_alexander.template.json --output results_alexander
```

Data should be kept in `author_data/` (gitignored) and never committed unless redistribution is explicitly authorized. The proposed category partition was made without seeing the participants' responses and is **not a validated factor structure**. The analysis may need modification to replicate each paper's original specifications and coding.
