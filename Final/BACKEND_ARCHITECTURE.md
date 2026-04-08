# Backend Architecture & Execution Reference

## System Architecture

```
┌───────────────────────────────────────────---───────────────┐
│                 QUANTUM SECURITY LAYER    │                 │
│  ┌──────────────────────┐   ┌────────────▼──────────────┐   │
│  │ Quantum Key Manager  │───│ Quantum Encryption Module │   │
│  │ (bb84_wrapper.py)    │   │ (quantum_encryption.py)   │   │
│  └──────────────────────┘   └────────────┬──────────────┘   │
│       (BB84 Protocol)                     │                 │
│       - Generate Keys                     │ XOR Encryption  │
│       - Simulate Eve                      │                 │
│       - Calculate QBER                    │                 │
└───────────────────────────────────────────┼─────────────────┘
                                            │
┌───────────────────────────────────────────┼─────────────────┐
│            MACHINE LEARNING LAYER (Optional)                │
│  ┌────────────────────────────────────────▼─────────────┐   │
│  │      Integrated QKD Environment (integrated_...env)  │   │
│  │  ┌─────────────────────────────────────────────┐     │   │
│  │  │  Observation: [QBER, Eve Likelihood, Ratio] │     │   │
│  │  │  Action: [0-4] Optimize parameters          │     │   │
│  │  │    0 = Maintain current protocol parameters │     │   │
│  │  │    1 = Increase error correction strength    │     │   │
│  │  │    2 = Decrease error correction strength    │     │   │
│  │  │    3 = Reduce key length (abort early)      │     │   │
│  │  │    4 = Apply privacy amplification           │     │   │
│  │  │  Reward: Key bits generated - penalties     │     │   │
│  │  └─────────────────────────────────────────────┘     │   │  
│  │              ▲                 │                     │   │
│  │              │                 ▼                     │   │
│  │     ┌────────────────┐  ┌─────────────┐              │   │
│  │     │  DQN Agent     │  │  BB84 Exec  │              │   │
│  │     │ (dqn_agent.py) │  │             │              │   │
│  │     └────────────────┘  └─────────────┘              │   │
│  └──────────────────────────────────────────────────────┘   │
│       (Trains agent to optimize QKD parameters)             │
└─────────────────────────────────────────────────────────────┘
```

## Component Interaction Flow

### Frontend (Web Chat)
```
User Input
    │
    ▼
┌─────────────────────┐
│ Generate Quantum Key│  (Per room, ~2-5 sec)
│ BB84Wrapper → Key   │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Encrypt Message    │  (XOR with quantum key)
│ Plaintext + Key     │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Send via Socket.IO │  (WebSocket to server)
│ Encrypted + Metadata│
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Receive & Decrypt  │  (Reverse XOR)
│ Encrypted → Plaintext
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Display to User    │  (Plaintext + Encrypted)
│ Both formats shown  │
└─────────────────────┘
```

### RL Training (ML Optimization)
```
┌──────────────────────┐
│ Generate Initial Keys│ (256-4096 qubit BB84)
│ (generate_keys.py)   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Test Environment Works           │
│ (test_env.py)                    │
│ - Create IntegratedQKDEnv        │
│ - Run 5 sample episodes          │
│ - Verify output format           │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Run Integration Tests            │
│ (test_integration.py)            │
│ - Test BB84 + DQN together      │
│ - Run 3 episodes                │
│ - Check component interaction   │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Training Loop (20-30 min)        │
│ (train_integrated.py)            │
│ For each episode:                │
│  1. Reset env (new BB84 run)     │
│  2. Select action (DQN)          │
│  3. Execute action               │
│  4. Collect reward               │
│  5. Update DQN model             │
│ Save trained model               │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Evaluate Trained Model           │
│ (evaluate_model.py)              │
│ - Load trained model             │
│ - Test on new episodes           │
│ - Compare performance            │
│ - Display metrics (QBER, etc)    │
└──────────────────────────────────┘
```

## Module Dependencies

```
run_backend_stepwise.py
    │
    ├─→ frontend/
    │   ├─ server.py
    │   │  ├─ flask, socket.io
    │   │  ├─ quantum_key_manager.py
    │   │  │  ├─ bb84_wrapper.py (RL module)
    │   │  │  │  ├─ qiskit (used only for random bit generation)
    │   │  │  │  └─ numpy, random
    │   │  │  └─ privacy_amplification.py (RL module)
    │   │  └─ quantum_encryption.py
    │   │     └─ numpy
    │   └─ templates/index.html
    │
    └─→ RL/
        ├─ generate_keys.py
        │  └─ bb84_wrapper.py
        │
        ├─ test_env.py
        │  └─ integrated_qkd_env.py
        │     ├─ bb84_wrapper.py
        │     ├─ privacy_amplification.py
        │     └─ gym
        │
        ├─ test_integration.py
        │  └─ (trainer, env)
        │
        ├─ train_integrated.py
        │  ├─ dqn_agent.py (torch)
        │  ├─ integrated_qkd_env.py
        │  └─ privacy_amplification.py
        │
        └─ evaluate_model.py
           └─ (trained model, env)
```

## Step-by-Step Execution Paths

### Path 1: Just Test Frontend
**Time:** 2 minutes
**Steps:**
1. Navigate to frontend folder
2. Run server.py
3. Open browser to http://localhost:5000
4. Create chat room and send messages

**Command:**
```bash
cd frontend && python server.py
```

---

### Path 2: Just Test RL (No Training)
**Time:** 5 minutes
**Steps:**
1. Generate keys
2. Test environment
3. Run integration tests

**Command:**
```bash
cd RL
python generate_keys.py
python test_env.py
python test_integration.py
```

---

### Path 3: Full RL Pipeline (With Training)
**Time:** 25-35 minutes
**Steps:**
1. Generate keys
2. Test environment  
3. Integration tests
4. Train model (15-30 min) ⏱️
5. Evaluate model

**Command:**
```bash
cd RL
python generate_keys.py
python test_env.py
python test_integration.py
python train_integrated.py
python evaluate_model.py
```

---

### Path 4: Full System (Frontend + RL)
**Time:** 30-40 minutes
**Terminal 1:**
```bash
cd frontend
python server.py
```

**Terminal 2:**
```bash
cd RL
python generate_keys.py && python test_env.py && python test_integration.py && python train_integrated.py && python evaluate_model.py
```

---

## Data Flow Examples

### Example 1: Frontend Chat Message

```
User (Alice) in Browser:
  Clicks "Send" with message "Hello Bob!"
    │
    ▼
JavaScript Frontend:
  Gets quantum key from server cache (or generates)
    │ Key: [10110101...] 256 bits
    ▼
Encrypt:
  XOR("Hello Bob!" × repeated) ⊕ Key
    │ Result: [01010011101...] encrypted
    ▼
Send via WebSocket:
  emit('message', {
    text: "Hello Bob!",
    encrypted: "0x1a2b3c...",
    room: "room_1",
    sender: "alice"
  })
    │
    ▼
Server (Flask):
  Receives message
  Verifies it matches encrypted form
  Broadcasts to all in room
    │ With plaintext AND encrypted
    ▼
All Users in Room:
  Receive message
  See: "Alice: Hello Bob! [encrypted: 0x1a2b...]"
```

### Example 2: RL Training Episode

```
Episode 1:
  ▼
env.reset():
  - Create new BB84Wrapper
  - Generate 256-qubit key
  - Simulate Eve (50% intercept)
  - Calculate QBER ≈ 1-2%
  - Return state = [0.015, 0.60, 0.85]
    │ [QBER, Eve_likelihood, Sifted_ratio]
    ▼
agent.act(state):
  - Feed through neural network
  - Output action Q-values
  - Select action (e.g., "increase_correction")
    ▼
env.step(action):
  - Apply action (modify BB84 parameters)
  - Run new BB84 protocol
  - Calculate new QBER
  - Calculate reward = 240 bits - penalties
    ▼
agent.remember():
  - Store (state, action, reward, next_state, done)
    ▼
agent.replay():
  - Sample batch from memory
  - Train neural network
  - Update Q-values
    ▼
repeat for max_steps
    ▼
Episode Done:
  - Calculate total reward: 4560 points
  - Save model checkpoint
    ▼
Episode 2, 3, ... (repeat 10 times)
    ▼
Training Complete:
  - Save final trained model
  - Compare: Trained vs Untrained
```

---

## Performance Benchmarks

### Frontend Operations
| Operation | Time | Notes |
|-----------|------|-------|
| Start server | ~2 sec | Flask startup |
| Generate key (first) | 2-5 sec | BB84 protocol |
| Generate key (cached) | <1 sec | Reuse existing |
| Encrypt message | <1 ms | XOR operation |
| Load web UI | <1 sec | HTTP request |
| Send message | <100 ms | WebSocket round-trip |

### RL Operations
| Operation | Time | Notes |
|-----------|------|-------|
| Generate keys | 5 sec | 1 BB84 run |
| Test environment | 10 sec | 5 episodes |
| Integration tests | 30 sec | 3 episodes |
| Train model | 20-30 min | 10 episodes, CPU-only |
| Evaluate model | 10 sec | 10 episodes |

---

## File Structure Reference

```
MAJOR_PROJECT/
├── run_backend_stepwise.py      ← INTERACTIVE MENU (START HERE)
├── run_backend.bat              ← Windows batch script
├── BACKEND_EXECUTION_GUIDE.md   ← Detailed guide
├── ARCHITECTURE.md              ← (in frontend)
│
├── frontend/
│   ├── server.py                ← Flask server (run this)
│   ├── quantum_key_manager.py   ← Key generation
│   ├── quantum_encryption.py    ← Encryption/decryption
│   ├── client.py                ← CLI test client
│   ├── requirements.txt          ← Frontend dependencies
│   ├── templates/
│   │   └── index.html           ← Web UI
│   └── quantum_keys/            ← Generated keys storage
│
├── Final/Zeenats_Debug/ML-based-QKD-using-DeepQN/RL/
│   ├── generate_keys.py         ← Step 1: Generate keys
│   ├── test_env.py              ← Step 2: Test environment
│   ├── test_integration.py       ← Step 3: Integration tests
│   ├── train_integrated.py       ← Step 4: Train model
│   ├── evaluate_model.py        ← Step 5: Evaluate
│   ├── test_channel_noise.py     ← Diagnostic test
│   ├── bb84_wrapper.py           ← BB84 implementation
│   ├── integrated_qkd_env.py     ← RL environment
│   ├── dqn_agent.py              ← DQN agent
│   ├── privacy_amplification.py  ← Key compression
│   ├── models_test/              ← Trained models
│   ├── training_logs/            ← Training output
│   └── README_INTEGRATED.md      ← RL documentation
│
└── virtualenv/                  ← Python virtual environment
```

---

## Quick Command Reference

### Run Interactive Menu
```bash
python run_backend_stepwise.py
```

### Run Individual Components
```bash
# Frontend
cd frontend && python server.py

# RL: Generate keys
cd RL && python generate_keys.py

# RL: Test environment
cd RL && python test_env.py

# RL: Integration tests
cd RL && python test_integration.py

# RL: Train model
cd RL && python train_integrated.py

# RL: Evaluate model
cd RL && python evaluate_model.py
```

### Run Full Sequence
```bash
# Generate → Test → Integrate → Train → Evaluate
cd RL && python generate_keys.py && python test_env.py && python test_integration.py && python train_integrated.py && python evaluate_model.py
```

---

## Debugging Tips

### 1. Check Python Environment
```bash
python --version
pip list | grep qiskit
pip list | grep torch
pip list | grep flask
```

### 2. Test Imports
```bash
python -c "import qiskit; print('Qiskit OK')"
python -c "import torch; print('PyTorch OK')"
python -c "import flask; print('Flask OK')"
```

### 3. Check Port Availability
```bash
netstat -ano | findstr :5000
```

### 4. Run Individual Tests
```bash
# Test BB84
python -c "from bb84_wrapper import BB84Wrapper; b = BB84Wrapper(); print(b.run_protocol())"

# Test DQN
python -c "from dqn_agent import DQNAgent; a = DQNAgent(3, 5); print('DQN OK')"

# Test Environment
python test_env.py
```

### 5. Add Debug Output
Edit any .py file and add print statements:
```python
print("[DEBUG] Starting BB84 protocol...")
print(f"[DEBUG] Generated key: {key}")
print(f"[DEBUG] QBER: {qber}")
```

---

## That's your complete backend execution system! 🚀

**Next Step:** Run `python run_backend_stepwise.py` to get started!
