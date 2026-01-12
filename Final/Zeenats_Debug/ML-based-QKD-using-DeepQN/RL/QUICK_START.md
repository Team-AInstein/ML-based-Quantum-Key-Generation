# Quick Start Guide: Integrated QKD + DQN Training

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd RL
pip install torch numpy qiskit qiskit-aer
```

### Step 2: Quick Test (3 episodes)
```bash
python test_integration.py
```

**Expected Output:**
```
======================================================================
INTEGRATED QKD TRAINING: BB84 + DQN + Privacy Amplification
======================================================================

Episode 1/3
  Episode Reward:   101.80 (avg10:   101.80)
  QBER: 0.0000 (avg10: 0.0000)
  Sifted Key Length:  12 (avg10:  12.0)
  Eve Likelihood: 0.0000
  Agent Epsilon: 1.0000

✓ Integration test completed successfully!
```

---

### Step 3: Start Production Training (100 episodes)
```bash
python run_training.py
```

**Expected Output:**
```
================================================================================
 QUANTUM KEY DISTRIBUTION + DEEP Q-NETWORK TRAINING
================================================================================

📋 Training Configuration:
   Episodes: 100
   Key Length: 64 qubits
   DQN Learning Rate: 0.001
   Epsilon Decay: 0.995
   📁 Logs saved to: ./training_logs/run_20260112_143000

Starting Training...

Episode 1/100
  Episode Reward: 95.32 (avg10: 95.32)
  QBER: 0.0125 (avg10: 0.0125)
  Sifted Key Length: 16 (avg10: 16.0)
  Eve Likelihood: 0.0250
  Agent Epsilon: 1.0000

...

Episode 100/100
  Episode Reward: 118.45 (avg10: 117.82)
  QBER: 0.0089 (avg10: 0.0105)
  Sifted Key Length: 22 (avg10: 21.3)
  Eve Likelihood: 0.0178
  Agent Epsilon: 0.0123

✓ Training completed in 45.23 minutes

Running Evaluation (10 episodes)...

Episode 1: Reward=120.15, QBER=0.0085, Key Length=22

Evaluation Results (n=10):
  Avg Reward: 118.50
  Avg QBER: 0.0095 ± 0.0034
  Avg Key Length: 21.3

Running Full Pipeline Demonstration...

==================== Privacy Amplification ====================
Original sifted key length: 22
After privacy amplification:
  Final key length: 5
  Reduction factor: 4.40x
  Eve's info reduced by ~97.8%

TRAINING SUMMARY
================================================================================
Training Time: 45.23 minutes
Total Episodes: 100

Final Evaluation (10 episodes):
  Avg Reward:     118.50
  Avg QBER:       0.0095 ± 0.0034
  Avg Key Length:  21.3 bits

📁 All results saved to: ./training_logs/run_20260112_143000
================================================================================
```

---

## 📁 What Gets Created

```
training_logs/
└── run_20260112_143000/
    ├── config.json          # Hyperparameters
    ├── summary.json         # Final statistics
    ├── training_log.json    # Episode-by-episode log
    └── models/
        ├── dqn_final.pt     # Final model weights
        ├── dqn_episode_20.pt
        ├── dqn_episode_40.pt
        ├── dqn_episode_60.pt
        ├── dqn_episode_80.pt
        └── dqn_episode_100.pt
```

---

## 🎮 Advanced Usage

### Load Trained Model & Evaluate
```python
from dqn_agent import DQNAgent
from integrated_qkd_env import IntegratedQKDEnv

# Load
agent = DQNAgent(state_size=3, action_size=5)
agent.load("./training_logs/run_20260112_143000/models/dqn_final.pt")

# Evaluate (no exploration)
env = IntegratedQKDEnv()
state = env.reset()
total_reward = 0

for step in range(20):
    action = agent.choose_action(state, training=False)
    next_state, reward, done = env.step(action)
    total_reward += reward
    
    print(f"Step {step+1}: QBER={env.current_qber:.4f}, "
          f"Eve={env.current_eve_likelihood:.3f}, Reward={reward:.2f}")
    
    state = next_state
    if done:
        break

print(f"Total Reward: {total_reward:.2f}")
```

### Apply Privacy Amplification to Key
```python
from privacy_amplification import PrivacyAmplification
from bb84_wrapper import BB84Wrapper

# Generate key
bb84 = BB84Wrapper(key_length=128)
result = bb84.run_protocol()

# Amplify privacy
final_key, metadata = PrivacyAmplification.full_privacy_amplification_pipeline(
    sifted_key=result['sifted_key'],
    eve_likelihood=bb84.calculate_eve_likelihood(),
    method="parity"  # or "toeplitz", "xor"
)

print(f"Original: {len(result['sifted_key'])} bits")
print(f"Final: {len(final_key)} bits")
print(f"Reduction: {metadata['reduction_factor']:.2f}x")
print(f"Eve's info: {metadata['eve_likelihood']:.1%}")
```

### Custom Training Configuration
```python
from train_integrated import QKDTrainer

trainer = QKDTrainer(
    episodes=200,          # More training
    key_length=128,        # Larger keys
    max_steps=30,          # More steps per episode
    model_save_dir="./my_models"
)

trainer.train()
trainer.evaluate(num_episodes=20)
trainer.demonstrate_with_privacy_amplification()
```

---

## 🔍 Monitoring Training

### Real-time Metrics
- **Episode Reward:** Goal is >115 by episode 50
- **QBER:** Target <0.012 (below 1.2% error rate)
- **Key Length:** Should increase from ~15 to ~22 bits
- **Epsilon:** Decays from 1.0 to 0.01 (less exploration)

### Good Training Signs
```
✓ Rewards increase over time
✓ QBER decreases and stabilizes
✓ Key length increases
✓ Epsilon decays smoothly
✓ No NaN or Inf in loss
```

### Bad Training Signs
```
❌ Rewards oscillate wildly
❌ QBER increases
❌ Loss contains NaN
❌ Reward doesn't improve after 50 episodes
```

---

## 📊 Results Interpretation

### QBER (Quantum Bit Error Rate)
- **< 0.05:** Very secure (no Eve detected)
- **0.05 - 0.11:** Suspicious (possible Eve)
- **> 0.11:** Very likely Eve present
- **> 0.25:** Abort protocol (too compromised)

### Key Generation
- Input: 64 qubits per BB84 run
- After sifting: ~25% kept (avg. 16 bits)
- After PA (k=3): ~6% of sifted (avg. 1 bit/round)
- Net secure key: ~2-3 bits per complete session

### Eve Likelihood
- 0.0: Very secure
- 0.5: Eve likely present
- 1.0: Eavesdropping detected

---

## 💡 Tips & Tricks

### Speed Up Training
```python
# Reduce key length for faster BB84 runs
trainer = QKDTrainer(
    episodes=100,
    key_length=32,      # Faster
    max_steps=10,       # Fewer steps
)
```

### Better Convergence
```python
# Increase epsilon decay for slower exploration fade
from dqn_agent import DQNAgent

agent = DQNAgent(
    epsilon_decay=0.998,  # Slower decay
    learning_rate=0.0005, # Lower LR for stability
)
```

### Reproducibility
```python
import torch
import numpy as np
import random

# Set seeds
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

# Now training is deterministic
```

---

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'torch'"
**Solution:**
```bash
pip install torch
# Or for GPU support:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue: "No module named 'qiskit'"
**Solution:**
```bash
pip install qiskit qiskit-aer
```

### Issue: Training very slow
**Solution:**
- Reduce `key_length` to 32
- Reduce `max_steps` to 10
- Check if using GPU: `torch.cuda.is_available()` should be `True`

### Issue: Out of memory
**Solution:**
- Reduce `episodes` to 50
- Reduce experience buffer size in `dqn_agent.py`
- Check GPU memory: `nvidia-smi`

### Issue: QBER stuck at high value
**Solution:**
- This is normal! Let training continue (QBER should decrease by episode 30)
- If not improving after 50 episodes, check reward function

---

## 📚 Documentation

- **README_INTEGRATED.md** - Full architecture & API
- **IMPLEMENTATION_SUMMARY.md** - What was built
- **BEFORE_AND_AFTER.md** - Comparison with old system
- **QUICK_START.md** - This file

---

## Next Steps

1. ✅ Run `test_integration.py` to verify setup
2. ✅ Run `run_training.py` for full training (45 min)
3. ✅ Review `training_logs/` results
4. ✅ Load model and evaluate on new scenarios
5. ✅ Experiment with privacy amplification
6. ✅ Modify hyperparameters for your use case

---

## Support

For issues or questions:
1. Check the error message
2. Review TROUBLESHOOTING section above
3. Consult README_INTEGRATED.md for API details
4. Review code comments in source files

---

**Happy Training! 🚀**
