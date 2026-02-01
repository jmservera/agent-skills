#!/bin/bash

# Define paths
# Script is running from /home/jmservera/source/agent-skills/
SOURCE_PARENT="$(dirname "$(readlink -f "$0")")"
SKILLS_DIR="$SOURCE_PARENT/skills"
DEST_PARENT="$HOME/.copilot/skills"

echo "Installing skills from $SKILLS_DIR to $DEST_PARENT..."

# Check if skills directory exists
if [ ! -d "$SKILLS_DIR" ]; then
    echo "Error: Skills directory $SKILLS_DIR not found."
    exit 1
fi

# Create destination parent if it doesn't exist
mkdir -p "$DEST_PARENT"

# Iterate over each skill in the skills directory
for skill_path in "$SKILLS_DIR"/*; do
    if [ -d "$skill_path" ]; then
        skill_name=$(basename "$skill_path")
        dest_path="$DEST_PARENT/$skill_name"
        
        echo "Installing $skill_name..."
        
        # Remove existing skill to ensure clean install
        if [ -d "$dest_path" ]; then
            echo "  Removing existing version..."
            rm -rf "$dest_path"
        fi
        
        # Copy the skill folder
        echo "  Copying files..."
        cp -r "$skill_path" "$DEST_PARENT/"
    fi
done

echo "Done! All skills installed."
