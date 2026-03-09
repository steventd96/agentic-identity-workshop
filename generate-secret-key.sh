#!/bin/bash

# Generate Flask Secret Key
# This script generates a secure random secret key for Flask

echo "Generating secure Flask secret key..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

echo ""
echo "Generated Secret Key:"
echo "====================="
echo "$SECRET_KEY"
echo ""
echo "Add this to your .env file:"
echo "FLASK_SECRET_KEY=$SECRET_KEY"
echo ""

# Optionally update .env file automatically
read -p "Do you want to automatically update .env file? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    if [ -f .env ]; then
        # Check if FLASK_SECRET_KEY already exists
        if grep -q "^FLASK_SECRET_KEY=" .env; then
            # Update existing key
            sed -i.bak "s|^FLASK_SECRET_KEY=.*|FLASK_SECRET_KEY=$SECRET_KEY|" .env
            echo "✓ Updated FLASK_SECRET_KEY in .env file"
            echo "  (Backup saved as .env.bak)"
        else
            # Add new key
            echo "" >> .env
            echo "# Flask Backend Secret Key (auto-generated)" >> .env
            echo "FLASK_SECRET_KEY=$SECRET_KEY" >> .env
            echo "✓ Added FLASK_SECRET_KEY to .env file"
        fi
    else
        echo "✗ .env file not found"
        exit 1
    fi
fi

echo ""
echo "Done!"

# Made with Bob