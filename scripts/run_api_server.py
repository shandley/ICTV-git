#!/usr/bin/env python3
"""
ICTV-Git API Server Runner

Launch the REST API server for the complete 20-year taxonomy system.
Provides comprehensive viral taxonomy data access with AI-powered features.
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse


def check_repository_path(repo_path: str) -> bool:
    """Verify the taxonomy repository exists and is valid"""
    repo_dir = Path(repo_path)
    
    if not repo_dir.exists():
        print(f"❌ Repository not found: {repo_path}")
        return False
    
    # Check for git repository
    if not (repo_dir / '.git').exists():
        print(f"❌ Not a git repository: {repo_path}")
        return False
    
    # Check for families directory
    if not (repo_dir / 'families').exists():
        print(f"❌ Missing families directory: {repo_path}/families")
        return False
    
    print(f"✅ Repository validated: {repo_path}")
    return True


def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import fastapi
        import uvicorn
        import yaml
        import pydantic
        print("✅ Core API dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing required dependency: {e}")
        print("Install with: pip install -r requirements_api.txt")
        return False


def install_dependencies():
    """Install API dependencies"""
    requirements_file = Path(__file__).parent.parent / "requirements_api.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    print(f"📦 Installing dependencies from {requirements_file}")
    try:
        # Try pip3 first, then fall back to pip
        pip_command = "pip3" if subprocess.run(["which", "pip3"], capture_output=True).returncode == 0 else "pip"
        subprocess.run([
            pip_command, "install", "-r", str(requirements_file)
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def run_server(repo_path: str, host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server"""
    
    # Set environment variable for repository path
    os.environ['ICTV_REPO_PATH'] = repo_path
    
    # Add src directory to Python path
    src_dir = Path(__file__).parent.parent / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    print(f"🚀 Starting ICTV-Git API Server")
    print(f"📂 Repository: {repo_path}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📖 Documentation: http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {reload}")
    print("-" * 50)
    
    try:
        import uvicorn
        from api.rest_server import app
        
        uvicorn.run(
            "api.rest_server:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements_api.txt")
    except Exception as e:
        print(f"❌ Server error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Run ICTV-Git API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python scripts/run_api_server.py

  # Specify custom repository path
  python scripts/run_api_server.py --repo /path/to/taxonomy/repo

  # Run in development mode with auto-reload
  python scripts/run_api_server.py --dev

  # Custom host and port
  python scripts/run_api_server.py --host 127.0.0.1 --port 8080

  # Install dependencies first
  python scripts/run_api_server.py --install-deps
        """
    )
    
    parser.add_argument(
        "--repo", 
        default="/Users/scotthandley/Code/ICTV-git/output/ictv_complete_20_year_taxonomy",
        help="Path to ICTV taxonomy repository"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0", 
        help="Host to bind server to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run server on (default: 8000)"
    )
    
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run in development mode with auto-reload"
    )
    
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install required dependencies before starting"
    )
    
    parser.add_argument(
        "--check-only",
        action="store_true", 
        help="Only check repository and dependencies, don't start server"
    )
    
    args = parser.parse_args()
    
    print("🦠 ICTV-Git API Server")
    print("=" * 50)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
        print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n💡 Install dependencies with: python scripts/run_api_server.py --install-deps")
        sys.exit(1)
    
    # Check repository
    if not check_repository_path(args.repo):
        print(f"\n💡 Expected repository at: {args.repo}")
        print("Run the complete 20-year conversion first:")
        print("  python scripts/complete_20_year_conversion.py")
        sys.exit(1)
    
    if args.check_only:
        print("\n✅ All checks passed - ready to run server")
        sys.exit(0)
    
    # Run server
    run_server(
        repo_path=args.repo,
        host=args.host,
        port=args.port,
        reload=args.dev
    )


if __name__ == "__main__":
    main()