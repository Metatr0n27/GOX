#!/bin/bash

git add .

echo
read -p "Checkpoint name: " MSG

git commit -m "$MSG"

echo
read -p "Push to GitHub? (y/N): " PUSH

if [[ "$PUSH" =~ ^[Yy]$ ]]; then
    git push
else
    echo "Checkpoint saved locally."
fi
