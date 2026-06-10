#!/bin/bash
# aQuickRescue Database Setup Script
# Quick setup for local development

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="${PROJECT_ROOT}/backend/dev.db"
SCHEMA_PATH="${PROJECT_ROOT}/backend/database/schema_sqlite.sql"

echo "🚀 aQuickRescue Database Setup"
echo "   Project Root: ${PROJECT_ROOT}"
echo "   Database: ${DB_PATH}"
echo "   Schema: ${SCHEMA_PATH}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if schema file exists
if [[ ! -f "${SCHEMA_PATH}" ]]; then
    echo "❌ Schema file not found: ${SCHEMA_PATH}"
    exit 1
fi

# Ask to reset or create
if [[ -f "${DB_PATH}" ]]; then
    echo "⚠️  Database already exists: ${DB_PATH}"
    read -p "Do you want to reset it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "${DB_PATH}"
        echo "🗑️  Removed existing database"
    else
        echo "✅ Using existing database"
        exit 0
    fi
fi

# Initialize database
echo ""
echo "📦 Initializing database..."
cd "${PROJECT_ROOT}"
python3 init_db.py --db "${DB_PATH}" --schema "${SCHEMA_PATH}" --reset

# Verify
echo ""
echo "✅ Database setup complete!"
echo ""
echo "📋 Test Users:"
echo "   - patient_john (PATIENT)"
echo "   - responder_alice (FIRST_RESPONDER)"
echo "   - doctor_bob (EMERGENCY_PHYSICIAN)"
echo "   - admin_carol (ADMIN)"
echo ""
echo "🔍 To inspect database:"
echo "   sqlite3 ${DB_PATH}"
echo ""
echo "📖 For more info, see DATABASE_SETUP.md"

