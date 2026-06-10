# Gammal Tech Internship – Healthcare Data Platform (ETL + Data Science)

## What this is

A complete Data Engineer + Data Scientist project built during my rotational internship at Gammal Tech.

**Part 1: Data Engineer** – ETL pipeline that cleans fake healthcare CSV data and loads it into MySQL.

**Part 2: Data Scientist** – Analysis, visualizations, and machine learning on the same database.

## Tech used

- Python (pandas, mysql-connector, matplotlib, seaborn, scikit-learn)
- MySQL
- Jupyter Notebook
- Synthetic data only – no real patient information

## Project Files

| File | What it does |
|------|--------------|
| `etl_load.py` | ETL pipeline: reads CSV → cleans data → loads into MySQL |
| `data_scientist.py` | Menu-based analysis: run SQL queries from terminal |
| `Data_Scientist_Healthcare_Analysis.ipynb` | Jupyter notebook with visualizations + ML model |
| `csv_files/` | Contains 7 CSV files with synthetic healthcare data |

## What the pipeline does (Data Engineer)

- Reads 7 CSV files (patients, doctors, appointments, prescriptions, pharmacies, insurance_companies, insurance_claims)
- Cleans bad data (fixes missing values, invalid ages, wrong statuses, mixed date formats)
- Creates a MySQL database with foreign key relationships
- Loads cleaned data in dependency order (parents before children)

## What the analysis does (Data Scientist)

### Option 1: Terminal Menu (`data_scientist.py`)
Run from command line: `python data_scientist.py`
- Choose from 8 business questions (1-8)
- Get instant answers from MySQL
- No visualizations, just results

### Option 2: Jupyter Notebook (`Data_Scientist_Healthcare_Analysis.ipynb`)
Contains:
- **Data quality checks** – missing values, age ranges, status distribution
- **Visualizations** – bar charts, histograms, time series plots
- **Key business questions answered**
- **Machine Learning model** – Logistic Regression to predict patient no-shows
- **Business recommendations**

## How to run

### Prerequisites
- MySQL installed and running locally
- Python 3.8+

### Step 1: Install dependencies

**For ETL + menu script:**
```bash
pip install pandas mysql-connector-python

For Jupyter notebook (add these):

pip install jupyter matplotlib seaborn scikit-learn

Or install all at once:

pip install pandas mysql-connector-python jupyter matplotlib seaborn scikit-learn

Notes

    This uses fake/synthetic data only – no real patient information

    The password and encryption key are hardcoded for demo purposes – never do this in production

    As an intern, I had no access to production data – this is my learning portfolio

Author

Intern at Gammal Tech (Healthcare Division)

Date

June 2026
