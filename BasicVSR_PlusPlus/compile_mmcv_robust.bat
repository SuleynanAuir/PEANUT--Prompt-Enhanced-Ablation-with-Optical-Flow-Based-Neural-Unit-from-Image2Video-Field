@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Building mmcv-full 1.6.0 from source
echo with CUDA 12.1 support
echo ========================================
echo.

REM Step 1: Setup Visual Studio environment
echo [1/5] Setting up Visual Studio 2022 environment...
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64
if errorlevel 1 (
    echo ERROR: Failed to setup Visual Studio environment
    pause
    exit /b 1
)
echo ✓ Visual Studio environment ready
echo.

REM Step 2: Activate conda environment
echo [2/5] Activating conda environment...
call conda activate basicvsrpp-demo
if errorlevel 1 (
    echo ERROR: Failed to activate conda environment
    pause
    exit /b 1
)
echo ✓ Conda environment activated
echo.

REM Step 3: Set compilation flags
echo [3/5] Setting compilation environment variables...
set MMCV_WITH_OPS=1
set FORCE_CUDA=1
set TORCH_CUDA_ARCH_LIST=8.6+PTX
set MAX_JOBS=4
echo ✓ Environment variables set
echo   MMCV_WITH_OPS=!MMCV_WITH_OPS!
echo   FORCE_CUDA=!FORCE_CUDA!
echo   MAX_JOBS=!MAX_JOBS!
echo.

REM Step 4: Clean previous installations
echo [4/5] Cleaning previous mmcv installations...
pip uninstall -y mmcv mmcv-full 2>nul
echo ✓ Cleaned
echo.

REM Step 5: Download and build mmcv from source
echo [5/5] Downloading and compiling mmcv-full 1.6.0...
echo This will take 15-30 minutes. Please be patient...
echo.

cd /d C:\Users\Aiur\BasicVSR_PlusPlus

REM Clone if not exists
if not exist "mmcv-1.6.0" (
    echo Downloading mmcv source code...
    git clone -b v1.6.0 --depth 1 https://github.com/open-mmlab/mmcv.git mmcv-1.6.0
    if errorlevel 1 (
        echo ERROR: Failed to download mmcv source
        echo Trying alternative method...
        
        REM Alternative: download zip
        powershell -Command "Invoke-WebRequest -Uri 'https://github.com/open-mmlab/mmcv/archive/refs/tags/v1.6.0.zip' -OutFile 'mmcv-1.6.0.zip'"
        powershell -Command "Expand-Archive -Path 'mmcv-1.6.0.zip' -DestinationPath '.'"
        rename mmcv-1.6.0 mmcv-1.6.0-src
        move mmcv-1.6.0-src mmcv-1.6.0
    )
)

cd mmcv-1.6.0

echo.
echo ======================================
echo Starting compilation...
echo ======================================
echo.

pip install -e . -v --no-build-isolation

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Compilation failed!
    echo ========================================
    echo.
    echo This could be due to:
    echo 1. Missing CUDA Toolkit 12.1
    echo 2. Incompatible Visual Studio version
    echo 3. Network issues during compilation
    echo.
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo ✓ Compilation successful!
echo ========================================
echo.

REM Verify installation
echo Verifying installation...
python -c "import mmcv; print('mmcv version:', mmcv.__version__)"
echo.
python -c "from mmcv.ops import ModulatedDeformConv2d; print('✓ CUDA extensions (DCN) loaded successfully!')"

if errorlevel 1 (
    echo.
    echo WARNING: CUDA extensions not loaded properly
    echo You may need to check CUDA installation
    pause
    exit /b 1
)

echo.
echo ========================================
echo All done! Ready to run BasicVSR++ demo
echo ========================================
echo.
pause
