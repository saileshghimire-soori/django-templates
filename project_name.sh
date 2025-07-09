#!/bin/bash

# Usage: bash project_name.sh NEW_PROJECT_NAME

set -e

if [ -z "$1" ]; then
  echo "Usage: bash $0 NEW_PROJECT_NAME"
  exit 1
fi

NEW_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OLD_NAME="$(basename "$SCRIPT_DIR")"
PROJECT_ROOT="$SCRIPT_DIR"

echo "Renaming project from '$OLD_NAME' to '$NEW_NAME' in $PROJECT_ROOT"

# 1. Replace in file contents
grep -rl --exclude-dir=".git" --exclude="$0" "$OLD_NAME" "$PROJECT_ROOT" | xargs sed -i "s/$OLD_NAME/$NEW_NAME/g"

# 2. Rename files and directories
find "$PROJECT_ROOT" -depth -name "*$OLD_NAME*" | while read path; do
  new_path="$(echo "$path" | sed "s/$OLD_NAME/$NEW_NAME/g")"
  mv "$path" "$new_path"
done

echo "Project renamed successfully."
