"""
Simple script to load and evaluate trained DQN model
"""

import os
import json
from pathlib import Path
from dqn_agent import DQNAgent
from integrated_qkd_env import IntegratedQKDEnv


def find_latest_model():
    """Find the most recent training run."""
    log_dir = Path("./training_logs")
    
    if not log_dir.exists():
        print("❌ No training_logs directory found!")
        print("Run 'python run_training.py' first to train a model.")
        return None
    
    # Find all run directories
    runs = sorted(log_dir.glob("run_*"))
    
    if not runs:
        print("❌ No training runs found in ./training_logs/")
        return None
    
    latest_run = runs[-1]
    model_path = latest_run / "models" / "dqn_final.pt"
    
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        return None
    
    print(f"✓ Found latest run: {latest_run.name}")
    print(f"✓ Model path: {model_path}")
    
    return model_path, latest_run


def load_and_evaluate(model_path, num_episodes=5):
    """Load trained model and evaluate."""
    
    print("\n" + "="*70)
    print("LOADING TRAINED MODEL")
    print("="*70)
    
    # Create agent
    agent = DQNAgent(state_size=3, action_size=5)
    
    # Load trained model
    print(f"\nLoading model from: {model_path}")
    agent.load(str(model_path))
    
    print(f"✓ Model loaded successfully!")
    print(f"  Epsilon: {agent.epsilon:.4f}")
    print(f"  Buffer size: {len(agent.experience_buffer)}")
    print(f"  Loss history: {len(agent.loss_history)} updates")
    
    # Evaluate on new episodes
    print("\n" + "="*70)
    print("EVALUATING ON TEST EPISODES")
    print("="*70)
    
    env = IntegratedQKDEnv(key_length=64, max_steps=20)
    
    episode_rewards = []
    episode_qbers = []
    episode_keys = []
    
    for episode in range(num_episodes):
        state = env.reset()
        episode_reward = 0
        
        print(f"\nEpisode {episode + 1}/{num_episodes}:")
        print(f"  Initial QBER: {env.current_qber:.4f}")
        print(f"  Eve Likelihood: {env.current_eve_likelihood:.4f}")
        
        for step in range(env.max_steps):
            # Choose action (NO EXPLORATION - only use learned policy)
            action = agent.choose_action(state, training=False)
            
            # Execute action in environment
            next_state, reward, done = env.step(action)
            
            episode_reward += reward
            state = next_state
            
            # Print step details
            action_names = [
                "Maintain",
                "Increase EC",
                "Decrease EC",
                "Reduce Key",
                "Apply PA"
            ]
            
            print(f"    Step {step + 1}: Action={action_names[action]:<15} "
                  f"QBER={env.current_qber:.4f} Reward={reward:>7.2f} "
                  f"Key={env.current_sifted_length:>2d}")
            
            if done:
                print(f"    → Episode ended at step {step + 1}")
                break
        
        # Store metrics
        episode_rewards.append(episode_reward)
        episode_qbers.append(env.current_qber)
        episode_keys.append(env.current_sifted_length)
        
        print(f"  Total Reward: {episode_reward:>8.2f}")
        print(f"  Final QBER: {env.current_qber:.4f}")
        print(f"  Final Key Length: {env.current_sifted_length} bits")
    
    # Summary statistics
    import numpy as np
    
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)
    print(f"\nEvaluated on {num_episodes} episodes:")
    print(f"  Avg Reward: {np.mean(episode_rewards):>8.2f} "
          f"(±{np.std(episode_rewards):.2f})")
    print(f"  Avg QBER: {np.mean(episode_qbers):.4f} "
          f"(±{np.std(episode_qbers):.4f})")
    print(f"  Avg Key Length: {np.mean(episode_keys):.1f} bits")
    print(f"\n✓ Evaluation complete!")
    
    return episode_rewards, episode_qbers, episode_keys


def main():
    """Main function."""
    
    print("\n" + "="*70)
    print("DQN MODEL EVALUATION")
    print("="*70)
    
    # Find latest model
    result = find_latest_model()
    
    if result is None:
        return
    
    model_path, run_dir = result
    
    # Load configuration
    config_path = run_dir / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        print(f"\n✓ Training config:")
        print(f"  Episodes: {config.get('episodes', 'N/A')}")
        print(f"  Key Length: {config.get('key_length', 'N/A')} qubits")
    
    # Load and evaluate
    load_and_evaluate(model_path, num_episodes=5)
    
    print("\n" + "="*70)
    print("✓ Done! Model evaluation complete.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
