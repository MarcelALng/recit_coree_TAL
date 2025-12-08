#!/usr/bin/env python3
"""
Master script to run all presidential speech scraping scripts sequentially.
Handles errors, logs progress, and supports resume capability.
"""

import subprocess
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path


class ScrapingOrchestrator:
    def __init__(self, config_file="config.json"):
        """Initialize the orchestrator with configuration."""
        self.config = self.load_config(config_file)
        self.state_file = self.config["execution"]["state_file"]
        self.state = self.load_state()
        self.log_file = self.config["scraping"]["log_file"]
        self.results = {
            "start_time": datetime.now().isoformat(),
            "scripts_executed": [],
            "scripts_failed": [],
            "scripts_skipped": []
        }
    
    def load_config(self, config_file):
        """Load configuration from JSON file."""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file {config_file} not found. Using defaults.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration."""
        return {
            "presidents": [
                "Yun_Bo_Seon", "Park_Chung_Hee", "Chun_Doo_Hwan",
                "Roh_Tae_Woo", "Kim_Young_Sam", "Kim_Dae_Jung",
                "Lee_Myung_Bak", "Park_Geun_Hye", "Moon_Jae_In"
            ],
            "scraping": {
                "retry_on_failure": True,
                "max_retries": 3,
                "delay_between_scripts": 2,
                "save_logs": True,
                "log_file": "scraping_log.txt"
            },
            "execution": {
                "run_scrap1": True,
                "run_scrap2": True,
                "resume_capability": True,
                "state_file": ".scraping_state.json"
            }
        }
    
    def load_state(self):
        """Load execution state for resume capability."""
        if not self.config["execution"]["resume_capability"]:
            return {"completed": []}
        
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"completed": []}
    
    def save_state(self):
        """Save current execution state."""
        if self.config["execution"]["resume_capability"]:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
    
    def log(self, message, level="INFO"):
        """Log message to console and file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        if self.config["scraping"]["save_logs"]:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
    
    def run_script(self, script_name, retries=0):
        """Execute a single scraping script."""
        if script_name in self.state["completed"]:
            self.log(f"⏭️  Skipping {script_name} (already completed)")
            self.results["scripts_skipped"].append(script_name)
            return True
        
        max_retries = self.config["scraping"]["max_retries"] if self.config["scraping"]["retry_on_failure"] else 0
        
        self.log(f"▶️  Running {script_name}...")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                self.log(f"✅ {script_name} completed successfully in {execution_time:.2f}s")
                self.state["completed"].append(script_name)
                self.save_state()
                self.results["scripts_executed"].append({
                    "script": script_name,
                    "status": "success",
                    "execution_time": execution_time
                })
                return True
            else:
                error_msg = result.stderr or result.stdout
                self.log(f"❌ {script_name} failed with exit code {result.returncode}", "ERROR")
                self.log(f"Error output: {error_msg[:500]}", "ERROR")
                
                if retries < max_retries:
                    self.log(f"🔄 Retrying {script_name} (attempt {retries + 1}/{max_retries})")
                    time.sleep(2)
                    return self.run_script(script_name, retries + 1)
                else:
                    self.results["scripts_failed"].append({
                        "script": script_name,
                        "error": error_msg[:500],
                        "exit_code": result.returncode
                    })
                    return False
        
        except subprocess.TimeoutExpired:
            self.log(f"⏱️  {script_name} timed out", "ERROR")
            self.results["scripts_failed"].append({
                "script": script_name,
                "error": "Timeout after 10 minutes"
            })
            return False
        
        except Exception as e:
            self.log(f"💥 Unexpected error running {script_name}: {e}", "ERROR")
            self.results["scripts_failed"].append({
                "script": script_name,
                "error": str(e)
            })
            return False
    
    def run_all(self):
        """Run all scraping scripts in sequence."""
        self.log("=" * 60)
        self.log("🚀 Starting Presidential Speeches Scraping Pipeline")
        self.log("=" * 60)
        
        presidents = self.config["presidents"]
        delay = self.config["scraping"]["delay_between_scripts"]
        
        # Phase 1: Run scrap1 scripts (collect links)
        if self.config["execution"]["run_scrap1"]:
            self.log("\n📋 Phase 1: Collecting article links (scrap1)")
            self.log("-" * 60)
            
            for president in presidents:
                script_name = f"scrap1_{president}.py"
                if os.path.exists(script_name):
                    self.run_script(script_name)
                    time.sleep(delay)
                else:
                    self.log(f"⚠️  Script {script_name} not found", "WARNING")
        
        # Phase 2: Run scrap2 scripts (extract full text)
        if self.config["execution"]["run_scrap2"]:
            self.log("\n📄 Phase 2: Extracting full text content (scrap2)")
            self.log("-" * 60)
            
            for president in presidents:
                script_name = f"scrap2_{president}.py"
                if os.path.exists(script_name):
                    self.run_script(script_name)
                    time.sleep(delay)
                else:
                    self.log(f"⚠️  Script {script_name} not found", "WARNING")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate and display execution summary."""
        self.results["end_time"] = datetime.now().isoformat()
        
        self.log("\n" + "=" * 60)
        self.log("📊 EXECUTION SUMMARY")
        self.log("=" * 60)
        
        total_executed = len(self.results["scripts_executed"])
        total_failed = len(self.results["scripts_failed"])
        total_skipped = len(self.results["scripts_skipped"])
        
        self.log(f"✅ Successfully executed: {total_executed}")
        self.log(f"❌ Failed: {total_failed}")
        self.log(f"⏭️  Skipped: {total_skipped}")
        
        if self.results["scripts_failed"]:
            self.log("\n❌ Failed scripts:")
            for failed in self.results["scripts_failed"]:
                self.log(f"  - {failed['script']}: {failed.get('error', 'Unknown error')[:100]}")
        
        # Save summary to JSON
        summary_file = f"scraping_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        self.log(f"\n💾 Summary saved to {summary_file}")
        self.log("=" * 60)
        
        return total_failed == 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run all presidential speech scraping scripts")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be executed without running")
    parser.add_argument("--reset", action="store_true", help="Reset state and run all scripts from scratch")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No scripts will be executed")
        orchestrator = ScrapingOrchestrator(args.config)
        print(f"\nPresidents to scrape: {orchestrator.config['presidents']}")
        print(f"Run scrap1: {orchestrator.config['execution']['run_scrap1']}")
        print(f"Run scrap2: {orchestrator.config['execution']['run_scrap2']}")
        print(f"Resume capability: {orchestrator.config['execution']['resume_capability']}")
        if orchestrator.state["completed"]:
            print(f"\nAlready completed: {orchestrator.state['completed']}")
        return
    
    orchestrator = ScrapingOrchestrator(args.config)
    
    if args.reset:
        orchestrator.log("🔄 Resetting state...")
        orchestrator.state = {"completed": []}
        orchestrator.save_state()
    
    success = orchestrator.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
