# CashBoost Project - Command Log

## Setup
```bash
pip install dbt-duckdb --break-system-packages #installed dbt and DuckDB for database storage
dbt init cashboost_dbt # Creates a new dbt file for project
dbt debug # Make sure to see All checks passed!
```

## Connecting & Merging to GitHub
```bash
git init
git add . 
git commit -m "Phase 1: A/B design and synthetic data" # Takes all data from file
git remote add origin <your-repo-url> # Adds data to my repo
git push -u origin main # Set up connection
git push # Push to GitHub
```

## Phase 2: dbt
```bash
cp ../cashboost_dataset.csv seeds/cashboost_dataset.csv # copying the table from my csv file into seed folder in dbt
dbt seed # loads cashboost_dataset.csv into DuckDB
rm -rf models/example # example folders
mkdir models/staging # creates staging file in models
mkdir models/marts # creates marts file in models

dbt run #builds staging and marts models (after running code in SQL)
dbt run --ful-refresh # rebuilds everything from scratch
dbt test # runs data quality tests
```
## Removing files from Git Repo
```bash
## If just deleting from repo (not source folder) on laptop
git rm filename.ext
git commit -m "Remove unwanted file"
git push

##if deleted from source folder on laptop and updating in Git
git add -u
git commit -m "Remove unwanted files"
git push
```