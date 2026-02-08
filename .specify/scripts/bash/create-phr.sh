#!/bin/bash
# create-phr.sh - Create a Prompt History Record

set -e

# Default values
STAGE="general"
FEATURE="none"
TITLE=""
OUTPUT_JSON=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --title)
      TITLE="$2"
      shift 2
      ;;
    --stage)
      STAGE="$2"
      shift 2
      ;;
    --feature)
      FEATURE="$2"
      shift 2
      ;;
    --json)
      OUTPUT_JSON=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Validate required parameters
if [ -z "$TITLE" ]; then
  echo "Error: --title is required"
  exit 1
fi

# Generate slug from title
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')

# Determine route based on stage
if [ "$STAGE" == "constitution" ]; then
  BASE_DIR="history/prompts/constitution"
  EXTENSION="constitution"
elif [ "$STAGE" == "general" ]; then
  BASE_DIR="history/prompts/general"
  EXTENSION="general"
else
  # Feature stages
  if [ "$FEATURE" == "none" ]; then
    echo "Error: Feature stages require --feature parameter"
    exit 1
  fi
  BASE_DIR="history/prompts/$FEATURE"
  EXTENSION="$STAGE"
fi

# Create directory if needed
mkdir -p "$BASE_DIR"

# Find next available ID
NEXT_ID=1
for file in "$BASE_DIR"/*.prompt.md; do
  if [ -f "$file" ]; then
    CURRENT_ID=$(basename "$file" | cut -d'-' -f1)
    if [ "$CURRENT_ID" -ge "$NEXT_ID" ]; then
      NEXT_ID=$((CURRENT_ID + 1))
    fi
  fi
done

# Format ID with leading zeros
FORMATTED_ID=$(printf "%03d" $NEXT_ID)

# Generate filename
FILENAME="$FORMATTED_ID-$SLUG.$EXTENSION.prompt.md"
FILEPATH="$BASE_DIR/$FILENAME"

# Read template
TEMPLATE_PATH=".specify/templates/phr-template.prompt.md"
if [ ! -f "$TEMPLATE_PATH" ]; then
  TEMPLATE_PATH="templates/phr-template.prompt.md"
fi

if [ ! -f "$TEMPLATE_PATH" ]; then
  echo "Error: Template not found at $TEMPLATE_PATH"
  exit 1
fi

# Copy template to target location
cp "$TEMPLATE_PATH" "$FILEPATH"

# Replace basic placeholders
DATE_ISO=$(date +%Y-%m-%d)
sed -i "s/{{ID}}/$FORMATTED_ID/g" "$FILEPATH"
sed -i "s/{{TITLE}}/$TITLE/g" "$FILEPATH"
sed -i "s/{{STAGE}}/$STAGE/g" "$FILEPATH"
sed -i "s/{{DATE_ISO}}/$DATE_ISO/g" "$FILEPATH"
sed -i "s/{{FEATURE}}/$FEATURE/g" "$FILEPATH"

# Output result
if [ "$OUTPUT_JSON" == true ]; then
  echo "{\"id\": \"$FORMATTED_ID\", \"path\": \"$FILEPATH\", \"stage\": \"$STAGE\"}"
else
  echo "Created PHR: $FILEPATH"
  echo "ID: $FORMATTED_ID"
  echo "Stage: $STAGE"
fi
