# Presidential Speeches Scraping Automation

Automated pipeline to scrape Korean presidential speeches from the Presidential Archives and push results to GitHub.

## 🎯 Features

- **Automated Execution**: Run all scraping scripts sequentially with a single command
- **Resume Capability**: Automatically resume from where it stopped if interrupted
- **Error Handling**: Retry failed scripts and continue with remaining ones
- **Git Integration**: Automatically commit and push results to GitHub
- **Detailed Logging**: Track execution progress and errors
- **Configurable**: Easy configuration via JSON file

## 📋 Prerequisites

- Python 3.7+
- Git installed
- Virtual environment activated
- GitHub repository (optional, for auto-push)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

Edit `config.json` to set your GitHub repository URL:

```json
{
  "github": {
    "repository_url": "https://github.com/your-username/your-repo.git",
    "branch": "main"
  }
}
```

### 3. Run All Scrapers

```bash
python run_all_scrapers.py
```

### 4. Push to GitHub

```bash
python git_push_results.py
```

## 📖 Detailed Usage

### Running Scrapers

**Run all scripts:**
```bash
python run_all_scrapers.py
```

**Dry run (see what would be executed):**
```bash
python run_all_scrapers.py --dry-run
```

**Reset state and run from scratch:**
```bash
python run_all_scrapers.py --reset
```

**Custom configuration file:**
```bash
python run_all_scrapers.py --config my_config.json
```

### Git Operations

**Commit and push results:**
```bash
python git_push_results.py
```

**Dry run (see what would be committed):**
```bash
python git_push_results.py --dry-run
```

**Custom configuration:**
```bash
python git_push_results.py --config my_config.json
```

## ⚙️ Configuration

The `config.json` file controls all aspects of the automation:

```json
{
  "github": {
    "repository_url": "",           // Your GitHub repo URL
    "branch": "main",                // Target branch
    "commit_message_template": "Update presidential speeches data - {timestamp}",
    "auto_push": true                // Auto-push after commit
  },
  "presidents": [                    // List of presidents to scrape
    "Yun_Bo_Seon",
    "Park_Chung_Hee",
    // ... more presidents
  ],
  "scraping": {
    "retry_on_failure": true,        // Retry failed scripts
    "max_retries": 3,                // Max retry attempts
    "delay_between_scripts": 2,      // Seconds between scripts
    "save_logs": true,               // Save logs to file
    "log_file": "scraping_log.txt"   // Log file path
  },
  "execution": {
    "run_scrap1": true,              // Run link collection scripts
    "run_scrap2": true,              // Run text extraction scripts
    "resume_capability": true,       // Enable resume on interrupt
    "state_file": ".scraping_state.json"  // State file path
  }
}
```

## 📁 Output Files

### JSON Data Files
- `president_links_*.json` - Article links for each president
- `president_texts_*.json` - Full text content for each president

### Log Files
- `scraping_log.txt` - Detailed execution log
- `scraping_summary_*.json` - Execution summary with statistics
- `.scraping_state.json` - Resume state (auto-generated)

## 🔧 Git Authentication

### Option 1: SSH Keys (Recommended)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: Settings > SSH and GPG keys
cat ~/.ssh/id_ed25519.pub

# Test connection
ssh -T git@github.com

# Use SSH URL in config.json
"repository_url": "git@github.com:username/repo.git"
```

### Option 2: Personal Access Token

```bash
# Create token: GitHub > Settings > Developer settings > Personal access tokens
# Use HTTPS URL with token in config.json
"repository_url": "https://github.com/username/repo.git"

# Configure Git to cache credentials
git config --global credential.helper cache
```

### Option 3: GitHub CLI

```bash
# Install and authenticate
gh auth login

# Use HTTPS URL in config.json
"repository_url": "https://github.com/username/repo.git"
```

## 🔄 Complete Workflow

Run everything with one command:

```bash
# Run all scrapers and push to GitHub
python run_all_scrapers.py && python git_push_results.py
```

Or create a shell script `run_pipeline.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting scraping pipeline..."
source venv/bin/activate

echo "📥 Running scrapers..."
python run_all_scrapers.py

if [ $? -eq 0 ]; then
    echo "📤 Pushing to GitHub..."
    python git_push_results.py
    echo "✅ Pipeline completed successfully!"
else
    echo "❌ Scraping failed. Skipping Git push."
    exit 1
fi
```

Make it executable:
```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

## 📊 Execution Summary

After running, check the summary JSON file for detailed statistics:

```json
{
  "start_time": "2025-12-08T22:00:00",
  "end_time": "2025-12-08T22:30:00",
  "scripts_executed": [
    {
      "script": "scrap1_Park_Chung_Hee.py",
      "status": "success",
      "execution_time": 45.23
    }
  ],
  "scripts_failed": [],
  "scripts_skipped": []
}
```

## 🐛 Troubleshooting

### Scripts fail with import errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Git push fails with authentication error
```bash
# Check remote URL
git remote -v

# Test SSH connection
ssh -T git@github.com

# Or configure credentials for HTTPS
git config --global credential.helper store
```

### Resume not working
```bash
# Check state file exists
cat .scraping_state.json

# Reset state if corrupted
python run_all_scrapers.py --reset
```

## 📝 Presidents Covered

1. Yun Bo-seon (윤보선) - 1960-1962
2. Park Chung-hee (박정희) - 1963-1979
3. Chun Doo-hwan (전두환) - 1980-1988
4. Roh Tae-woo (노태우) - 1988-1993
5. Kim Young-sam (김영삼) - 1993-1998
6. Kim Dae-jung (김대중) - 1998-2003
7. Lee Myung-bak (이명박) - 2008-2013
8. Park Geun-hye (박근혜) - 2013-2017
9. Moon Jae-in (문재인) - 2017-2022

## 📄 License

This project is for educational and research purposes.

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the automation pipeline.
