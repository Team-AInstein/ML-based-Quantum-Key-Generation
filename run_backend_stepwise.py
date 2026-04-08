#!/usr/bin/env python3
"""
Backend Step-by-Step Runner
========================================
Runs all backend components in the correct order with detailed output.
This script helps debug and verify each component of the system.

Usage:
    python run_backend_stepwise.py [mode]
    
Modes:
    1 = Run frontend server only
    2 = Run RL training pipeline only
    3 = Run full backend (frontend + RL)
    4 = Run individual components (manual selection)
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}{Colors.END}\n")

def print_step(step_num, text):
    """Print a step number."""
    print(f"{Colors.CYAN}[STEP {step_num}] {Colors.BOLD}{text}{Colors.END}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def get_project_paths():
    """Get all important project paths."""
    base = Path("c:/Users/naeem/VS/Python/MAJOR_PROJECT")
    return {
        'base': base,
        'frontend': base / "frontend",
        'rl': base / "Final/Zeenats_Debug/ML-based-QKD-using-DeepQN/RL",
        'virtualenv': base / "virtualenv",
    }

def check_dependencies():
    """Check if all required packages are installed."""
    print_step(1, "Checking Dependencies")
    
    required_packages = {
        'flask': 'Flask (web framework)',
        'flask_socketio': 'Flask-SocketIO (real-time communication)',
        'qiskit': 'Qiskit (quantum computing)',
        'numpy': 'NumPy (numerical computing)',
        'torch': 'PyTorch (deep learning)',
    }
    
    missing = []
    for package, description in required_packages.items():
        try:
            __import__(package)
            print_success(f"{description} is installed")
        except ImportError:
            print_warning(f"{description} is NOT installed")
            missing.append(package)
    
    if missing:
        print_error(f"Missing packages: {', '.join(missing)}")
        print_info("Install with: pip install -r requirements.txt")
        return False
    
    print_success("All dependencies are installed!")
    return True

def verify_files():
    """Verify that all required files exist."""
    print_step(2, "Verifying Required Files")
    
    paths = get_project_paths()
    required_files = {
        'Frontend Server': paths['frontend'] / "server.py",
        'Frontend Key Manager': paths['frontend'] / "quantum_key_manager.py",
        'Frontend Encryption': paths['frontend'] / "quantum_encryption.py",
        'RL BB84 Wrapper': paths['rl'] / "bb84_wrapper.py",
        'RL QKD Environment': paths['rl'] / "integrated_qkd_env.py",
        'RL DQN Agent': paths['rl'] / "dqn_agent.py",
        'RL Generator': paths['rl'] / "generate_keys.py",
        'RL Trainer': paths['rl'] / "train_integrated.py",
        'RL Evaluator': paths['rl'] / "evaluate_model.py",
    }
    
    missing = []
    for name, filepath in required_files.items():
        if filepath.exists():
            print_success(f"{name}: {filepath.name}")
        else:
            print_error(f"{name}: NOT FOUND at {filepath}")
            missing.append(name)
    
    if missing:
        print_error(f"Missing {len(missing)} required files!")
        return False
    
    print_success("All required files exist!")
    return True

def run_frontend_server():
    """Run the frontend Flask server."""
    print_header("STARTING FRONTEND SERVER")
    paths = get_project_paths()
    
    print_info("The server will start on http://localhost:5000")
    print_info("Open your browser and navigate to that address")
    print_info("Press Ctrl+C to stop the server")
    
    os.chdir(str(paths['frontend']))
    try:
        subprocess.run([sys.executable, "server.py"])
    except KeyboardInterrupt:
        print_warning("\nServer stopped by user")

def test_frontend_components():
    """Test individual frontend components."""
    print_header("TESTING FRONTEND COMPONENTS")
    paths = get_project_paths()
    os.chdir(str(paths['frontend']))
    
    print_step(1, "Testing Quantum Encryption Module")
    try:
        from quantum_encryption import QuantumEncryption
        qe = QuantumEncryption(b"test_key_256bits0123456789ABCDEF")
        encrypted = qe.encrypt("Hello, World!")
        print_success(f"Encryption works! Encrypted: {encrypted[:50]}...")
    except Exception as e:
        print_error(f"Encryption test failed: {e}")
        return False
    
    print_step(2, "Testing Quantum Key Manager Module")
    try:
        from quantum_key_manager import QuantumKeyManager
        print_success("Quantum Key Manager imported successfully")
    except Exception as e:
        print_error(f"Key Manager test failed: {e}")
        return False
    
    print_success("Frontend components are working!")
    return True

def run_rl_generate_keys():
    """Run the RL key generation script."""
    print_header("RUNNING: RL KEY GENERATION")
    paths = get_project_paths()
    os.chdir(str(paths['rl']))
    
    print_info("This will generate quantum keys using BB84 protocol...")
    try:
        subprocess.run([sys.executable, "generate_keys.py"], check=True)
        print_success("Key generation completed!")
        return True
    except subprocess.CalledProcessError:
        print_error("Key generation failed!")
        return False
    except KeyboardInterrupt:
        print_warning("Key generation interrupted by user")
        return False

def run_rl_test_env():
    """Test the RL environment."""
    print_header("TESTING: RL ENVIRONMENT")
    paths = get_project_paths()
    os.chdir(str(paths['rl']))
    
    print_info("Testing integrated QKD environment...")
    try:
        subprocess.run([sys.executable, "test_env.py"], check=True)
        print_success("Environment test completed!")
        return True
    except subprocess.CalledProcessError:
        print_error("Environment test failed!")
        return False
    except KeyboardInterrupt:
        print_warning("Environment test interrupted by user")
        return False

def run_rl_test_integration():
    """Run integration tests."""
    print_header("RUNNING: INTEGRATION TESTS")
    paths = get_project_paths()
    os.chdir(str(paths['rl']))
    
    print_info("Running quick integration tests...")
    try:
        subprocess.run([sys.executable, "test_integration.py"], check=True)
        print_success("Integration tests completed!")
        return True
    except subprocess.CalledProcessError:
        print_error("Integration tests failed!")
        return False
    except KeyboardInterrupt:
        print_warning("Integration tests interrupted by user")
        return False

def run_rl_training():
    """Run the RL training pipeline."""
    print_header("RUNNING: RL TRAINING")
    paths = get_project_paths()
    os.chdir(str(paths['rl']))
    
    print_info("This will train the DQN agent (may take 10-30 minutes)...")
    print_info("Output will be saved to training_logs/")
    try:
        subprocess.run([sys.executable, "train_integrated.py"], check=True)
        print_success("Training completed!")
        return True
    except subprocess.CalledProcessError:
        print_error("Training failed!")
        return False
    except KeyboardInterrupt:
        print_warning("Training interrupted by user")
        return False

def run_rl_evaluation():
    """Run model evaluation."""
    print_header("RUNNING: MODEL EVALUATION")
    paths = get_project_paths()
    os.chdir(str(paths['rl']))
    
    print_info("Evaluating trained model...")
    try:
        subprocess.run([sys.executable, "evaluate_model.py"], check=True)
        print_success("Evaluation completed!")
        return True
    except subprocess.CalledProcessError:
        print_error("Evaluation failed!")
        return False
    except KeyboardInterrupt:
        print_warning("Evaluation interrupted by user")
        return False

def show_menu():
    """Show the main menu."""
    print_header("BACKEND STEP-BY-STEP RUNNER")
    print("Select what you want to run:\n")
    print(f"{Colors.BOLD}Frontend (Web Server):{Colors.END}")
    print("  1) Test Frontend Components")
    print("  2) Run Frontend Server (http://localhost:5000)\n")
    
    print(f"{Colors.BOLD}RL Training Pipeline:{Colors.END}")
    print("  3) Generate Keys (BB84)")
    print("  4) Test Environment")
    print("  5) Run Integration Tests")
    print("  6) Train DQN Model (LONG - 15-30 min)")
    print("  7) Evaluate Model\n")
    
    print(f"{Colors.BOLD}Full Pipelines:{Colors.END}")
    print("  8) Full RL Pipeline (generate → test → integrate → train → evaluate)")
    print("  9) Check System & Run All Tests\n")
    
    print(f"{Colors.BOLD}Other:{Colors.END}")
    print("  0) Exit\n")

def main():
    """Main entry point."""
    print_header("QUANTUM KEY DISTRIBUTION BACKEND")
    print_info("Python Version: " + sys.version.split()[0])
    print_info(f"Working Directory: {os.getcwd()}\n")
    
    # Initial checks
    if not check_dependencies():
        print_error("Cannot proceed without required dependencies!")
        return
    
    if not verify_files():
        print_error("Cannot proceed without required files!")
        return
    
    print_success("\nSystem check passed! All components are ready.\n")
    time.sleep(1)
    
    # Main loop
    while True:
        show_menu()
        choice = input(f"{Colors.BOLD}Enter your choice (0-9): {Colors.END}").strip()
        
        if choice == "0":
            print_success("Exiting backend runner. Goodbye!")
            break
        
        elif choice == "1":
            test_frontend_components()
        
        elif choice == "2":
            run_frontend_server()
        
        elif choice == "3":
            run_rl_generate_keys()
        
        elif choice == "4":
            run_rl_test_env()
        
        elif choice == "5":
            run_rl_test_integration()
        
        elif choice == "6":
            print_warning("This will take 15-30 minutes. Continue? (y/n)")
            if input().lower() == 'y':
                run_rl_training()
        
        elif choice == "7":
            run_rl_evaluation()
        
        elif choice == "8":
            print_header("FULL RL PIPELINE")
            print_info("Running: Generate → Test → Integrate → Train → Evaluate\n")
            
            if run_rl_generate_keys():
                time.sleep(2)
                if run_rl_test_env():
                    time.sleep(2)
                    if run_rl_test_integration():
                        time.sleep(2)
                        if run_rl_training():
                            time.sleep(2)
                            run_rl_evaluation()
            
            print_success("Full pipeline completed!")
        
        elif choice == "9":
            print_header("FULL SYSTEM CHECK")
            print_success("Dependencies checked")
            print_success("Files verified")
            
            if test_frontend_components():
                time.sleep(2)
                if run_rl_test_env():
                    time.sleep(2)
                    if run_rl_test_integration():
                        print_success("All tests passed!")
        
        else:
            print_error("Invalid choice. Please enter 0-9.")
        
        print("\n" + "="*60)
        input(f"{Colors.BOLD}Press Enter to continue...{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Program interrupted by user.{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
