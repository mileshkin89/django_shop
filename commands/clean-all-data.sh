#!/bin/sh
set -e

echo "========================================="
echo "Database Full Cleanup Process"
echo "========================================="
echo "WARNING: This will delete ALL test data from the database!"
echo "This includes:"
echo "  - Catalog"
echo "  - Addresses"
echo "  - Users"
echo ""

read -p "Are you sure you want to continue? Type 'yes' to confirm: " confirm
if [ "$confirm" != "yes" ]; then
    echo "Operation cancelled."
    exit 0
fi

# Record start time
START_TIME=$(date +%s)

#echo "Step 1: Cleaning catalog..."
#echo "-----------------------------------------"
#python manage.py clean_catalog --yes
#echo ""

echo "Step 2: Cleaning addresses..."
echo "-----------------------------------------"
python manage.py clean_address --yes
echo ""

echo "Step 3: Cleaning users..."
echo "-----------------------------------------"
python manage.py clean_users --yes
echo ""

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo "========================================="
echo "Database Cleanup Completed!"
echo "========================================="
echo "Total execution time: ${MINUTES}m ${SECONDS}s"
echo ""

echo ""
echo "========================================="
echo "All Done! Database is now empty."
echo "========================================="
