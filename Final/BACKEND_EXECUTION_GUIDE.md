# Backend Step-by-Step Execution Guide

## Quick Start

### Option 1: Interactive Menu (Recommended)
```bash
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT
python run_backend_stepwise.py
```
This opens an interactive menu where you can select what to run.

### Option 2: Direct Execution
Navigate to specific folder and run individual scripts directly.

---

## Backend Components Overview

### 1. FRONTEND (Flask Web Server)
**Location:** `c:\Users\naeem\VS\Python\MAJOR_PROJECT\frontend\`

**Purpose:** Web-based quantum secure chat application

**Files:**
- `server.py` - Main Flask server
- `quantum_key_manager.py` - BB84 key generation per room
- `quantum_encryption.py` - XOR encryption with quantum keys
- `templates/index.html` - Web UI
- `client.py` - CLI terminal client

**How to run:**
```bash
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT\frontend
python server.py
```
Then open browser to: `http://localhost:5000`

**What it does:**
- Generates quantum keys for each chat room
- Encrypts/decrypts messages using quantum keys
- Shows messages in both plaintext and encrypted form
- Supports multiple users in same room

---

### 2. RL TRAINING PIPELINE (Deep Q-Network)
**Location:** `c:\Users\naeem\VS\Python\MAJOR_PROJECT\Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL\`

**Purpose:** Trains AI agent to optimize quantum key distribution

**Core Components:**

#### Step 1: Key Generation
**File:** `generate_keys.py`
```bash
cd RL
python generate_keys.py
```
- Generates BB84 quantum keys
- Simulates Eve eavesdropping
- Calculates QBER (Quantum Bit Error Rate)
- Output: Keys saved to files

#### Step 2: Test Environment
**File:** `test_env.py`
```bash
python test_env.py
```
- Tests that the QKD environment works
- Runs 5 sample episodes
- Shows state/action/reward

#### Step 3: Integration Tests
**File:** `test_integration.py`
```bash
python test_integration.py
```
- Tests BB84 + DQN together
- Runs 3 episodes with detailed output
- Verifies all components integrate

#### Step 4: Train Model
**File:** `train_integrated.py`
```bash
python train_integrated.py
```
**⚠️ WARNING: Takes 15-30 minutes!**
- Trains DQN agent to optimize key generation
- 10 episodes with training
- Saves model to `models_test/`
- Output: Training logs in `training_logs/`

#### Step 5: Evaluate Model
**File:** `evaluate_model.py`
```bash
python evaluate_model.py
```
- Tests the trained model on new data
- 10 evaluation episodes
- Compares trained vs untrained performance
- Shows QBER, key size, rewards

---

## STEP-BY-STEP MANUAL EXECUTION

### Frontend Only
```bash
# Step 1: Go to frontend
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT\frontend

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run server
python server.py

# Step 4: Open browser
# Go to http://localhost:5000

# Step 5: Test with multiple users
# Open 2 browser tabs
# Tab 1: Click "Join as Alice"
# Tab 2: Click "Join as Bob"
# Send messages between them!
```

### RL Training Pipeline Only
```bash
# Step 1: Go to RL folder
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT\Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL

# Step 2: Generate keys
echo "=== Generating Keys ==="
python generate_keys.py
echo "✓ Keys generated"

# Step 3: Test environment
echo "=== Testing Environment ==="
python test_env.py
echo "✓ Environment works"

# Step 4: Run integration tests
echo "=== Running Integration Tests ==="
python test_integration.py
echo "✓ Integration tests passed"

# Step 5: Train the model (TAKES 20+ MINUTES)
echo "=== Training DQN Agent ==="
python train_integrated.py
echo "✓ Training complete"

# Step 6: Evaluate the model
echo "=== Evaluating Model ==="
python evaluate_model.py
echo "✓ Evaluation complete"
```

### Full Backend (Frontend + RL)
```bash
# Terminal 1: Start Frontend Server
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT\frontend
python server.py

# Terminal 2: Run RL Pipeline
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT\Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL
python generate_keys.py
python test_env.py
python test_integration.py
python train_integrated.py
python evaluate_model.py
```

---

## Key Modules Explained

### BB84 Wrapper (`bb84_wrapper.py`)
Implements the BB84 quantum key distribution protocol.

```python
from bb84_wrapper import BB84Wrapper

# Create BB84 instance
bb84 = BB84Wrapper(
    key_length=256,           # Number of qubits
    eve_present=True,         # Is Eve eavesdropping?
    eve_intercept_ratio=0.5,  # Eve intercepts 50% of transmissions
    channel_error_rate=0.01   # 1% natural channel noise
)

# Run the protocol
result = bb84.run_protocol()
print(f"QBER: {result['qber']}")
print(f"Eve likelihood: {result['eve_likelihood']}")
```

### Integrated QKD Environment (`integrated_qkd_env.py`)
RL environment that wraps BB84 for agent training.

```python
from integrated_qkd_env import IntegratedQKDEnv

# Create environment
env = IntegratedQKDEnv(key_length=256, max_steps=20)

# Step through episodes
state, info = env.reset()
for step in range(20):
    action = env.action_space.sample()  # Random action
    state, reward, done, truncated, info = env.step(action)
    print(f"Step {step}: QBER={info['qber']:.4f}, Key={info['key_size']}")
    if done:
        break
```

### DQN Agent (`dqn_agent.py`)
Deep Q-Network for learning optimal strategies.

```python
from dqn_agent import DQNAgent

# Create agent
agent = DQNAgent(
    state_size=3,      # [QBER, Eve_likelihood, Key_ratio]
    action_size=5,     # 5 possible actions
    learning_rate=0.001,
    gamma=0.99         # Discount factor
)

# Train on environment
agent.remember(state, action, reward, next_state, done)
loss = agent.replay(batch_size=32)
```

---

## Expected Outputs

### Frontend Server
```
* Running on http://0.0.0.0:5000
Press CTRL+C to quit
* Debugger is active!
* Debugger PIN: 123-456-789
```

### Generate Keys
```
✓ Generated 256-qubit BB84 key
✓ QBER: 0.0125 (1.25% - indicates Eve likely present)
✓ Final key after privacy amplification: 248 bits
```

### Training
```
Episode 1/10: reward=156.43, avg_qber=0.015, key_size=240
Episode 2/10: reward=162.18, avg_qber=0.012, key_size=248
...
✓ Training complete. Model saved to models_test/dqn_model.pt
```

### Evaluation
```
Episode 1: QBER=0.0108, Key=240 bits, Reward=165.3
Episode 2: QBER=0.0142, Key=236 bits, Reward=158.7
...
Average QBER: 0.0125 ± 0.0032
Average Key Size: 242 ± 5 bits
```

---

## Troubleshooting

### Error: "Module not found: qiskit"
**Solution:** Install dependencies
```bash
pip install qiskit numpy torch flask flask-socketio
```

### Error: "Port 5000 already in use"
**Solution:** Either stop the other process or use different port
```bash
# Find what's using port 5000
netstat -ano | findstr :5000

# Then either kill it or use different port
# To use different port, edit server.py line: 
# app.run(port=5001)  # Use 5001 instead
```

### Training too slow
**Solution:** Reduce episodes or key length
- Edit `train_integrated.py`, change `num_episodes=10`
- Edit `integrated_qkd_env.py`, change `key_length=64`

### QBER always showing 0
**Solution:** This is being investigated. Run test:
```bash
python test_channel_noise.py
```

---

## File Sizes & Time Estimates

| Component | Time | Size |
|-----------|------|------|
| Generate Keys | 5 sec | ~100 KB |
| Test Environment | 10 sec | - |
| Integration Tests | 30 sec | - |
| Train Model | 20-30 min | ~50 MB |
| Evaluate Model | 10 sec | - |
| Full Frontend Setup | 2 min | - |
| **Total (Full Pipeline)** | ~25-35 min | ~50 MB |

---

## Recommended Execution Order

1. **First Time Only:**
   ```bash
   # Check everything works
   python run_backend_stepwise.py
   # Select option 9 (Full System Check)
   ```

2. **Daily Development:**
   ```bash
   # Terminal 1: Frontend
   cd frontend && python server.py
   
   # Terminal 2: Quick tests
   cd RL
   python generate_keys.py
   python test_integration.py
   ```

3. **Before Deployment:**
   ```bash
   # Run full pipeline
   python run_backend_stepwise.py
   # Select option 8 (Full RL Pipeline)
   ```

---

## Questions?

- **How to debug?** Edit the scripts and add `print()` statements
- **How to modify parameters?** Open the .py files and change variables
- **How to save outputs?** Add logging: `with open('output.txt', 'w') as f: f.write(output)`

**That's it! You now have a complete backend runner system!**
