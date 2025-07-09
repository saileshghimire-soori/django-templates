#!/bin/bash

# Check if app name is provided
if [ -z "$1" ]; then
  echo "Usage: ./create_app.sh <app_name>"
  exit 1
fi

APP_NAME=$1
APPS_DIR="apps"
APP_PATH="$APPS_DIR/$APP_NAME"

# Make sure we're in the Django project root (where manage.py is)
if [ ! -f "manage.py" ]; then
  echo "Error: manage.py not found. Please run this script from your Django project root."
  exit 1
fi

# Create the apps directory and the app subdirectory
mkdir -p "$APP_PATH"

# Start the Django app inside the subdirectory
python manage.py startapp "$APP_NAME" "$APP_PATH"

# Make sure apps/ is a Python package
touch "$APPS_DIR/__init__.py"

# Fix the 'name' attribute in the generated apps.py
APPS_PY="$APP_PATH/apps.py"
if [ -f "$APPS_PY" ]; then
  sed -i "s/name = '$APP_NAME'/name = 'apps.$APP_NAME'/" "$APPS_PY"
fi

# Add the new app to LOCAL_APPS in settings.py if not already present
SETTINGS_PY="auction_backend/settings.py"
APP_DOTTED="apps.$APP_NAME"
if ! grep -q "'$APP_DOTTED'" "$SETTINGS_PY"; then
  sed -i "/^LOCAL_APPS *= *\[/ s/\[/\[\'$APP_DOTTED\', /" "$SETTINGS_PY"
fi

echo "✅ Django app '$APP_NAME' created at '$APP_PATH'"
