#!/bin/bash

set -e

# Load .env variables
ENV_FILE="$(dirname "$0")/.env"
if [ ! -f "$ENV_FILE" ]; then
  echo ".env file not found!"
  exit 1
fi

export $(grep -v '^#' "$ENV_FILE" | xargs)

if [ "$DB_CREATION" != "True" ]; then
  echo "DB_CREATION is not True. Exiting."
  exit 0
fi

# Default admin user (we assume it's 'postgres')
DB_ADMIN_USER=postgres
echo "Using admin user: $DB_ADMIN_USER"

if [ "$DB_Format" = "postgresql" ]; then
  echo "Creating PostgreSQL user and database..."

  # Create user if it doesn't exist
  psql -h "$DB_HOST" -U "$DB_ADMIN_USER" -p "$DB_PORT" -tc "SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER';" | grep -q 1 || \
    psql -h "$DB_HOST" -U "$DB_ADMIN_USER" -p "$DB_PORT" -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

  # Create database if it doesn't exist
  psql -h "$DB_HOST" -U "$DB_ADMIN_USER" -p "$DB_PORT" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME';" | grep -q 1 || \
    createdb -h "$DB_HOST" -U "$DB_ADMIN_USER" -p "$DB_PORT" "$DB_NAME"

  # Grant privileges
  psql -h "$DB_HOST" -U "$DB_ADMIN_USER" -p "$DB_PORT" -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

  echo "✅ PostgreSQL user and database setup complete."

elif [ "$DB_Format" = "mysql" ]; then
  echo "Creating MySQL database '$DB_NAME'..."
  mysql -h "$DB_HOST" -P "$DB_PORT" -u root -p -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;"
  echo "✅ MySQL database created or already exists."
else
  echo "❌ DB_Format '$DB_Format' not supported."
  exit 1
fi

# Didn't worked...
