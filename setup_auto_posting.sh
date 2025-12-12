#!/bin/bash
#
# Setup Script for Daily Auto-posting
#
# This script helps you set up the daily auto-posting feature for SEO blog generation.
# It will guide you through the configuration and cron job installation.
#

set -e

echo "=========================================="
echo "Daily Auto-posting Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Warning: Running as root. Consider running as a regular user."
    echo ""
fi

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Installation directory: $SCRIPT_DIR"
echo ""

# Step 1: Check Python installation
echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Found: $PYTHON_VERSION"
echo ""

# Step 2: Check required packages
echo "Step 2: Checking required Python packages..."
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing requests..."
    pip3 install requests
fi

if ! python3 -c "import openai" 2>/dev/null; then
    echo "Installing openai..."
    pip3 install openai
fi

echo "All required packages are installed"
echo ""

# Step 3: Check environment variables
echo "Step 3: Checking environment variables..."
if [ -z "$AI_API" ]; then
    echo "Warning: AI_API environment variable is not set"
    echo "You need to set it before running the auto-posting script"
    echo ""
    echo "To set it temporarily:"
    echo "  export AI_API='your-api-key-here'"
    echo ""
    echo "To set it permanently, add to ~/.bashrc or ~/.profile:"
    echo "  echo 'export AI_API=\"your-api-key-here\"' >> ~/.bashrc"
    echo ""
else
    echo "AI_API is set: ${AI_API:0:10}..."
fi

if [ -z "$WP_BASE_URL" ]; then
    echo "WP_BASE_URL is not set (will use default: https://freya-era.com)"
else
    echo "WP_BASE_URL is set: $WP_BASE_URL"
fi
echo ""

# Step 4: Create logs directory
echo "Step 4: Creating logs directory..."
mkdir -p logs
echo "Logs directory created: $SCRIPT_DIR/logs"
echo ""

# Step 5: Test the scripts
echo "Step 5: Testing scripts..."
echo "Testing keyword manager..."
if python3 keyword_manager.py --stats; then
    echo "✓ Keyword manager is working"
else
    echo "✗ Keyword manager test failed"
    exit 1
fi
echo ""

# Step 6: Dry run test
echo "Step 6: Running dry-run test..."
if [ -n "$AI_API" ]; then
    echo "Running auto-posting script in dry-run mode..."
    if python3 auto_post_daily.py --dry-run --force-keyword "ラブドール テスト"; then
        echo "✓ Dry-run test successful"
    else
        echo "✗ Dry-run test failed"
        exit 1
    fi
else
    echo "Skipping dry-run test (AI_API not set)"
fi
echo ""

# Step 7: Cron job setup
echo "Step 7: Cron job setup"
echo ""
echo "To set up the daily auto-posting at 10:00 AM, you need to add a cron job."
echo ""
echo "Option 1: Automatic setup (recommended)"
echo "  This will add the cron job to your crontab automatically."
echo ""
echo "Option 2: Manual setup"
echo "  You will need to edit your crontab manually."
echo ""

read -p "Do you want to automatically add the cron job? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Automatic setup
    CRON_COMMAND="0 10 * * * cd $SCRIPT_DIR && /usr/bin/python3 auto_post_daily.py --status publish >> logs/cron.log 2>&1"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "auto_post_daily.py"; then
        echo "Cron job already exists. Skipping."
    else
        # Add cron job
        (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
        echo "✓ Cron job added successfully"
    fi
    
    echo ""
    echo "Current crontab:"
    crontab -l | grep auto_post_daily.py || echo "(no matching entries)"
else
    # Manual setup
    echo ""
    echo "To manually set up the cron job:"
    echo "1. Run: crontab -e"
    echo "2. Add the following line:"
    echo ""
    echo "   0 10 * * * cd $SCRIPT_DIR && /usr/bin/python3 auto_post_daily.py --status publish >> logs/cron.log 2>&1"
    echo ""
    echo "3. If AI_API is not set globally, add it to the cron command:"
    echo ""
    echo "   0 10 * * * AI_API='your-api-key' cd $SCRIPT_DIR && /usr/bin/python3 auto_post_daily.py --status publish >> logs/cron.log 2>&1"
    echo ""
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Make sure AI_API environment variable is set"
echo "2. The script will run automatically every day at 10:00 AM"
echo "3. Check logs in: $SCRIPT_DIR/logs/"
echo "4. Monitor keyword usage: python3 keyword_manager.py --stats"
echo ""
echo "To test manually:"
echo "  python3 auto_post_daily.py --dry-run"
echo ""
echo "To post immediately:"
echo "  python3 auto_post_daily.py --status publish"
echo ""
