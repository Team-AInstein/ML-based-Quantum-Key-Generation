@echo off
REM Backend Step-by-Step Batch Script for Windows
REM This script helps run all backend components

setlocal enabledelayedexpansion
cd /d "c:\Users\naeem\VS\Python\MAJOR_PROJECT"

echo.
echo ======================================================
echo   QUANTUM KEY DISTRIBUTION - BACKEND RUNNER
echo ======================================================
echo.
echo Select what you want to run:
echo.
echo [FRONTEND]
echo   1) Test Frontend Components
echo   2) Run Frontend Server ^(http://localhost:5000^)
echo.
echo [RL TRAINING]
echo   3) Generate Keys ^(BB84^)
echo   4) Test Environment
echo   5) Run Integration Tests
echo   6) Train DQN Model ^(LONG - 15-30 min^)
echo   7) Evaluate Model
echo.
echo [FULL PIPELINES]
echo   8) Full RL Pipeline ^(all steps in sequence^)
echo   9) System Check + All Tests
echo.
echo [OTHER]
echo   0) Exit
echo.
set /p choice="Enter your choice (0-9): "

if "%choice%"=="0" (
    echo Exiting...
    exit /b 0
)

if "%choice%"=="1" (
    echo Running: Test Frontend Components
    cd frontend
    python -c "from quantum_encryption import QuantumEncryption; qe = QuantumEncryption(b'test_key_256bits0123456789ABCDEF'); print('✓ Encryption OK')"
    cd ..
    goto end
)

if "%choice%"=="2" (
    echo Running: Frontend Server
    cd frontend
    python server.py
    goto end
)

if "%choice%"=="3" (
    echo Running: Generate Keys
    cd Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL
    python generate_keys.py
    goto end
)

if "%choice%"=="4" (
    echo Running: Test Environment
    cd Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL
    python test_env.py
    goto end
)

if "%choice%"=="5" (
    echo Running: Integration Tests
    cd Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL
    python test_integration.py
    goto end
)

if "%choice%"=="6" (
    echo WARNING: Training takes 15-30 minutes!
    set /p confirm="Continue? (y/n): "
    if /i "%confirm%"=="y" (
        cd Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL
        python train_integrated.py
    )
    goto end
)

if "%choice%"=="7" (
    echo Running: Evaluate Model
    cd Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL
    python evaluate_model.py
    goto end
)

if "%choice%"=="8" (
    echo Running: Full RL Pipeline
    cd Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL
    
    echo.
    echo [STEP 1/5] Generate Keys...
    python generate_keys.py
    if errorlevel 1 goto error
    
    echo.
    echo [STEP 2/5] Test Environment...
    python test_env.py
    if errorlevel 1 goto error
    
    echo.
    echo [STEP 3/5] Run Integration Tests...
    python test_integration.py
    if errorlevel 1 goto error
    
    echo.
    echo [STEP 4/5] Train Model ^(this will take 20+ minutes^)...
    python train_integrated.py
    if errorlevel 1 goto error
    
    echo.
    echo [STEP 5/5] Evaluate Model...
    python evaluate_model.py
    if errorlevel 1 goto error
    
    echo.
    echo ✓ Full pipeline completed successfully!
    goto end
)

if "%choice%"=="9" (
    echo Running: System Check + All Tests
    
    echo.
    echo [CHECK 1/3] Testing Frontend Components...
    cd frontend
    python -c "from quantum_encryption import QuantumEncryption; qe = QuantumEncryption(b'test_key_256bits0123456789ABCDEF'); print('✓ Frontend OK')"
    cd ..
    if errorlevel 1 goto error
    
    echo.
    echo [CHECK 2/3] Testing RL Environment...
    cd Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL
    python test_env.py
    if errorlevel 1 goto error
    
    echo.
    echo [CHECK 3/3] Running Integration Tests...
    python test_integration.py
    if errorlevel 1 goto error
    
    echo.
    echo ✓ All system checks passed!
    goto end
)

echo Invalid choice!

:error
echo.
echo ✗ An error occurred!
goto end

:end
echo.
pause
