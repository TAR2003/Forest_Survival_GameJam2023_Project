#!/usr/bin/env python3
"""
Forest Survival Enhanced Edition - Deployment Automation Script
Automates the complete deployment process for the enhanced game.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime

class DeploymentAutomation:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.docs_dir = self.project_root / "docs"
        
        # Deployment configuration
        self.config = {
            "version": "2.0.0",
            "app_name": "ForestSurvival-Enhanced",
            "description": "Forest Survival Enhanced Edition with comprehensive new systems",
            "author": "TAR2003",
            "platforms": ["windows", "linux", "macos"],
            "python_version": "3.10"
        }
    
    def log(self, message, level="INFO"):
        """Log deployment messages with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def run_command(self, command, description):
        """Run a command and handle errors."""
        self.log(f"Running: {description}")
        try:
            result = subprocess.run(command, shell=True, check=True, 
                                  capture_output=True, text=True)
            self.log(f"Success: {description}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.log(f"Error in {description}: {e.stderr}", "ERROR")
            return None
    
    def validate_environment(self):
        """Validate that the deployment environment is ready."""
        self.log("Validating deployment environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            self.log("Python 3.8+ required for deployment", "ERROR")
            return False
        
        # Check if required files exist
        required_files = [
            "main.py",
            "src/master_game_engine.py",
            "requirements.txt",
            "README.md"
        ]
        
        for file in required_files:
            if not (self.project_root / file).exists():
                self.log(f"Required file missing: {file}", "ERROR")
                return False
        
        # Check if audio and pictures directories exist
        if not (self.project_root / "audio").exists():
            self.log("Audio directory missing", "ERROR")
            return False
        
        if not (self.project_root / "pictures").exists():
            self.log("Pictures directory missing", "ERROR")
            return False
        
        self.log("Environment validation passed")
        return True
    
    def run_tests(self):
        """Run comprehensive tests before deployment."""
        self.log("Running comprehensive test suite...")
        
        # Import and run tests
        try:
            sys.path.append(str(self.project_root / "src"))
            from testing.comprehensive_test_suite import ComprehensiveTestSuite
            from testing.final_integration import FinalIntegrationCoordinator
            
            # Run comprehensive tests
            test_suite = ComprehensiveTestSuite()
            test_results = test_suite.run_all_tests()
            
            if test_results["failed"] > 0:
                self.log(f"Tests failed: {test_results['failed']} failures", "ERROR")
                return False
            
            # Run integration tests
            integration = FinalIntegrationCoordinator()
            integration_results = integration.run_full_integration()
            
            if not integration_results["success"]:
                self.log("Integration tests failed", "ERROR")
                return False
            
            self.log("All tests passed successfully")
            return True
            
        except Exception as e:
            self.log(f"Error running tests: {str(e)}", "ERROR")
            return False
    
    def clean_build_directories(self):
        """Clean previous build artifacts."""
        self.log("Cleaning build directories...")
        
        for directory in [self.dist_dir, self.build_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                self.log(f"Cleaned {directory}")
        
        self.dist_dir.mkdir(exist_ok=True)
        self.log("Build directories prepared")
    
    def install_dependencies(self):
        """Install required dependencies for deployment."""
        self.log("Installing deployment dependencies...")
        
        # Install core requirements
        result = self.run_command(
            "pip install -r requirements.txt",
            "Installing core requirements"
        )
        if not result:
            return False
        
        # Install deployment tools
        deployment_deps = [
            "pyinstaller>=4.10",
            "setuptools>=60.0.0",
            "wheel>=0.37.0"
        ]
        
        for dep in deployment_deps:
            result = self.run_command(
                f"pip install {dep}",
                f"Installing {dep}"
            )
            if not result:
                return False
        
        self.log("Dependencies installed successfully")
        return True
    
    def build_executable(self, platform="current"):
        """Build executable for specified platform."""
        self.log(f"Building executable for {platform}...")
        
        # PyInstaller command for enhanced edition
        pyinstaller_cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            f"--name={self.config['app_name']}",
            "--add-data=audio;audio",
            "--add-data=pictures;pictures", 
            "--add-data=src;src",
            "--add-data=docs;docs",
            "--hidden-import=pygame",
            "--hidden-import=numpy",
            "--hidden-import=psutil",
            "src/master_game_engine.py"
        ]
        
        # Adjust path separators for different platforms
        if platform == "linux" or platform == "macos":
            pyinstaller_cmd = [cmd.replace(";", ":") if "add-data" in cmd else cmd 
                             for cmd in pyinstaller_cmd]
        
        result = self.run_command(
            " ".join(pyinstaller_cmd),
            f"Building {platform} executable"
        )
        
        if result:
            self.log(f"Executable built successfully for {platform}")
            return True
        else:
            return False
    
    def create_distribution_package(self):
        """Create complete distribution package."""
        self.log("Creating distribution package...")
        
        package_dir = self.dist_dir / f"{self.config['app_name']}-{self.config['version']}"
        package_dir.mkdir(exist_ok=True)
        
        # Copy executable
        exe_name = f"{self.config['app_name']}.exe"
        if sys.platform.startswith("linux"):
            exe_name = self.config['app_name'].lower().replace("-", "_")
        elif sys.platform == "darwin":
            exe_name = f"{self.config['app_name']}.app"
        
        exe_path = self.dist_dir / exe_name
        if exe_path.exists():
            if exe_path.is_dir():
                shutil.copytree(exe_path, package_dir / exe_name)
            else:
                shutil.copy2(exe_path, package_dir / exe_name)
        
        # Copy documentation
        docs_to_copy = ["README.md", "LICENSE", "requirements.txt"]
        for doc in docs_to_copy:
            doc_path = self.project_root / doc
            if doc_path.exists():
                shutil.copy2(doc_path, package_dir / doc)
        
        # Copy docs directory
        if self.docs_dir.exists():
            shutil.copytree(self.docs_dir, package_dir / "docs")
        
        # Create version info file
        version_info = {
            "version": self.config["version"],
            "build_date": datetime.now().isoformat(),
            "description": self.config["description"],
            "author": self.config["author"],
            "python_version": sys.version,
            "platform": sys.platform
        }
        
        with open(package_dir / "version_info.json", "w") as f:
            json.dump(version_info, f, indent=2)
        
        # Create installation instructions
        install_instructions = self.create_installation_instructions()
        with open(package_dir / "INSTALL.txt", "w") as f:
            f.write(install_instructions)
        
        self.log(f"Distribution package created: {package_dir}")
        return package_dir
    
    def create_installation_instructions(self):
        """Generate installation instructions for the package."""
        return f"""
Forest Survival Enhanced Edition v{self.config['version']}
Installation Instructions

QUICK START:
1. Run {self.config['app_name']}.exe (Windows) or the executable for your platform
2. Enjoy the enhanced forest survival experience!

REQUIREMENTS:
- Windows 10/11, macOS 10.14+, or Linux Ubuntu 18.04+
- 4GB RAM minimum, 8GB recommended
- 2GB free storage space
- DirectX 11 compatible graphics (Windows)

FEATURES:
- Enhanced game engine with comprehensive new systems
- Professional testing framework and bug tracking
- Advanced visual and audio effects
- Comprehensive documentation and API reference

RUNNING FROM SOURCE:
If you prefer to run from source code:
1. Install Python 3.8+ (3.10+ recommended)
2. pip install -r requirements.txt
3. python src/master_game_engine.py

DOCUMENTATION:
- README.md: Complete game overview and features
- docs/API_DOCUMENTATION.md: Developer API reference
- docs/DEPLOYMENT_GUIDE.md: Deployment instructions
- docs/CHANGELOG.md: Version history and changes

SUPPORT:
- GitHub Issues: Report bugs and request features
- Documentation: Comprehensive guides and API reference
- Community: Game development community support

BUILD INFORMATION:
- Version: {self.config['version']}
- Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Python Version: {sys.version}
- Platform: {sys.platform}

LICENSE:
See LICENSE file for licensing information.

Enjoy the enhanced forest survival experience!
"""
    
    def create_archive(self, package_dir):
        """Create compressed archive of the distribution package."""
        self.log("Creating distribution archive...")
        
        # Create ZIP archive
        archive_name = f"{self.config['app_name']}-{self.config['version']}-{sys.platform}"
        shutil.make_archive(
            str(self.dist_dir / archive_name),
            "zip",
            str(package_dir.parent),
            package_dir.name
        )
        
        archive_path = self.dist_dir / f"{archive_name}.zip"
        self.log(f"Distribution archive created: {archive_path}")
        return archive_path
    
    def generate_deployment_report(self, success=True):
        """Generate deployment report."""
        self.log("Generating deployment report...")
        
        report = {
            "deployment_info": {
                "version": self.config["version"],
                "timestamp": datetime.now().isoformat(),
                "success": success,
                "platform": sys.platform,
                "python_version": sys.version
            },
            "build_artifacts": [],
            "distribution_files": []
        }
        
        # List build artifacts
        if self.dist_dir.exists():
            for item in self.dist_dir.iterdir():
                if item.is_file():
                    report["build_artifacts"].append({
                        "name": item.name,
                        "size": item.stat().st_size,
                        "type": "file"
                    })
                elif item.is_dir():
                    report["build_artifacts"].append({
                        "name": item.name,
                        "type": "directory"
                    })
        
        # Save report
        report_path = self.dist_dir / "deployment_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Deployment report saved: {report_path}")
        return report
    
    def deploy(self, run_tests=True, create_archive=True):
        """Run complete deployment process."""
        self.log("Starting Forest Survival Enhanced Edition deployment...")
        self.log(f"Version: {self.config['version']}")
        self.log(f"Platform: {sys.platform}")
        
        try:
            # Step 1: Validate environment
            if not self.validate_environment():
                raise Exception("Environment validation failed")
            
            # Step 2: Run tests (optional)
            if run_tests:
                if not self.run_tests():
                    raise Exception("Tests failed")
            
            # Step 3: Clean and prepare
            self.clean_build_directories()
            
            # Step 4: Install dependencies
            if not self.install_dependencies():
                raise Exception("Dependency installation failed")
            
            # Step 5: Build executable
            if not self.build_executable():
                raise Exception("Executable build failed")
            
            # Step 6: Create distribution package
            package_dir = self.create_distribution_package()
            
            # Step 7: Create archive (optional)
            archive_path = None
            if create_archive:
                archive_path = self.create_archive(package_dir)
            
            # Step 8: Generate report
            self.generate_deployment_report(success=True)
            
            self.log("Deployment completed successfully!")
            self.log(f"Distribution package: {package_dir}")
            if archive_path:
                self.log(f"Distribution archive: {archive_path}")
            
            return True
            
        except Exception as e:
            self.log(f"Deployment failed: {str(e)}", "ERROR")
            self.generate_deployment_report(success=False)
            return False

def main():
    """Main deployment script entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Forest Survival Enhanced Edition Deployment Automation"
    )
    parser.add_argument(
        "--skip-tests", 
        action="store_true", 
        help="Skip running tests before deployment"
    )
    parser.add_argument(
        "--no-archive", 
        action="store_true", 
        help="Skip creating distribution archive"
    )
    parser.add_argument(
        "--platform", 
        choices=["current", "windows", "linux", "macos"], 
        default="current",
        help="Target platform for deployment"
    )
    
    args = parser.parse_args()
    
    # Create deployment automation instance
    deployer = DeploymentAutomation()
    
    # Update platform if specified
    if args.platform != "current":
        deployer.log(f"Note: Cross-platform builds require platform-specific setup")
    
    # Run deployment
    success = deployer.deploy(
        run_tests=not args.skip_tests,
        create_archive=not args.no_archive
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()