@echo off
echo ========================================
echo Compiling mmcv-full with CUDA support
echo ========================================

REM Activate Visual Studio 2022 Build Tools environment
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64

REM Activate conda environment
call conda activate basicvsrpp-demo

REM Set environment variables for mmcv compilation
set MMCV_WITH_OPS=1
set FORCE_CUDA=1

REM Uninstall existing mmcv
pip uninstall -y mmcv mmcv-full

REM Install mmcv-full from source
echo.
echo Starting compilation... This may take 10-20 minutes.
echo.
pip install "mmcv-full==1.6.0" --no-binary mmcv-full -v

echo.
echo ========================================
echo Compilation completed!
echo ========================================
echo.
echo Verifying installation...
python -c "import mmcv; print('mmcv version:', mmcv.__version__); from mmcv.ops import ModulatedDeformConv2d; print('CUDA extensions loaded successfully!')"

pause
