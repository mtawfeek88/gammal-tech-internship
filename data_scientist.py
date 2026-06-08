import mysql.connector
from mysql.connector import Error
import pandas as pd

# ============================================
# CONFIGURATION
# ============================================

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',  # Change to your password
    'database': 'healthcare_db'
}

ENCRYPTION_KEY = 'my_secret_key_123'  # Must match ETL script

# ============================================
# CONNECTION FUNCTION
# ============================================

def get_connection():
    """Create and return MySQL connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"❌ Connection error: {e}")
        return None

# ============================================
# QUERY FUNCTIONS (Each returns DataFrame)
# ============================================

def doctor_visits_all():
    """Show ALL doctors with visit counts (decrypted names)"""
    query = f"""
        SELECT d.doctor_id, 
               CAST(AES_DECRYPT(d.name, '{ENCRYPTION_KEY}') AS CHAR) as doctor_name,
               COUNT(a.appointment_id) as visit_count
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        GROUP BY d.doctor_id, d.name
        ORDER BY visit_count DESC
    """
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        result = pd.read_sql(query, conn)
        conn.close()
        return result
    except Error as e:
        print(f"❌ Query error: {e}")
        conn.close()
        return pd.DataFrame()

def doctor_visits_top_bottom():
    """Return top 3 and bottom 3 doctors"""
    query_top = f"""
        SELECT d.doctor_id, 
               CAST(AES_DECRYPT(d.name, '{ENCRYPTION_KEY}') AS CHAR) as doctor_name,
               COUNT(a.appointment_id) as visit_count
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        GROUP BY d.doctor_id, d.name
        ORDER BY visit_count DESC
        LIMIT 3
    """
    
    query_bottom = f"""
        SELECT d.doctor_id, 
               CAST(AES_DECRYPT(d.name, '{ENCRYPTION_KEY}') AS CHAR) as doctor_name,
               COUNT(a.appointment_id) as visit_count
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        GROUP BY d.doctor_id, d.name
        ORDER BY visit_count ASC
        LIMIT 3
    """
    
    conn = get_connection()
    if conn is None:
        return pd.DataFrame(), pd.DataFrame()
    
    try:
        top = pd.read_sql(query_top, conn)
        bottom = pd.read_sql(query_bottom, conn)
        conn.close()
        return top, bottom
    except Error as e:
        print(f"❌ Query error: {e}")
        conn.close()
        return pd.DataFrame(), pd.DataFrame()

def insurance_approvals_all():
    """Show ALL insurance companies with claim stats"""
    query = """
        SELECT ic.company_id, 
               ic.name as company_name,
               COUNT(icd.claim_id) as total_claims,
               SUM(CASE WHEN icd.status = 'Approved' THEN 1 ELSE 0 END) as approved,
               SUM(CASE WHEN icd.status = 'Rejected' THEN 1 ELSE 0 END) as rejected,
               SUM(CASE WHEN icd.status = 'Pending' THEN 1 ELSE 0 END) as pending
        FROM insurance_claims icd
        JOIN insurance_companies ic ON icd.insurance_company_id = ic.company_id
        GROUP BY ic.company_id, ic.name
        ORDER BY approved DESC
    """
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        result = pd.read_sql(query, conn)
        conn.close()
        return result
    except Error as e:
        print(f"❌ Query error: {e}")
        conn.close()
        return pd.DataFrame()

def specialty_visits_all():
    """Show ALL specialties with visit counts"""
    query = """
        SELECT d.specialty, 
               COUNT(a.appointment_id) as visit_count
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE d.specialty IS NOT NULL AND d.specialty != ''
        GROUP BY d.specialty
        ORDER BY visit_count DESC
    """
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        result = pd.read_sql(query, conn)
        conn.close()
        return result
    except Error as e:
        print(f"❌ Query error: {e}")
        conn.close()
        return pd.DataFrame()

def patient_age_stats():
    """Show age statistics"""
    query = """
        SELECT 
            COUNT(*) as total_patients,
            AVG(age) as average_age,
            MIN(age) as youngest_age,
            MAX(age) as oldest_age
        FROM patients
        WHERE age IS NOT NULL AND age > 0 AND age <= 120
    """
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        result = pd.read_sql(query, conn)
        conn.close()
        return result
    except Error as e:
        print(f"❌ Query error: {e}")
        conn.close()
        return pd.DataFrame()

def doctor_prescriptions_all():
    """Show ALL doctors with prescription counts (decrypted names)"""
    query = f"""
        SELECT d.doctor_id, 
               CAST(AES_DECRYPT(d.name, '{ENCRYPTION_KEY}') AS CHAR) as doctor_name,
               COUNT(p.prescription_id) as prescription_count
        FROM prescriptions p
        JOIN doctors d ON p.doctor_id = d.doctor_id
        GROUP BY d.doctor_id, d.name
        ORDER BY prescription_count DESC
    """
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        result = pd.read_sql(query, conn)
        conn.close()
        return result
    except Error as e:
        print(f"❌ Query error: {e}")
        conn.close()
        return pd.DataFrame()

def pharmacy_prescriptions_all():
    """Show ALL pharmacies with prescription counts"""
    query = """
        SELECT ph.pharmacy_id, 
               ph.name as pharmacy_name,
               COUNT(p.prescription_id) as prescription_count
        FROM prescriptions p
        JOIN pharmacies ph ON p.pharmacy_id = ph.pharmacy_id
        GROUP BY ph.pharmacy_id, ph.name
        ORDER BY prescription_count DESC
    """
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        result = pd.read_sql(query, conn)
        conn.close()
        return result
    except Error as e:
        print(f"❌ Query error: {e}")
        conn.close()
        return pd.DataFrame()

def appointment_status_summary():
    """Show appointment status breakdown"""
    query = """
        SELECT status, 
               COUNT(*) as count
        FROM appointments
        WHERE status IS NOT NULL
        GROUP BY status
        ORDER BY count DESC
    """
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        result = pd.read_sql(query, conn)
        conn.close()
        return result
    except Error as e:
        print(f"❌ Query error: {e}")
        conn.close()
        return pd.DataFrame()

# ============================================
# MENU SYSTEM
# ============================================

def show_menu():
    print("\n" + "=" * 65)
    print("DATA SCIENTIST - HEALTHCARE ANALYSIS")
    print("=" * 65)
    print("1. All doctors ranked by visits (best → worst)")
    print("2. Top 3 and Bottom 3 doctors by visits")
    print("3. All insurance companies (approvals, rejections, pending)")
    print("4. All specialties ranked by visits")
    print("5. Patient age statistics (min, max, avg)")
    print("6. All doctors ranked by prescriptions written")
    print("7. All pharmacies ranked by prescriptions fulfilled")
    print("8. Appointment status summary")
    print("0. EXIT")
    print("-" * 65)

def main():
    while True:
        show_menu()
        choice = input("Enter your choice (0-8): ")
        
        if choice == '1':
            print("\n📊 ALL DOCTORS RANKED BY VISITS:")
            result = doctor_visits_all()
            if not result.empty:
                print(result.to_string(index=False))
            else:
                print("   No data found or connection error")
        
        elif choice == '2':
            print("\n🏆 TOP 3 DOCTORS (MOST VISITS):")
            top, bottom = doctor_visits_top_bottom()
            if not top.empty:
                print(top.to_string(index=False))
            else:
                print("   No data found")
            print("\n📉 BOTTOM 3 DOCTORS (LEAST VISITS):")
            if not bottom.empty:
                print(bottom.to_string(index=False))
            else:
                print("   No data found")
        
        elif choice == '3':
            print("\n🏢 INSURANCE COMPANIES - CLAIM SUMMARY:")
            result = insurance_approvals_all()
            if not result.empty:
                print(result.to_string(index=False))
            else:
                print("   No data found")
        
        elif choice == '4':
            print("\n⭐ SPECIALTIES RANKED BY VISITS:")
            result = specialty_visits_all()
            if not result.empty:
                print(result.to_string(index=False))
            else:
                print("   No data found")
        
        elif choice == '5':
            print("\n📊 PATIENT AGE STATISTICS:")
            result = patient_age_stats()
            if not result.empty:
                print(f"   Total patients: {result['total_patients'].iloc[0]}")
                print(f"   Average age: {result['average_age'].iloc[0]:.1f} years")
                print(f"   Youngest patient: {result['youngest_age'].iloc[0]} years")
                print(f"   Oldest patient: {result['oldest_age'].iloc[0]} years")
            else:
                print("   No data found")
        
        elif choice == '6':
            print("\n📝 ALL DOCTORS RANKED BY PRESCRIPTIONS:")
            result = doctor_prescriptions_all()
            if not result.empty:
                print(result.to_string(index=False))
            else:
                print("   No data found")
        
        elif choice == '7':
            print("\n💊 ALL PHARMACIES RANKED BY PRESCRIPTIONS:")
            result = pharmacy_prescriptions_all()
            if not result.empty:
                print(result.to_string(index=False))
            else:
                print("   No data found")
        
        elif choice == '8':
            print("\n📅 APPOINTMENT STATUS SUMMARY:")
            result = appointment_status_summary()
            if not result.empty:
                print(result.to_string(index=False))
            else:
                print("   No data found")
        
        elif choice == '0':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please enter 0-8")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
