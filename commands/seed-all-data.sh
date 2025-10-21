#!/bin/sh
set -e

echo "========================================="
echo "Database Full Seeding Process"
echo "========================================="
echo "This script will populate the database with all test data:"
echo "  1. Users"
echo "  2. Catalog"
echo ""

START_TIME=$(date +%s)

echo "Step 1: Seeding users..."
echo "-----------------------------------------"
python manage.py seed_users
echo ""


#echo "Step 2: Seeding catalog data..."
#echo "-----------------------------------------"
#python manage.py seed_catalog
#echo ""


END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo "========================================="
echo "Database Seeding Completed!"
echo "========================================="
echo "Total execution time: ${MINUTES}m ${SECONDS}s"
echo ""

echo ""
echo "========================================="
echo "All Done! Database is fully populated."
echo "========================================="
