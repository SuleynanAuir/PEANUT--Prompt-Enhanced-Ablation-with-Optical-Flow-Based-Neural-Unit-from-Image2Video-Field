@echo off
echo ========================================
echo Building mmcv-full from source
echo ========================================

REM Activate Visual Studio 2022 Build Tools environment
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64

REM Activate conda environment
call conda activate basicvsrpp-demo

REM Set environment variables for mmcv compilation
set MMCV_WITH_OPS=1
set FORCE_CUDA=1
set MAX_JOBS=4

REM Uninstall existing mmcv
pip uninstall -y mmcv mmcv-full

REM Clone mmcv repository
cd /d C:\Users\Aiur\BasicVSR_PlusPlus
if exist mmcv-build rmdir /s /q mmcv-build
git clone -b v1.6.0 https://github.com/open-mmlab/mmcv.git mmcv-build
cd mmcv-build

echo.
echo Starting compilation... This may take 15-30 minutes.
echo.

REM Build and install
pip install -e . -v

echo.
echo ========================================
echo Build completed!
echo ========================================
echo.
echo Verifying installation...
python -c "import mmcv; print('mmcv version:', mmcv.__version__); from mmcv.ops import ModulatedDeformConv2d; print('✓ CUDA extensions loaded successfully!')"

cd ..
pause
