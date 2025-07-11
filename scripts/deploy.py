#!/usr/bin/env python3
"""
Deployment script for YouTube Summarizer.

This script automates deployment tasks for different environments.
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from datetime import datetime


def run_command(command, check=True, shell=False, cwd=None):
    """Run a command and return the result."""
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True, cwd=cwd)
        else:
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True, cwd=cwd)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None


def check_git_status():
    """Check if git repository is clean."""
    print("🔍 Checking git status...")
    
    result = run_command("git status --porcelain")
    if result is None:
        print("❌ Failed to check git status")
        return False
    
    if result.stdout.strip():
        print("⚠️  Working directory is not clean:")
        print(result.stdout)
        response = input("Continue anyway? (y/N): ").lower()
        return response == 'y'
    
    print("✅ Working directory is clean")
    return True


def run_tests():
    """Run tests before deployment."""
    print("🧪 Running tests...")
    
    result = run_command("python -m pytest tests/ -v --tb=short")
    if result is None or result.returncode != 0:
        print("❌ Tests failed!")
        if result:
            print(result.stdout)
            print(result.stderr)
        return False
    
    print("✅ All tests passed")
    return True


def build_docker_image(tag=None):
    """Build Docker image."""
    if tag is None:
        tag = f"youtube-summarizer:{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print(f"🐳 Building Docker image: {tag}")
    
    result = run_command(f"docker build -t {tag} .")
    if result is None:
        print("❌ Failed to build Docker image")
        return False, None
    
    print(f"✅ Docker image built: {tag}")
    return True, tag


def deploy_heroku():
    """Deploy to Heroku."""
    print("🚀 Deploying to Heroku...")
    
    # Check if Heroku CLI is installed
    result = run_command("heroku --version", check=False)
    if result is None or result.returncode != 0:
        print("❌ Heroku CLI is not installed")
        return False
    
    # Check if logged in
    result = run_command("heroku auth:whoami", check=False)
    if result is None or result.returncode != 0:
        print("❌ Not logged in to Heroku. Run: heroku login")
        return False
    
    # Deploy
    result = run_command("git push heroku main")
    if result is None:
        print("❌ Failed to deploy to Heroku")
        return False
    
    print("✅ Deployed to Heroku successfully")
    return True


def deploy_vercel():
    """Deploy to Vercel."""
    print("🚀 Deploying to Vercel...")
    
    # Check if Vercel CLI is installed
    result = run_command("vercel --version", check=False)
    if result is None or result.returncode != 0:
        print("❌ Vercel CLI is not installed. Run: npm i -g vercel")
        return False
    
    # Deploy
    result = run_command("vercel --prod")
    if result is None:
        print("❌ Failed to deploy to Vercel")
        return False
    
    print("✅ Deployed to Vercel successfully")
    return True


def deploy_railway():
    """Deploy to Railway."""
    print("🚀 Deploying to Railway...")
    
    # Check if Railway CLI is installed
    result = run_command("railway --version", check=False)
    if result is None or result.returncode != 0:
        print("❌ Railway CLI is not installed. Run: npm i -g @railway/cli")
        return False
    
    # Deploy
    result = run_command("railway up")
    if result is None:
        print("❌ Failed to deploy to Railway")
        return False
    
    print("✅ Deployed to Railway successfully")
    return True


def deploy_docker_registry(image_tag, registry_url):
    """Deploy to Docker registry."""
    print(f"🐳 Deploying to Docker registry: {registry_url}")
    
    # Tag image for registry
    registry_tag = f"{registry_url}/{image_tag}"
    result = run_command(f"docker tag {image_tag} {registry_tag}")
    if result is None:
        print("❌ Failed to tag image for registry")
        return False
    
    # Push to registry
    result = run_command(f"docker push {registry_tag}")
    if result is None:
        print("❌ Failed to push to registry")
        return False
    
    print(f"✅ Deployed to registry: {registry_tag}")
    return True


def update_version():
    """Update version information."""
    print("📝 Updating version information...")
    
    version_file = Path("version.json")
    
    if version_file.exists():
        with open(version_file, 'r') as f:
            version_data = json.load(f)
    else:
        version_data = {"version": "1.0.0", "build": 0}
    
    # Increment build number
    version_data["build"] += 1
    version_data["deployed_at"] = datetime.now().isoformat()
    
    # Get git commit hash
    result = run_command("git rev-parse HEAD", check=False)
    if result and result.returncode == 0:
        version_data["commit"] = result.stdout.strip()[:8]
    
    with open(version_file, 'w') as f:
        json.dump(version_data, f, indent=2)
    
    print(f"✅ Version updated: {version_data['version']}.{version_data['build']}")
    return version_data


def create_deployment_backup():
    """Create a backup before deployment."""
    print("💾 Creating deployment backup...")
    
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{timestamp}.tar.gz"
    
    # Create backup excluding unnecessary files
    exclude_patterns = [
        "--exclude=venv",
        "--exclude=__pycache__",
        "--exclude=*.pyc",
        "--exclude=.git",
        "--exclude=cache",
        "--exclude=logs",
        "--exclude=backups"
    ]
    
    exclude_str = " ".join(exclude_patterns)
    result = run_command(f"tar -czf {backup_file} {exclude_str} .", shell=True)
    
    if result is None:
        print("❌ Failed to create backup")
        return False
    
    print(f"✅ Backup created: {backup_file}")
    return True


def validate_environment(env):
    """Validate environment configuration."""
    print(f"🔍 Validating {env} environment...")
    
    required_vars = {
        'production': ['SECRET_KEY', 'FLASK_ENV'],
        'staging': ['SECRET_KEY', 'FLASK_ENV'],
        'development': ['FLASK_ENV']
    }
    
    env_file = Path(f".env.{env}")
    if not env_file.exists():
        env_file = Path(".env")
    
    if not env_file.exists():
        print(f"❌ Environment file not found: {env_file}")
        return False
    
    # Read environment variables
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    # Check required variables
    missing_vars = []
    for var in required_vars.get(env, []):
        if var not in env_vars or not env_vars[var]:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print(f"✅ Environment validation passed")
    return True


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy YouTube Summarizer")
    parser.add_argument("platform", choices=["heroku", "vercel", "railway", "docker"], 
                       help="Deployment platform")
    parser.add_argument("--env", choices=["development", "staging", "production"], 
                       default="production", help="Environment")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-git-check", action="store_true", help="Skip git status check")
    parser.add_argument("--docker-tag", help="Docker image tag")
    parser.add_argument("--registry", help="Docker registry URL")
    parser.add_argument("--force", action="store_true", help="Force deployment")
    
    args = parser.parse_args()
    
    print("🚀 YouTube Summarizer Deployment")
    print("=" * 50)
    print(f"Platform: {args.platform}")
    print(f"Environment: {args.env}")
    print()
    
    # Pre-deployment checks
    if not args.skip_git_check and not check_git_status():
        if not args.force:
            print("❌ Deployment cancelled")
            sys.exit(1)
    
    if not validate_environment(args.env):
        if not args.force:
            print("❌ Deployment cancelled")
            sys.exit(1)
    
    if not args.skip_tests and not run_tests():
        if not args.force:
            print("❌ Deployment cancelled")
            sys.exit(1)
    
    # Create backup
    if not create_deployment_backup():
        print("⚠️  Failed to create backup, continuing anyway...")
    
    # Update version
    version_data = update_version()
    
    # Deploy based on platform
    success = False
    
    if args.platform == "heroku":
        success = deploy_heroku()
    elif args.platform == "vercel":
        success = deploy_vercel()
    elif args.platform == "railway":
        success = deploy_railway()
    elif args.platform == "docker":
        docker_success, image_tag = build_docker_image(args.docker_tag)
        if docker_success:
            if args.registry:
                success = deploy_docker_registry(image_tag, args.registry)
            else:
                success = True
                print(f"✅ Docker image ready: {image_tag}")
    
    if success:
        print("\n🎉 Deployment completed successfully!")
        print(f"Version: {version_data['version']}.{version_data['build']}")
        if 'commit' in version_data:
            print(f"Commit: {version_data['commit']}")
        print(f"Deployed at: {version_data['deployed_at']}")
    else:
        print("\n❌ Deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
