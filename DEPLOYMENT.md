# PRALAYA-NET Render Deployment Guide

## Python 3.13 Deployment Fix

This guide covers the fixes applied to resolve the `setuptools.build_meta` import error on Render.

## Problem
```
pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import 'setuptools.build_meta'
```

## Root Cause
- Outdated pip/setuptools/wheel versions on Render's Python 3.13 environment
- Missing PEP 517/518 build backend configuration
- Packages with incompatible Python 3.13 versions

## Files Modified

### 1. `backend/requirements_simple.txt` ✅
- Added explicit `setuptools>=70.0.0`, `wheel>=0.43.0`, `pip>=24.0`
- Updated all packages to Python 3.13 compatible versions

### 2. `backend/pyproject.toml` ✅ (NEW)
- Added proper `[build-system]` configuration
- Specified `build-backend = "setuptools.build_meta"`
- Defined project metadata for modern Python packaging

### 3. `backend/render.yaml` ✅
- Set `pythonVersion: "3.13"`
- Added pre-build command to upgrade pip/setuptools/wheel

### 4. `backend/Dockerfile` ✅
- Updated to Python 3.13
- Added early pip/setuptools/wheel upgrade

### 5. `render.yaml` ✅
- Updated build command to upgrade build tools first
- Fixed path to requirements file

### 6. `Dockerfile` (root) ✅
- Updated for root-level deployment

## Deployment Options

### Option 1: Direct Deploy (No Dockerfile)
1. Connect your repository to Render
2. Use these settings:
   - **Environment**: Python
   - **Python Version**: 3.13
   - **Build Command**:
     ```bash
     pip install --upgrade pip setuptools wheel && pip install -r backend/requirements_simple.txt
     ```
   - **Start Command**:
     ```bash
     cd backend && python main.py
     ```

### Option 2: Docker Deploy
1. Use the provided `Dockerfile` at root
2. Render will automatically detect and use it
3. Ensure `PYTHON_VERSION=3.13` environment variable is set

## Quick Test (Local)

```bash
# Test Python 3.13 compatibility
python --version  # Should be 3.13.x

# Upgrade build tools
pip install --upgrade pip setuptools wheel

# Test installation
cd backend
pip install -r requirements_simple.txt

# Verify installation
python -c "import setuptools; print(f'setuptools: {setuptools.__version__}')"
python -c "import uvicorn; print(f'uvicorn: {uvicorn.__version__}')"
python -c "import fastapi; print(f'fastapi: {fastapi.__version__}')"

# Run the app
python main.py
```

## Environment Variables for Render

Add these in Render dashboard:
```
PYTHON_VERSION=3.13
PORT=10000
HOST=0.0.0.0
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
PIP_DISABLE_PIP_VERSION_CHECK=1
DEMO_MODE=true
```

## Troubleshooting

### Still getting setuptools error?
Run this in your build command:
```bash
pip install --force-reinstall setuptools wheel pip
```

### Package not installing?
Check if the package supports Python 3.13:
```bash
pip index versions <package-name>
```

### torch/opencv-python issues?
These packages may not have Python 3.13 wheels yet. Use:
```bash
pip install --only-binary=:all: torch  # May fail
# OR
pip install torch --pre  # Try pre-release
```

## Rollback Plan

If Python 3.13 causes issues, downgrade to 3.11:
1. Change `pythonVersion: "3.11"` in render.yaml
2. Update requirements.txt with original versions
3. Redeploy

## Verification Checklist

- [ ] `pip --version` shows 24.0+
- [ ] `python -c "import setuptools; print(setuptools.__version__)"` shows 70.0+
- [ ] `pip install -r requirements_simple.txt` completes without errors
- [ ] Application starts: `python main.py`
- [ ] Health check passes: `curl http://localhost:8000/health`

## Support

If issues persist:
1. Check Render build logs for specific package errors
2. Try installing problematic packages individually
3. Consider using `requirements_simple.txt` (minimal dependencies) first

