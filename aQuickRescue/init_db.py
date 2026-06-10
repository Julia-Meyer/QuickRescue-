#!/usr/bin/env python3
"""
aQuickRescue Database Initialization Script
Initializes SQLite3 database from schema_sqlite.sql
"""

import sqlite3
import argparse
import os


class DatabaseInitializer:
    """Initialize SQLite3 database for aQuickRescue"""

    def __init__(self, db_path: str = "dev.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def reset_database(self):
        """Drop all tables"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print(f"🗑️  Removed existing database")

    def execute_schema(self, schema_file: str = "schema_sqlite.sql"):
        """Execute SQL schema from file"""
        if not os.path.exists(schema_file):
            print(f"❌ Schema file not found: {schema_file}")
            return False

        with open(schema_file, 'r') as f:
            sql_script = f.read()

        cursor = self.conn.cursor()
        cursor.executescript(sql_script)
        self.conn.commit()
        print(f"✅ Schema executed successfully")
        return True

    def get_stats(self) -> dict:
        """Get database statistics"""
        cursor = self.conn.cursor()
        stats = {}
        tables = ['users', 'patient_profiles', 'emergency_access', 'audit_logs', 'access_logs', 'role_permissions']

        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            except sqlite3.Error:
                stats[table] = 0

        return stats

    def initialize(self, reset: bool = False, schema_file: str = "schema_sqlite.sql"):
        """Initialize database"""
        print(f"🚀 Initializing aQuickRescue Database")
        print(f"   Database: {self.db_path}")

        if reset:
            self.reset_database()

        self.connect()

        if not self.execute_schema(schema_file):
            self.close()
            return False

        stats = self.get_stats()
        print(f"\n📈 Database Statistics:")
        for table, count in stats.items():
            print(f"  {table}: {count} rows")

        self.close()
        print(f"\n✨ Database initialization complete!")
        return True


def main():
    parser = argparse.ArgumentParser(description="Initialize SQLite3 database for aQuickRescue")
    parser.add_argument('--db', default='dev.db', help='Database file path')
    parser.add_argument('--schema', default='schema_sqlite.sql', help='Schema file path')
    parser.add_argument('--reset', action='store_true', help='Drop and recreate database')

    args = parser.parse_args()

    initializer = DatabaseInitializer(args.db)
    initializer.initialize(reset=args.reset, schema_file=args.schema)


if __name__ == '__main__':
    main()

