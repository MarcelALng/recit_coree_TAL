#!/bin/bash
# Complete automation pipeline: scrape and push to GitHub

set -e  # Exit on error

echo "=" 
echo "🚀 Presidential Speeches Scraping Pipeline"
echo "="

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Please create one first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Run scrapers
echo ""
echo "📥 Phase 1: Running all scraping scripts..."
echo "---"
python run_all_scrapers.py

# Check if scraping was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Scraping completed successfully!"
    
    # Ask user if they want to push to GitHub
    echo ""
    read -p "📤 Push results to GitHub? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Phase 2: Pushing to GitHub..."
        echo "---"
        python git_push_results.py
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "=" 
            echo "✅ Pipeline completed successfully!"
            echo "="
        else
            echo ""
            echo "⚠️  Git push failed, but data is saved locally"
            exit 1
        fi
    else
        echo "⏭️  Skipping GitHub push"
        echo "   You can push manually later with: python git_push_results.py"
    fi
else
    echo ""
    echo "❌ Scraping failed. Check scraping_log.txt for details."
    exit 1
fi
