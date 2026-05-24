"""
MySQL Database Setup Script
Creates the database and initializes tables
"""

import mysql.connector
from mysql.connector import Error

def setup_mysql_database():
    """Create MySQL database and initialize it"""
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='$Albert2022#'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS phemedaa_forms")
            print("✓ Database 'phemedaa_forms' created or already exists")
            
            # Switch to the database
            cursor.execute("USE phemedaa_forms")
            
            cursor.close()
            connection.close()
            print("✓ MySQL connection successful")
            
            # Now initialize Flask app and create tables
            from app import app, db
            
            with app.app_context():
                db.create_all()
                print("✓ All tables created successfully")
            
            print("\n✓ MySQL setup complete!")
            return True
            
    except Error as e:
        print(f"✗ MySQL Error: {e}")
        print("\nPlease ensure:")
        print("1. MySQL is running on localhost:3306")
        print("2. Username: root")
        print("3. Password: $Albert2022#")
        return False

if __name__ == '__main__':
    setup_mysql_database()
