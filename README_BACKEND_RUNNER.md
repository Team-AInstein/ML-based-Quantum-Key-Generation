# Quick Start: Run Backend Step-by-Step

## 🚀 Start Here

### Option 1: Interactive Menu (Easiest)
```bash
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT
python run_backend_stepwise.py
```
Then select from the menu (1-9)

### Option 2: Windows Batch Script
```bash
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT
run_backend.bat
```
Then select from the menu (1-9)

### Option 3: Manual Step-by-Step

#### **Frontend Only** (5 min)
```bash
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT\frontend
python server.py
# Open browser: http://localhost:5000
```

#### **RL Only** (5 min quick test)
```bash
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT\Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL

# Step 1: Generate keys
python generate_keys.py

# Step 2: Test environment
python test_env.py

# Step 3: Run integration tests
python test_integration.py
```

#### **RL Full Training** (25-35 min including all steps)
```bash
cd c:\Users\naeem\VS\Python\MAJOR_PROJECT\Final\Zeenats_Debug\ML-based-QKD-using-DeepQN\RL

# Step 1: Generate keys
python generate_keys.py

# Step 2: Test environment
python test_env.py

# Step 3: Run integration tests
python test_integration.py

# Step 4: Train model (⏱️ 15-30 minutes!)
python train_integrated.py

# Step 5: Evaluate model
python evaluate_model.py
```

---

## 📁 What Each Component Does

### **Frontend (Web Chat)**
- **File:** `frontend/server.py`
- **Time:** 2 min
- **Does:** Quantum secure chat application
- **Output:** Web UI at http://localhost:5000
- **Test:** Open 2 browser tabs, chat between them

### **RL Step 1: Generate Keys**
- **File:** `RL/generate_keys.py`
- **Time:** 5 sec
- **Does:** Creates BB84 quantum keys with Eve simulation
- **Output:** Keys saved, shows QBER
- **Command:** `python generate_keys.py`

### **RL Step 2: Test Environment**
- **File:** `RL/test_env.py`
- **Time:** 10 sec
- **Does:** Verifies RL environment works
- **Output:** 5 sample episodes with metrics
- **Command:** `python test_env.py`

### **RL Step 3: Integration Tests**
- **File:** `RL/test_integration.py`
- **Time:** 30 sec
- **Does:** Tests BB84 + DQN together
- **Output:** 3 episodes showing integrated operation
- **Command:** `python test_integration.py`

### **RL Step 4: Train Model**
- **File:** `RL/train_integrated.py`
- **Time:** ⏱️ 15-30 minutes
- **Does:** Trains DQN agent on QKD task
- **Output:** Trained model saved, training logs
- **Command:** `python train_integrated.py`

### **RL Step 5: Evaluate Model**
- **File:** `RL/evaluate_model.py`
- **Time:** 10 sec
- **Does:** Tests trained model performance
- **Output:** Metrics and performance comparison
- **Command:** `python evaluate_model.py`

---

## 🎯 Recommended Sequences

### **First Time (5 min)**
```bash
python run_backend_stepwise.py
# Select: 9 (Full System Check)
```
This tests everything without long training.

### **Daily Development (10 min)**
```bash
# Terminal 1: Frontend
cd frontend && python server.py

# Terminal 2: Quick RL test
cd RL && python generate_keys.py && python test_integration.py
```

### **Before Deployment (30 min)**
```bash
python run_backend_stepwise.py
# Select: 8 (Full RL Pipeline)
```
This runs complete training.

---

## 📊 Expected Output Examples

### Generate Keys
```
✓ Generated 256-qubit BB84 key
✓ QBER: 0.0125 (1.25%)
✓ Final key after privacy amplification: 248 bits
```

### Test Environment
```
Episode 1: reward=156.43, qber=0.015, key_size=240
Episode 2: reward=162.18, qber=0.012, key_size=248
Episode 3: reward=159.87, qber=0.018, key_size=236
```

### Train Model
```
Episode 1/10: avg_reward=156.43
Episode 2/10: avg_reward=162.18
...
✓ Training complete. Model saved.
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | `pip install -r frontend/requirements.txt` |
| "Port 5000 in use" | Change port in `server.py` or kill other process |
| "Training too slow" | Reduce episodes or key_length in script |
| "QBER always 0" | Run `python test_channel_noise.py` to diagnose |

---

## 📖 For More Details

- **BACKEND_EXECUTION_GUIDE.md** - Detailed step-by-step guide
- **BACKEND_ARCHITECTURE.md** - System architecture and data flows
- **frontend/README.md** - Frontend documentation
- **RL/README_INTEGRATED.md** - RL system documentation

---

## ✅ You Now Have 3 Ways to Run Everything:

1. **`python run_backend_stepwise.py`** ← Interactive menu (easiest)
2. **`run_backend.bat`** ← Windows batch (also easy)
3. **Manual commands** ← Direct control

**Pick one and start!** 🚀
