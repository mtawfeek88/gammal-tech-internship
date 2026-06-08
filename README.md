# Gammal Tech Internship – Healthcare ETL Pipeline

## What this is
A Python ETL pipeline that cleans fake healthcare CSV data and loads it into a MySQL database. Built as part of my rotational internship at Gammal Tech.

## Tech used
- Python (pandas, mysql-connector)
- MySQL
- Synthetic data only – no real patient information

## What the pipeline does
1. Reads 7 CSV files (patients, doctors, prescriptions, etc.)
2. Cleans bad data (fixes missing values, invalid ages, wrong statuses)
3. Creates a MySQL database with foreign key relationships
4. Loads cleaned data in dependency order

## How to run (for anyone reviewing this)
1. Install dependencies: `pip install pandas mysql-connector-python`
2. Have MySQL running locally
3. Change the password in `DB_CONFIG` to your own MySQL password
4. Run: `python etl_load.py`

## Note
This uses fake/synthetic data only. The password and encryption key are hardcoded for demo purposes – never do this in production.

## Update: Data Science Analysis Added

I've added `data_scientist.py` which:
- Queries the MySQL database using SELECT statements
- Analyzes prescription patterns, appointment statuses, and insurance claims
- Built as part of my data science rotation at Gammal Tech

All analysis uses the same synthetic healthcare data from the ETL pipeline.
