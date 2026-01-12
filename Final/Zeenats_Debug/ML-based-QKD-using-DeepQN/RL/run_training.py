"""
Production Training Script: Full-Scale DQN Training on Integrated QKD
Use this for actual training sessions with comprehensive logging
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

from train_integrated import QKDTrainer


def setup_logging_directory():
    """Create timestamped directory for this training run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path(f"./training_logs/run_{timestamp}")
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def save_training_config(log_dir, config):
    """Save training configuration."""
    config_path = log_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✓ Config saved to {config_path}")


def main():
    """Main training runner."""
    
    print("\n" + "=" * 80)
    print(" QUANTUM KEY DISTRIBUTION + DEEP Q-NETWORK TRAINING")
    print(" Integrated: Real BB84 + DQN + Privacy Amplification")
    print("=" * 80)
    
    # Configuration
    config = {
        'episodes': 100,
        'key_length': 64,
        'max_steps': 20,
        'dqn_learning_rate': 0.001,
        'dqn_gamma': 0.99,
        'dqn_epsilon_start': 1.0,
        'dqn_epsilon_min': 0.01,
        'dqn_epsilon_decay': 0.995,
        'batch_size': 32,
    }
    
    # Setup logging
    log_dir = setup_logging_directory()
    save_training_config(log_dir, config)
    
    # Create trainer
    print(f"\n📋 Training Configuration:")
    print(f"   Episodes: {config['episodes']}")
    print(f"   Key Length: {config['key_length']} qubits")
    print(f"   Max Steps/Episode: {config['max_steps']}")
    print(f"   DQN Learning Rate: {config['dqn_learning_rate']}")
    print(f"   Gamma (discount): {config['dqn_gamma']}")
    print(f"   Epsilon Decay: {config['dqn_epsilon_decay']}")
    print(f"   Batch Size: {config['batch_size']}")
    print(f"\n   📁 Logs saved to: {log_dir}")
    
    trainer = QKDTrainer(
        episodes=config['episodes'],
        key_length=config['key_length'],
        max_steps=config['max_steps'],
        model_save_dir=str(log_dir / "models")
    )
    
    # Training
    print("\n" + "-" * 80)
    print("Starting Training...")
    print("-" * 80)
    
    start_time = time.time()
    trainer.train()
    training_time = time.time() - start_time
    
    print(f"\n✓ Training completed in {training_time/60:.2f} minutes")
    
    # Evaluation
    print("\n" + "-" * 80)
    print("Running Evaluation (10 episodes)...")
    print("-" * 80)
    eval_stats = trainer.evaluate(num_episodes=10)
    
    # Demonstration
    print("\n" + "-" * 80)
    print("Running Full Pipeline Demonstration...")
    print("-" * 80)
    trainer.demonstrate_with_privacy_amplification()
    
    # Save summary
    summary = {
        'training_time_seconds': training_time,
        'training_time_minutes': training_time / 60,
        'total_episodes': config['episodes'],
        'evaluation_results': {
            'avg_reward': float(eval_stats['avg_reward']),
            'avg_qber': float(eval_stats['avg_qber']),
            'avg_key_length': float(eval_stats['avg_key_length']),
            'std_qber': float(eval_stats['std_qber']),
        },
        'training_results': {
            'avg_reward_all': float(__import__('numpy').mean(trainer.episode_rewards)),
            'avg_qber_all': float(__import__('numpy').mean(trainer.episode_qbers)),
            'avg_key_length_all': float(__import__('numpy').mean(trainer.episode_key_lengths)),
        }
    }
    
    summary_path = log_dir / "summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 80)
    print("TRAINING SUMMARY")
    print("=" * 80)
    print(f"Training Time: {summary['training_time_minutes']:.2f} minutes")
    print(f"Total Episodes: {summary['total_episodes']}")
    print(f"\nFinal Evaluation (10 episodes):")
    print(f"  Avg Reward: {eval_stats['avg_reward']:>8.2f}")
    print(f"  Avg QBER: {eval_stats['avg_qber']:>6.4f} ± {eval_stats['std_qber']:>6.4f}")
    print(f"  Avg Key Length: {eval_stats['avg_key_length']:>5.1f} bits")
    print(f"\nTraining Averages (all {config['episodes']} episodes):")
    print(f"  Avg Reward: {summary['training_results']['avg_reward_all']:>8.2f}")
    print(f"  Avg QBER: {summary['training_results']['avg_qber_all']:>6.4f}")
    print(f"  Avg Key Length: {summary['training_results']['avg_key_length_all']:>5.1f} bits")
    print(f"\n📁 All results saved to: {log_dir}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
