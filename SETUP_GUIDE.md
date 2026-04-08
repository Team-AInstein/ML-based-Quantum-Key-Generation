# ML-based Quantum Key Distribution (QKD) System - Complete Setup Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Running the System](#running-the-system)
6. [Understanding Epsilon Decay](#understanding-epsilon-decay)
7. [Training the DQN Agent](#training-the-dqn-agent)
8. [Running the Frontend](#running-the-frontend)
9. [Testing and Validation](#testing-and-validation)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

This project implements a **Machine Learning-based Quantum Key Distribution (QKD) system** using Deep Q-Network (DQN) reinforcement learning to optimize BB84 protocol parameters in the presence of quantum noise and eavesdropping attacks.

### Key Features
- **BB84 Protocol Implementation**: Using Qiskit for quantum circuit simulation
- **DQN-based Optimization**: Neural network learns optimal QKD parameters
- **Eavesdropper Detection**: Monitors QBER to detect Eve's presence
- **Privacy Amplification**: Post-processing to ensure information-theoretic security
- **Real-time Frontend**: Flask-based web interface for secure communication

### Research Focus
The project emphasizes the **exploration-exploitation balance** in reinforcement learning, specifically analyzing epsilon decay rates to ensure:
- Fast convergence to high rewards
- Thorough exploration of quantum state space
- Robustness against delayed/subtle eavesdropping attacks
- Avoidance of premature convergence risks

---

## System Architecture

```
project/
├── Final/
│   ├── Zeenats_Debug/ML-based-QKD-using-DeepQN/
│   │   └── RL/                           # Reinforcement Learning Module
│   │       ├── dqn_agent.py              # Deep Q-Network implementation
│   │       ├── integrated_qkd_env.py     # QKD environment for RL
│   │       ├── bb84_wrapper.py           # BB84 protocol wrapper
│   │       ├── train_integrated.py       # Main training script
│   │       ├── decay_experiment.py       # Epsilon decay analysis
│   │       ├── evaluate_model.py         # Model evaluation
│   │       └── privacy_amplification.py  # Security post-processing
│   │
│   └── QKD-protocols/                    # Raw BB84 implementations
│       └── BB84_attack_experiment/
│           ├── simulator_with_eve.py     # Simulation with eavesdropper
│           ├── simulator_without_eve.py  # Clean channel simulation
│           └── bb84.py                   # Core BB84 logic
│
├── frontend/                             # Web Interface
│   ├── server.py                         # Flask server
│   ├── client.py                         # Client connection logic
│   ├── quantum_key_manager.py            # Key management
│   └── quantum_encryption.py             # Encryption/decryption
│
├── run_backend_stepwise.py               # Automated runner script
└── SETUP_GUIDE.md                        # This file
```

---

## Prerequisites

### Required Software
- **Python**: 3.8 or higher (3.10 recommended)
- **pip**: Latest version
- **Virtual Environment**: `venv` or `virtualenv` (recommended)

### Hardware Recommendations
- **RAM**: 8GB minimum, 16GB recommended
- **CPU**: Multi-core processor (for faster training)
- **GPU**: Optional (CUDA-compatible for PyTorch acceleration)

---

## Installation

### Step 1: Clone/Navigate to Repository
```bash
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT.worktrees\copilot-worktree-2026-04-08T16-05-32
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### Step 3: Install Core Dependencies

#### Quantum Computing Framework
```bash
# Qiskit (quantum circuit simulation)
pip install qiskit==0.45.0
pip install qiskit-aer==0.13.0

# Note: Qiskit versions are important for compatibility
```

#### Deep Learning Framework
```bash
# PyTorch (for DQN neural networks)
# CPU version:
pip install torch==2.1.0 torchvision torchaudio

# GPU version (if CUDA available):
pip install torch==2.1.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Scientific Computing
```bash
pip install numpy==1.24.3
pip install matplotlib==3.7.2
```

#### Frontend Dependencies
```bash
cd frontend
pip install -r requirements.txt
cd ..

# Or install manually:
pip install flask==2.3.2
pip install flask-socketio==5.3.4
pip install flask-cors==4.0.0
pip install python-socketio==5.9.0
pip install colorama==0.4.6
```

### Step 4: Verify Installation
```bash
# Test Qiskit
python -c "import qiskit; print(f'Qiskit {qiskit.__version__} installed')"

# Test PyTorch
python -c "import torch; print(f'PyTorch {torch.__version__} installed')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Test other dependencies
python -c "import numpy, matplotlib, flask; print('All dependencies OK')"
```

---

## Running the System

### Option 1: Automated Runner (Recommended)

The `run_backend_stepwise.py` script provides an interactive menu to run different components:

```bash
python run_backend_stepwise.py
```

**Menu Options:**
1. Run frontend server only
2. Run RL training pipeline only
3. Run full backend (frontend + RL)
4. Run individual components (manual selection)

### Option 2: Manual Execution

See sections below for detailed manual execution steps.

---

## Understanding Epsilon Decay

### What is Epsilon Decay?

Epsilon (ε) controls the **exploration-exploitation tradeoff** in reinforcement learning:
- **High ε (1.0)**: Agent explores randomly (100% exploration)
- **Low ε (0.01)**: Agent exploits learned policy (99% exploitation)
- **Decay Rate**: How quickly ε decreases over episodes

### Why It Matters for Quantum Security

In quantum key distribution:
- **Fast decay (0.90)**: Agent converges quickly but may miss rare eavesdropping patterns
- **Slow decay (0.99)**: Agent explores thoroughly but takes too long to converge
- **Optimal "Goldilocks" (0.97)**: Balances speed and thoroughness

### The Premature Convergence Problem

```
Episode 30: ε = 0.90^30 ≈ 0.04  → Exploration stops early
Episode 30: ε = 0.97^30 ≈ 0.40  → Still exploring actively
```

**Real-world impact:**
- Eavesdropper (Eve) might only appear after 100 episodes of stable communication
- If agent stops exploring at episode 30, it may have "locked in" a strategy that:
  - ✅ Handles noise efficiently
  - ❌ Is blind to subtle intrusion patterns

### Current Configuration

**Default value: 0.970**

Location: `Final/Zeenats_Debug/ML-based-QKD-using-DeepQN/RL/dqn_agent.py` (line 58)

**Justification:**
> "While 0.90 offered the fastest convergence, a value of 0.95-0.97 was selected as the optimal balance to ensure sufficient exploration of the quantum state space while still reaching stability within the 200-episode limit. This ensures the agent has thoroughly 'vetted' the environment before committing to a strategy, critical for academic research and production security."

### Running Epsilon Decay Experiments

To analyze different decay rates:

```bash
cd Final/Zeenats_Debug/ML-based-QKD-using-DeepQN/RL

# Run experiment with default values (0.85, 0.90, 0.95, 0.99)
python decay_experiment.py --episodes 200

# Run with custom values
python decay_experiment.py --episodes 200 --decays 0.90 0.95 0.97 0.99

# Specify output directory
python decay_experiment.py --episodes 200 --out my_experiments
```

**Output:**
- `decay_experiment_results.json`: Raw data for all decay rates
- `decay_experiment_plot.png`: Comparison plot with smoothed reward curves
- `summary_decay_X.XXX.json`: Individual summaries for each decay rate

---

## Training the DQN Agent

### Quick Start Training

```bash
cd Final/Zeenats_Debug/ML-based-QKD-using-DeepQN/RL

# Basic training (100 episodes)
python train_integrated.py

# Extended training with custom parameters
python train_integrated.py --episodes 200 --key-length 128
```

### Advanced Training Options

```bash
python run_training.py --live-plot --noise 0.01 --random-noise --epsilon-decay 0.995 --episodes 500 --lr 0.00005

#Slower epsilon decay 
python run_training.py --live-plot --episodes 500 --epsilon-decay 0.995 --epsilon-min 0.001

#Finding best case scenaraio (Goldilock Equation)


```

### Training Parameters Explained

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--episodes` | 100 | Number of training episodes |
| `--key-length` | 128 | Bits per BB84 run |
| `--max-steps` | 20 | Steps per episode |
| `--channel-error` | 0.01 | Quantum channel noise (1%) |
| `--eve-probability` | 0.5 | Chance of eavesdropper (50%) |
| `--epsilon-decay` | 0.970 | Exploration decay rate |
| `--epsilon-min` | 0.01 | Minimum exploration rate |
| `--learning-rate` | 0.0001 | DQN learning rate |
| `--gamma` | 0.99 | Discount factor |
| `--batch-size` | 32 | Replay buffer batch size |

### Understanding Training Output

```
Episode 50/200 | Reward: 432.5 | Loss: 0.045 | Epsilon: 0.235 | QBER: 0.08
```

- **Reward**: Higher is better (target ~430-450)
- **Loss**: DQN training loss (should stabilize)
- **Epsilon**: Current exploration rate (decays to 0.01)
- **QBER**: Quantum Bit Error Rate (lower is better)

### Saved Models

Trained models are saved to: `./models/` (or specified `--model-dir`)

Files:
- `dqn_model_final.pt`: Final trained model
- `training_results.json`: Complete training metrics
- `reward_curve.png`: Episode rewards over time

---

## Running the Frontend

### Start Flask Server

```bash
cd frontend

# Run server on default port (5000)
python server.py

# Run on custom port
python server.py --port 8080
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Quantum Key Manager initialized
 * Ready for client connections
```

### Start Client

In a new terminal:

```bash
cd frontend
python client.py
```

### Using the Web Interface

1. Open browser: `http://127.0.0.1:5000`
2. Enter message in text box
3. Click "Send Secure Message"
4. Server encrypts using quantum-generated keys
5. Decrypted message appears in chat

### Key Generation Flow

1. **BB84 Protocol**: Generate quantum key bits
2. **QBER Check**: Verify channel security
3. **Privacy Amplification**: Extract secure final key
4. **Encryption**: XOR message with key (one-time pad)

---

## Testing and Validation

### Unit Tests

```bash
cd Final/Zeenats_Debug/ML-based-QKD-using-DeepQN/RL

# Test DQN agent
python -m pytest test_rl_controller.py

# Test QKD environment
python test_env.py

# Test BB84 integration
python test_integration.py

# Test QBER calculation
python test_qber_fix.py
```

### Integration Tests

```bash
# Test full pipeline
python test_integration.py

# Test with channel noise
python test_channel_noise.py
```

### Evaluate Trained Model

```bash
python evaluate_model.py --model-path ./models/dqn_model_final.pt --episodes 50
```

**Output:**
- Average reward over evaluation episodes
- QBER statistics
- Key length distribution
- Eavesdropper detection rate

---

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'qiskit'
**Solution:**
```bash
pip install qiskit qiskit-aer
```

#### 2. CUDA out of memory (PyTorch GPU)
**Solution:**
- Reduce `--batch-size` (try 16 or 8)
- Use CPU version: `device = torch.device("cpu")`

#### 3. Flask server already running
**Solution:**
```bash
# Kill existing process (Windows)
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Flask*"

# Kill existing process (Linux/Mac)
pkill -f "python server.py"

# Or use different port
python server.py --port 8080
```

#### 4. Training loss explodes (NaN values)
**Solution:**
- Lower learning rate: `--learning-rate 0.00001`
- Check for infinite rewards in environment
- Verify gradient clipping is enabled

#### 5. QBER always high (>15%)
**Solution:**
- Increase `--key-length` for better statistics
- Reduce `--channel-error`
- Check Eve probability is not 100%

### Debug Mode

Enable verbose logging:

```bash
# Training
python train_integrated.py --episodes 10 --verbose

# Frontend
python server.py --debug
```

---

## Additional Resources

### Key Files Reference

| File | Purpose |
|------|---------|
| `dqn_agent.py` | DQN neural network and training logic |
| `integrated_qkd_env.py` | RL environment for QKD optimization |
| `bb84_wrapper.py` | Quantum circuit implementation (Qiskit) |
| `train_integrated.py` | Main training orchestrator |
| `decay_experiment.py` | Epsilon decay analysis tool |
| `privacy_amplification.py` | Post-processing security |
| `server.py` | Flask web server |
| `quantum_key_manager.py` | Key storage and retrieval |

### Parameter Tuning Guide

**For faster training:**
- Increase epsilon decay: `0.95`
- Reduce episodes: `100`
- Increase learning rate: `0.0005`

**For better security:**
- Decrease epsilon decay: `0.97` or `0.99`
- Increase episodes: `300`
- Lower learning rate: `0.00005`
- Increase key length: `256`

**For development/debugging:**
- Few episodes: `10-20`
- Short key length: `32`
- High learning rate: `0.001`
- Disable live plots

---

## Quick Reference Commands

### Complete Workflow

```bash
# 1. Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Train DQN agent
cd Final/Zeenats_Debug/ML-based-QKD-using-DeepQN/RL
python train_integrated.py --episodes 200

# 3. Evaluate model
python evaluate_model.py --model-path ./models/dqn_model_final.pt

# 4. Run decay experiments (optional)
python decay_experiment.py --episodes 200 --decays 0.90 0.95 0.97 0.99

# 5. Start frontend server
cd ../../../../../frontend
python server.py

# 6. Start client (new terminal)
python client.py
```

### One-Line Setup (After Dependencies Installed)

```bash
python run_backend_stepwise.py
```

---

## Project Status & Notes

### Epsilon Decay Update (Latest Changes)

**Date**: Current session  
**Change**: Updated default epsilon_decay from `0.995` to `0.970`  
**Reason**: Based on guide feedback emphasizing:
- Speed is not the only factor in security contexts
- Premature convergence risks missing subtle eavesdropping patterns
- Academic research prefers thorough exploration over fast convergence
- Balance between 200-episode convergence and quantum state space coverage

**Updated files:**
- `dqn_agent.py`: Default parameter changed to 0.970
- `train_integrated.py`: Added detailed comments on decay choice
- `decay_experiment.py`: Comprehensive documentation on decay implications

---

## Contact & Support

For questions about:
- **RL Implementation**: Check `dqn_agent.py` docstrings
- **BB84 Protocol**: See `bb84_wrapper.py` and QKD-protocols/ directory
- **Frontend Issues**: Review `server.py` and Flask logs
- **Training Problems**: Run with `--verbose` flag

---

**Last Updated**: Current session  
**Version**: 1.0  
**Python Version**: 3.8+  
**License**: Research/Academic Use

