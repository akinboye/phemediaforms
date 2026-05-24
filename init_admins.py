"""
Initialize admin users for PHEMEDAA Forms Portal
Run this after setting up the database
"""

from app import app, db
from models import SuperAdmin, Admin
from auth import hash_password

def init_admins():
    """Create initial admin users"""
    
    with app.app_context():
        # Check if superadmin already exists
        existing_superadmin = SuperAdmin.query.filter_by(username='admin').first()
        
        if existing_superadmin:
            print("✓ SuperAdmin 'admin' already exists")
        else:
            # Create superadmin
            superadmin = SuperAdmin(
                username='admin',
                password=hash_password('admin123'),
                email='admin@phemediaa.com'
            )
            db.session.add(superadmin)
            db.session.commit()
            print("✓ SuperAdmin created")
            print("  Username: admin")
            print("  Password: admin123")
            print("  Email: admin@phemediaa.com")
        
        # Get the superadmin ID for creating admin users
        superadmin = SuperAdmin.query.filter_by(username='admin').first()
        
        # Create a regular admin user
        existing_admin = Admin.query.filter_by(username='user').first()
        
        if existing_admin:
            print("✓ Admin 'user' already exists")
        else:
            admin = Admin(
                first_name='Admin',
                last_name='User',
                email='user@phemediaa.com',
                phone_number='+234 803 231 7546',
                username='user',
                password=hash_password('user123'),
                is_active=True,
                created_by=superadmin.id
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created")
            print("  Username: user")
            print("  Password: user123")
            print("  Email: user@phemediaa.com")
        
        print("\n✓ Admin users initialized successfully!")
        print("\nLogin Credentials:")
        print("-" * 40)
        print("SUPERADMIN:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nREGULAR ADMIN:")
        print("  Username: user")
        print("  Password: user123")

if __name__ == '__main__':
    init_admins()
