# Forest Survival - Enhanced Edition Deployment Guide

## 🚀 Deployment Overview

This guide covers deployment options for the Forest Survival Enhanced Edition, from development environments to production distribution.

## 📋 Prerequisites

### System Requirements

**Development Environment:**
- Python 3.8+ (3.10+ recommended)
- pip package manager
- Git version control
- 4GB RAM minimum, 8GB recommended
- 2GB free storage space

**Production Environment:**
- Same as development, plus:
- Web server (if deploying web version)
- CI/CD pipeline tools
- Distribution platforms access

### Dependencies

Install all required dependencies:
```bash
pip install -r requirements.txt
```

Core dependencies include:
- pygame >= 2.0.0
- numpy >= 1.20.0
- Additional system-specific packages

## 🏗️ Build Process

### 1. Development Build

For local development and testing:

```bash
# Clone repository
git clone https://github.com/TAR2003/Forest_Survival_GameJam2023_Project.git
cd Forest_Survival_GameJam2023_Project

# Install dependencies
pip install -r requirements.txt

# Run enhanced edition
python src/master_game_engine.py
```

### 2. Testing Build

Run comprehensive tests before deployment:

```bash
# Run all tests
python -m src.testing.comprehensive_test_suite

# Run integration tests
python -m src.testing.final_integration

# Check bug tracking system
python -c "from src.testing.bug_tracking import BugTrackingSystem; BugTrackingSystem().generate_status_report()"
```

### 3. Production Build

Create optimized build for distribution:

```bash
# Run final integration
python src/testing/final_integration.py

# Generate production executable (Windows)
pip install pyinstaller
pyinstaller --onefile --windowed main.py

# Or for enhanced edition
pyinstaller --onefile --add-data "src;src" --add-data "audio;audio" --add-data "pictures;pictures" src/master_game_engine.py
```

## 🎯 Deployment Methods

### Method 1: Standalone Executable

**Windows:**
```bash
# Create executable
pyinstaller --onefile --windowed --name "ForestSurvival-Enhanced" ^
    --add-data "audio;audio" ^
    --add-data "pictures;pictures" ^
    --add-data "src;src" ^
    src/master_game_engine.py

# Output: dist/ForestSurvival-Enhanced.exe
```

**macOS:**
```bash
# Create macOS app bundle
pyinstaller --onefile --windowed --name "ForestSurvival-Enhanced" \
    --add-data "audio:audio" \
    --add-data "pictures:pictures" \
    --add-data "src:src" \
    src/master_game_engine.py

# Create DMG (requires additional tools)
# Output: dist/ForestSurvival-Enhanced.app
```

**Linux:**
```bash
# Create Linux executable
pyinstaller --onefile --name "forest-survival-enhanced" \
    --add-data "audio:audio" \
    --add-data "pictures:pictures" \
    --add-data "src:src" \
    src/master_game_engine.py

# Output: dist/forest-survival-enhanced
```

### Method 2: Python Package Distribution

Create distributable Python package:

```bash
# Create setup.py
pip install setuptools wheel

# Build package
python setup.py sdist bdist_wheel

# Install from package
pip install dist/forest_survival_enhanced-1.0.0-py3-none-any.whl
```

### Method 3: Container Deployment

Docker containerization for cloud deployment:

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy game files
COPY . .

# Run game
CMD ["python", "src/master_game_engine.py"]
```

Build and run:
```bash
# Build image
docker build -t forest-survival-enhanced .

# Run container
docker run -it --rm forest-survival-enhanced
```

## 🌐 Platform-Specific Deployment

### Windows Distribution

1. **Executable Creation:**
   ```bash
   pyinstaller --onefile --windowed main.py
   ```

2. **Installer Creation (NSIS):**
   ```nsis
   ; Create Windows installer
   !include "MUI2.nsh"
   
   Name "Forest Survival Enhanced"
   OutFile "ForestSurvival-Enhanced-Setup.exe"
   InstallDir "$PROGRAMFILES\ForestSurvival"
   
   Section "MainSection" SEC01
     SetOutPath "$INSTDIR"
     File "dist\ForestSurvival-Enhanced.exe"
     File /r "audio"
     File /r "pictures"
   SectionEnd
   ```

3. **Microsoft Store Deployment:**
   - Package as MSIX
   - Submit to Microsoft Store
   - Follow Microsoft certification requirements

### macOS Distribution

1. **App Bundle Creation:**
   ```bash
   pyinstaller --windowed --onefile src/master_game_engine.py
   ```

2. **Code Signing:**
   ```bash
   codesign --force --verify --verbose --sign "Developer ID" ForestSurvival-Enhanced.app
   ```

3. **DMG Creation:**
   ```bash
   hdiutil create -volname "Forest Survival Enhanced" -srcfolder dist/ -ov ForestSurvival-Enhanced.dmg
   ```

4. **Mac App Store:**
   - Create App Store Connect listing
   - Package with Xcode
   - Submit for review

### Linux Distribution

1. **AppImage Creation:**
   ```bash
   # Create AppImage
   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
   chmod +x appimagetool-x86_64.AppImage
   ./appimagetool-x86_64.AppImage forest-survival.AppDir
   ```

2. **Snap Package:**
   ```yaml
   # snapcraft.yaml
   name: forest-survival-enhanced
   version: '1.0'
   summary: Enhanced forest survival game
   description: |
     Forest Survival Enhanced Edition with comprehensive new systems
   
   base: core20
   confinement: strict
   
   parts:
     forest-survival:
       plugin: python
       source: .
       python-requirements:
         - requirements.txt
   ```

3. **Flatpak Package:**
   ```json
   {
     "app-id": "com.github.tar2003.ForestSurvival",
     "runtime": "org.freedesktop.Platform",
     "runtime-version": "21.08",
     "sdk": "org.freedesktop.Sdk",
     "command": "forest-survival-enhanced"
   }
   ```

## 🔧 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/build-and-deploy.yml
name: Build and Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m src.testing.comprehensive_test_suite
        python src/testing/final_integration.py
  
  build:
    needs: test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: |
        pyinstaller --onefile --windowed --name "ForestSurvival-Enhanced" \
          --add-data "audio:audio" \
          --add-data "pictures:pictures" \
          --add-data "src:src" \
          src/master_game_engine.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: forest-survival-${{ matrix.os }}
        path: dist/
```

### Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/TAR2003/Forest_Survival_GameJam2023_Project.git'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'python -m src.testing.comprehensive_test_suite'
                sh 'python src/testing/final_integration.py'
            }
        }
        
        stage('Build') {
            steps {
                sh '''
                pip install pyinstaller
                pyinstaller --onefile --windowed --name "ForestSurvival-Enhanced" \\
                  --add-data "audio:audio" \\
                  --add-data "pictures:pictures" \\
                  --add-data "src:src" \\
                  src/master_game_engine.py
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                archiveArtifacts artifacts: 'dist/*', fingerprint: true
            }
        }
    }
}
```

## 📦 Distribution Platforms

### Game Distribution Platforms

1. **Steam:**
   - Use Steamworks SDK
   - Create Steam store page
   - Upload builds via SteamPipe
   - Set pricing and release date

2. **itch.io:**
   ```bash
   # Upload to itch.io
   # Create itch.io project
   # Upload executable and assets
   # Configure download settings
   ```

3. **Game Jolt:**
   - Create Game Jolt listing
   - Upload game files
   - Set up game page with screenshots

### General Software Platforms

1. **GitHub Releases:**
   ```bash
   # Create release with GitHub CLI
   gh release create v1.0.0 dist/ForestSurvival-Enhanced.exe \
     --title "Forest Survival Enhanced v1.0.0" \
     --notes "Enhanced edition with comprehensive new systems"
   ```

2. **SourceForge:**
   - Create project page
   - Upload release files
   - Configure download statistics

## 🔍 Quality Assurance

### Pre-Deployment Checklist

- [ ] All tests pass successfully
- [ ] Performance benchmarks meet requirements
- [ ] All assets load correctly
- [ ] Audio system functions properly
- [ ] UI elements responsive and accessible
- [ ] Save/load system works correctly
- [ ] Error handling tested
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] License information included

### Performance Validation

```bash
# Run performance tests
python -c "
from src.testing.comprehensive_test_suite import PerformanceTest
test = PerformanceTest()
results = test.execute()
print(f'Performance test results: {results}')
"

# Check memory usage
python -c "
from src.master_game_engine import MasterGameEngine
import psutil
engine = MasterGameEngine()
process = psutil.Process()
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

### Security Validation

```bash
# Check for security vulnerabilities
pip install safety bandit

# Scan dependencies
safety check

# Static security analysis
bandit -r src/
```

## 🚀 Deployment Environments

### Development Environment

```bash
# Local development setup
export FOREST_SURVIVAL_ENV=development
export DEBUG_MODE=true
python src/master_game_engine.py
```

### Staging Environment

```bash
# Staging environment setup
export FOREST_SURVIVAL_ENV=staging
export DEBUG_MODE=false
export PERFORMANCE_MONITORING=true
python src/master_game_engine.py
```

### Production Environment

```bash
# Production environment setup
export FOREST_SURVIVAL_ENV=production
export DEBUG_MODE=false
export PERFORMANCE_MONITORING=true
export ERROR_REPORTING=true
python src/master_game_engine.py
```

## 📊 Monitoring and Analytics

### Deployment Monitoring

1. **Performance Monitoring:**
   ```python
   # Enable performance monitoring
   from src.testing.comprehensive_test_suite import PerformanceMonitor
   
   monitor = PerformanceMonitor()
   monitor.start_monitoring()
   ```

2. **Error Tracking:**
   ```python
   # Enable error tracking
   from src.testing.bug_tracking import BugTrackingSystem
   
   bug_tracker = BugTrackingSystem()
   bug_tracker.enable_automatic_reporting()
   ```

3. **User Analytics:**
   ```python
   # Track user interactions
   from src.ui_ux.user_experience import UserExperience
   
   ux = UserExperience()
   ux.enable_analytics_tracking()
   ```

## 🔧 Troubleshooting

### Common Deployment Issues

1. **Missing Dependencies:**
   ```bash
   # Verify all dependencies
   pip check
   pip list --outdated
   ```

2. **Asset Loading Problems:**
   ```bash
   # Verify asset paths
   python -c "
   import os
   for root, dirs, files in os.walk('audio'):
       print(f'{root}: {len(files)} files')
   for root, dirs, files in os.walk('pictures'):
       print(f'{root}: {len(files)} files')
   "
   ```

3. **Performance Issues:**
   ```bash
   # Profile performance
   python -m cProfile -o profile_results.prof src/master_game_engine.py
   python -m pstats profile_results.prof
   ```

### Rollback Procedures

1. **Git Rollback:**
   ```bash
   # Rollback to previous version
   git revert HEAD
   git push origin main
   ```

2. **Package Rollback:**
   ```bash
   # Reinstall previous version
   pip install forest-survival-enhanced==0.9.0
   ```

## 📈 Post-Deployment

### Monitoring

1. Set up performance dashboards
2. Configure error alerting
3. Monitor user feedback
4. Track download statistics

### Updates

1. Plan regular update cycles
2. Maintain backward compatibility
3. Document changes in changelog
4. Test updates in staging first

### Support

1. Set up issue tracking system
2. Create user documentation
3. Provide community support channels
4. Monitor and respond to feedback

This deployment guide ensures professional distribution of the Forest Survival Enhanced Edition across multiple platforms and environments.