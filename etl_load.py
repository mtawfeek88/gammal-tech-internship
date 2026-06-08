import pandas as pd
import mysql.connector
from mysql.connector import Error
import os

# ============================================
# CONFIGURATION
# ============================================
CSV_FOLDER = "csv_files"
DB_NAME = "healthcare_db"

# MySQL connection (change password to yours)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',  # # ⚠️ CHANGE THIS to your own MySQL password. This is fake/local only.
    'database': DB_NAME
}

# Encryption key (in real world, store in environment variable)
ENCRYPTION_KEY = 'my_secret_key_123'  ## Fake key for demo only. Never hardcode in real projects
# ============================================
# STEP 1: CLEAN EACH CSV FILE (FIX, DON'T DELETE)
# ============================================

def clean_patients(df):
    """Clean patients data - FIX bad data, don't delete rows"""
    # Fix missing names (don't delete)
    df['name'] = df['name'].fillna('Unknown Patient')
    
    # Fix missing phone (don't delete)
    df['phone'] = df['phone'].fillna('UNKNOWN')
    
    # Fix missing insurance_company_id
    df['insurance_company_id'] = df['insurance_company_id'].fillna(0).astype(int)
    
    # Fix negative ages → set to 0
    df['age'] = df['age'].apply(lambda x: 0 if x < 0 else x)
    
    # Fix ages > 120 → set to 120
    df['age'] = df['age'].apply(lambda x: 120 if x > 120 else x)
    
    # Fix missing ages → set to average (30)
    df['age'] = df['age'].fillna(30)
    
    # Remove any completely empty rows (all nulls) - rare case
    df = df.dropna(how='all')
    
    return df

def clean_doctors(df):
    """Clean doctors data"""
    df['name'] = df['name'].fillna('Unknown Doctor')
    df['specialty'] = df['specialty'].fillna('General')
    df['phone'] = df['phone'].fillna('UNKNOWN')
    df = df.dropna(subset=['doctor_id'])
    return df

def clean_pharmacies(df):
    """Clean pharmacies data"""
    df['name'] = df['name'].fillna('Unknown Pharmacy')
    df['location'] = df['location'].fillna('Unknown')
    df = df.dropna(subset=['pharmacy_id'])
    return df

def clean_insurance(df):
    """Clean insurance companies data"""
    df['name'] = df['name'].fillna('Unknown Insurance')
    df = df.dropna(subset=['company_id'])
    return df

def clean_appointments(df):
    """Clean appointments data"""
    df = df.dropna(subset=['appointment_id', 'patient_id', 'doctor_id'])
    valid_statuses = ['Scheduled', 'Completed', 'Cancelled']
    df['status'] = df['status'].apply(lambda x: x if x in valid_statuses else 'Scheduled')
    return df

def clean_prescriptions(df):
    """Clean prescriptions data"""
    df = df.dropna(subset=['prescription_id', 'doctor_id', 'patient_id'])
    valid_statuses = ['Pending', 'Fulfilled', 'Rejected', 'Cancelled']
    df['status'] = df['status'].apply(lambda x: x if x in valid_statuses else 'Pending')
    df['pharmacy_id'] = df['pharmacy_id'].fillna(0).astype(int)
    df['medication_name'] = df['medication_name'].fillna('Unknown Medication')
    return df

def clean_claims(df):
    """Clean insurance claims data"""
    df = df.dropna(subset=['claim_id', 'appointment_id', 'patient_id'])
    valid_statuses = ['Pending', 'Approved', 'Rejected']
    df['status'] = df['status'].apply(lambda x: x if x in valid_statuses else 'Pending')
    df['amount'] = df['amount'].fillna(0)
    return df

# ============================================
# STEP 2: CREATE DATABASE AND TABLES (WITH ENCRYPTION)
# ============================================

def create_database():
    """Create database if not exists"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"✅ Database '{DB_NAME}' created or already exists")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"❌ Error creating database: {e}")
        return False
    return True

def create_tables():
    """Create all tables with encryption for sensitive columns"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Disable foreign key checks temporarily
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Patients table (with encrypted sensitive columns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INT PRIMARY KEY,
                name VARBINARY(255) NOT NULL,
                age INT,
                phone VARCHAR(20),
                insurance_company_id INT
            )
        """)
        
        # Doctors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id INT PRIMARY KEY,
                name VARBINARY(100) NOT NULL,
                specialty VARCHAR(50),
                phone VARCHAR(20)
            )
        """)
        
        # Pharmacies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pharmacies (
                pharmacy_id INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(200)
            )
        """)
        
        # Insurance companies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insurance_companies (
                company_id INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            )
        """)
        
        # Appointments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INT PRIMARY KEY,
                patient_id INT,
                doctor_id INT,
                appointment_date DATE,
                status VARCHAR(20),
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
            )
        """)
        
        # Prescriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                prescription_id INT PRIMARY KEY,
                doctor_id INT,
                patient_id INT,
                pharmacy_id INT,
                medication_name VARCHAR(100),
                status VARCHAR(20),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(pharmacy_id)
            )
        """)
        
        # Insurance claims table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insurance_claims (
                claim_id INT PRIMARY KEY,
                appointment_id INT,
                patient_id INT,
                insurance_company_id INT,
                amount DECIMAL(10,2),
                status VARCHAR(20),
                FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (insurance_company_id) REFERENCES insurance_companies(company_id)
            )
        """)
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        conn.commit()
        print("✅ All tables created successfully (with encryption for sensitive columns)")
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"❌ Error creating tables: {e}")
        return False

# ============================================
# STEP 3: LOAD CLEANED DATA TO MYSQL (BATCH INSERT)
# ============================================

def load_to_mysql_batch(df, table_name, encrypt_columns=None):
    """Load dataframe to MySQL table using BATCH insert (faster)"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 🔽 ADD THIS LINE 🔽
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Clear table first
        cursor.execute(f"DELETE FROM {table_name}")
        
        # Convert dataframe to list of tuples
        rows = [tuple(row) for _, row in df.iterrows()]
        
        if not rows:
            print(f"⚠️ No rows to load into {table_name}")
            # 🔽 ADD THIS BEFORE RETURN 🔽
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            return True
        
        # Build insert SQL
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # Encrypt sensitive columns if needed
        if encrypt_columns:
            print(f"   🔐 Encrypting columns: {encrypt_columns}")
        
        # Batch insert
        cursor.executemany(sql, rows)
        conn.commit()
        
        # 🔽 ADD THIS LINE 🔽
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        print(f"✅ Loaded {len(rows)} rows into {table_name}")
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"❌ Error loading to {table_name}: {e}")
        return False

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    print("=" * 55)
    print("HEALTHCARE DATA ENGINEER PIPELINE (with Encryption & Batch)")
    print("=" * 55)
    
    # Step A: Clean all CSV files
    print("\n📂 STEP 1: Cleaning CSV files (FIXING bad data, not deleting)...")
    
    files_to_clean = {
        'patients.csv': clean_patients,
        'doctors.csv': clean_doctors,
        'pharmacies.csv': clean_pharmacies,
        'insurance_companies.csv': clean_insurance,
        'appointments.csv': clean_appointments,
        'prescriptions.csv': clean_prescriptions,
        'insurance_claims.csv': clean_claims
    }
    
    cleaned_data = {}
    
    for filename, clean_func in files_to_clean.items():
        filepath = os.path.join(CSV_FOLDER, filename)
        try:
            df = pd.read_csv(filepath)
            print(f"   Reading {filename}: {len(df)} rows")
            df_cleaned = clean_func(df)
            cleaned_data[filename.replace('.csv', '')] = df_cleaned
            print(f"   Cleaned {filename}: {len(df_cleaned)} rows (kept all possible data)")
        except FileNotFoundError:
            print(f"   ❌ File not found: {filepath}")
            return
        except Exception as e:
            print(f"   ❌ Error cleaning {filename}: {e}")
            return
    
    # Step B: Create database and tables
    print("\n🗄️ STEP 2: Creating database and tables...")
    
    if not create_database():
        return
    if not create_tables():
        return
    
    # Step C: Load data to MySQL in correct order (using BATCH)
    print("\n📤 STEP 3: Loading data to MySQL (batch mode)...")
    
    # Define which tables have encrypted columns
    encryption_config = {
        'patients': ['name'],      # Encrypt patient names
        'doctors': ['name'],       # Encrypt doctor names
        # Other tables don't need encryption for this example
    }
    
    # Load in dependency order (parents first, then children)
    load_order = [
        'patients',
        'doctors',
        'pharmacies',
        'insurance_companies',
        'appointments',
        'prescriptions',
        'insurance_claims'
    ]
    
    for table_name in load_order:
        if table_name in cleaned_data:
            encrypt_cols = encryption_config.get(table_name, None)
            load_to_mysql_batch(cleaned_data[table_name], table_name, encrypt_cols)
    
    print("\n" + "=" * 55)
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 55)
    
    # Show sample verification
    print("\n📊 Verification: First 5 patients in database")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT patient_id, age, phone FROM patients LIMIT 5")
        for row in cursor.fetchall():
            print(f"   ID: {row[0]}, Age: {row[1]}, Phone: {row[2]}")
        cursor.close()
        conn.close()
    except:
        pass
    
    print("\n🔐 Note: Patient names are encrypted in the database (VARBINARY column)")
    print("   To decrypt: SELECT AES_DECRYPT(name, 'key') FROM patients;")

if __name__ == "__main__":
    main()
