# Integrated QKD + DQN Training System

## Overview

This enhanced system integrates **Real BB84 Protocol Execution**, **Deep Q-Networks (DQN)**, **Advanced Eve Detection**, **Privacy Amplification**, and **Model Persistence** into a cohesive quantum key distribution optimization framework.

## Components

### 1. **BB84 Wrapper** (`bb84_wrapper.py`)
Real quantum key distribution protocol implementation that interfaces with RL.

**Features:**
- Generates cryptographically random bits using quantum simulation
- Simulates Eve's eavesdropping with configurable interception ratio
- Calculates Quantum Bit Error Rate (QBER) for eavesdropping detection
- Returns sifted keys, measurement data, and Eve likelihood

**Key Methods:**
```python
bb84 = BB84Wrapper(key_length=64, eve_present=True, eve_intercept_ratio=0.5)
result = bb84.run_protocol()
# Returns: sifted_key, qber, eve_likelihood, measurements_data
```

---

### 2. **Integrated QKD Environment** (`integrated_qkd_env.py`)
RL environment that executes real BB84 runs and provides feedback.

**State Space:** `(QBER_normalized, Eve_Likelihood, Sifted_Key_Ratio)`
- Continuous normalized values in [0, 1]
- Updated after each BB84 execution

**Action Space:** 5 discrete actions
- `0`: Maintain parameters (baseline)
- `1`: Increase error correction strength
- `2`: Decrease error correction (noisier but faster)
- `3`: Reduce key length (abort if too many errors)
- `4`: Apply privacy amplification

**Reward Function:**
```
reward = key_bits_generated * 0.1
       - qber_penalty (if QBER > threshold)
       + eve_detection_bonus (if likely Eve present)
```

**Example:**
```python
env = IntegratedQKDEnv(key_length=64, max_steps=20)
state = env.reset()
next_state, reward, done = env.step(action=1)
```

---

### 3. **Deep Q-Network (DQN)** (`dqn_agent.py`)
Neural network-based RL agent that learns optimal QKD strategies.

**Architecture:**
```
Input Layer (3) → Dense (128, ReLU) → Dropout(0.2)
                → Dense (128, ReLU) → Dropout(0.2)
                → Output Layer (5 actions)
```

**Key Features:**
- **Experience Replay:** Stores and samples from buffer of 10,000 experiences
- **Target Network:** Separate frozen network for stability
- **Epsilon-Greedy:** Exploration decay from 1.0 to 0.01 over training
- **Gradient Clipping:** Prevents exploding gradients
- **Persistent Storage:** Save/load model weights and optimizer state

**Training Loop:**
```python
agent = DQNAgent(state_size=3, action_size=5)
for experience in episodes:
    state = env.reset()
    while not done:
        action = agent.choose_action(state, training=True)
        next_state, reward, done = env.step(action)
        agent.remember(state, action, reward, next_state, done)
        loss = agent.replay()  # Mini-batch training
        state = next_state
```

**Hyperparameters:**
```python
learning_rate = 0.001   # Adam optimizer
gamma = 0.99            # Discount factor
epsilon = 1.0 → 0.01   # Exploration decay
batch_size = 32         # Mini-batch for replay
target_update_freq = 100 # Sync target network every 100 updates
```

---

### 4. **Privacy Amplification** (`privacy_amplification.py`)
Reduces Eve's information about the final key from O(1/2) to O(2^-k).

**Methods:**

#### A. Parity-Check Based PA
Iterative XOR of adjacent bits. Eve's information ≈ 2^-k after k rounds.
```python
final_key = PrivacyAmplification.parity_check_pa(sifted_key, num_rounds=3)
```

#### B. Toeplitz Matrix PA
XOR subsets according to random Toeplitz matrix pattern.
```python
final_key = PrivacyAmplification.toeplitz_matrix_pa(sifted_key, compression_factor=0.5)
```

#### C. XOR Compression
Simple XOR of fixed-size groups.
```python
final_key = PrivacyAmplification.xor_compression(sifted_key, group_size=4)
```

#### D. Error Correction
Majority voting if Eve likely present (probability > 0.5).

**Full Pipeline:**
```python
final_key, metadata = PrivacyAmplification.full_privacy_amplification_pipeline(
    sifted_key=bob_key,
    eve_likelihood=0.75,
    method="parity"  # or "toeplitz", "xor"
)
# metadata contains: original_length, final_length, reduction_factor, eve_likelihood
```

**Privacy Guarantee:**
- Original QBER ≈ 0: Eve gets ~50% info per bit
- After PA round 1: Eve gets ~25% info
- After PA round k: Eve gets ~2^-k of original info

---

### 5. **Integrated Training** (`train_integrated.py`)
Orchestrates complete training pipeline with all components.

**QKDTrainer Class:**

```python
trainer = QKDTrainer(
    episodes=100,           # Training episodes
    key_length=64,          # BB84 qubits per run
    max_steps=20,           # Steps per episode
    model_save_dir="./models"
)

# Full training with checkpoints
trainer.train()

# Evaluate (no exploration)
eval_stats = trainer.evaluate(num_episodes=10)

# Demonstrate full pipeline
trainer.demonstrate_with_privacy_amplification()
```

**Output:**
- DQN model weights: `./models/dqn_final.pt`
- Training log: `./models/training_log.json`
- Checkpoints: `./models/dqn_episode_{N}.pt` (every 20 episodes)

**Statistics Tracked:**
```
Episode Results:
  - Episode Reward (mean, std)
  - QBER (mean, std)
  - Sifted Key Length (mean)
  - Agent Epsilon (exploration rate)
```

---

## How They Work Together

### Training Flow:

```
┌─────────────────────────────────────────────────┐
│ Episode Start                                   │
└────────────┬────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────┐
│ Environment Reset                               │
│  - Random Eve: 50% chance eavesdropping         │
│  - Initialize protocol parameters              │
└────────────┬────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────┐
│ Agent Observes State                            │
│  (QBER, Eve_Likelihood, Key_Ratio)             │
└────────────┬────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────┐
│ DQN Chooses Action (ε-greedy)                   │
│  - Exploration: random action (ε prob)         │
│  - Exploitation: argmax Q(s, a) (1-ε prob)     │
└────────────┬────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────┐
│ Environment Executes Action                     │
│  - Adjust EC strength / key length              │
│  - Run real BB84 protocol                       │
│  - Extract QBER, sifted key                     │
└────────────┬────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────┐
│ Compute Reward                                  │
│  - Key generation quality                       │
│  - QBER penalty / bonus                         │
│  - Eve detection reward                         │
└────────────┬────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────┐
│ DQN Learning                                    │
│  - Store: (state, action, reward, next_state)  │
│  - Sample mini-batch from replay buffer         │
│  - Compute Q-loss using target network          │
│  - Backprop & update weights                    │
│  - Sync target network (every 100 updates)     │
└────────────┬────────────────────────────────────┘
             ↓
        Repeat or
          Done?
             ↓
     (Apply Privacy
      Amplification)
```

---

## Usage Examples

### Example 1: Basic Training (50 episodes)
```python
from train_integrated import QKDTrainer

trainer = QKDTrainer(episodes=50, key_length=64, max_steps=20)
trainer.train()
trainer.evaluate(num_episodes=10)
```

### Example 2: Load and Fine-Tune Existing Model
```python
from dqn_agent import DQNAgent
from integrated_qkd_env import IntegratedQKDEnv

agent = DQNAgent(state_size=3, action_size=5)
agent.load("./models/dqn_final.pt")

env = IntegratedQKDEnv()
state = env.reset()
action = agent.choose_action(state, training=False)  # Exploit only
```

### Example 3: Generate Secure Key with Privacy Amplification
```python
from bb84_wrapper import BB84Wrapper
from privacy_amplification import PrivacyAmplification

# Run BB84
bb84 = BB84Wrapper(key_length=128, eve_present=False)
result = bb84.run_protocol()

# Apply privacy amplification
final_key, metadata = PrivacyAmplification.full_privacy_amplification_pipeline(
    sifted_key=result['sifted_key'],
    eve_likelihood=bb84.calculate_eve_likelihood(),
    method="parity"
)

print(f"Secure key: {final_key}")
print(f"Length: {metadata['final_length']} bits")
print(f"Eve's info reduced by: {metadata['reduction_factor']:.2f}x")
```

### Example 4: Eve Detection & Response
```python
env = IntegratedQKDEnv(key_length=64, max_steps=15)
state = env.reset()

print(f"Eve Likelihood: {state[1]:.3f}")

if state[1] > 0.5:
    print("⚠ Likely Eve detected! Applying countermeasures...")
    action = 4  # Privacy amplification
else:
    print("✓ Channel appears secure")
    action = 0  # Maintain

next_state, reward, done = env.step(action)
```

---

## Key Improvements

| Feature | Before | After |
|---------|--------|-------|
| **Protocol** | Simplified env | Real BB84 with Qiskit |
| **RL Agent** | Tabular Q-learning | Deep Q-Network (neural net) |
| **Eve Model** | Binary threshold | Probabilistic likelihood |
| **Privacy** | Not implemented | Full PA pipeline (3 methods) |
| **Persistence** | Lost each run | Save/load model weights |
| **Scalability** | Fixed state/action | Extensible (state_size, action_size params) |

---

## Files

```
RL/
├── bb84_wrapper.py              # Real BB84 protocol
├── integrated_qkd_env.py        # RL environment with real BB84
├── dqn_agent.py                 # Deep Q-Network agent
├── privacy_amplification.py     # PA implementations
├── train_integrated.py          # Main training script
├── test_integration.py          # Quick integration test
└── models/
    ├── dqn_final.pt             # Final trained model
    ├── dqn_episode_*.pt         # Checkpoints
    └── training_log.json        # Statistics
```

---

## Future Enhancements

1. **Double DQN:** Reduce overestimation in Q-values
2. **Dueling DQN:** Separate value and advantage streams
3. **Prioritized Experience Replay:** Weight important experiences higher
4. **Multi-Agent:** Alice, Bob, Eve as separate agents
5. **Real Quantum Hardware:** Deploy on IBM quantum computers
6. **Adaptive Epsilon:** Decay based on training progress
7. **Eve Learning:** Adaptive eavesdropper that learns counter-strategies

---

## References

- Bennett & Brassard (1984): BB84 Protocol
- Shor & Preskill (2000): Security of QKD
- Van Hasselt et al. (2015): Deep Reinforcement Learning with Double Q-learning
- Wang et al. (2015): Dueling Network Architectures
- Mnih et al. (2015): Human-level control through DQN

---

## License

MIT License - See LICENSE file for details

---

**Contact:** QKD Research Team
