import sqlite3
conn = sqlite3.connect('instance/phemedaa_forms.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(form_submissions)")
columns = cursor.fetchall()
print("✓ form_submissions table columns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")
    
# Check for approver_position specifically
approver_pos_found = any(col[1] == 'approver_position' for col in columns)
print("\n✓ approver_position column present:" if approver_pos_found else "\n✗ approver_position column MISSING:", approver_pos_found)
conn.close()
