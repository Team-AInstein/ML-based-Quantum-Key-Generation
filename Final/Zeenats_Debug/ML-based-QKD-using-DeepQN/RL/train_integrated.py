"""
Integrated Training Script: Real BB84 + DQN + Privacy Amplification
Trains DQN agent to optimize QKD parameters under eavesdropping attacks
"""

import os
import json
import numpy as np
from pathlib import Path

from integrated_qkd_env import IntegratedQKDEnv
from dqn_agent import DQNAgent
from privacy_amplification import PrivacyAmplification


class QKDTrainer:
    """Orchestrates training of DQN agent on integrated QKD environment."""
    
    def __init__(self, 
                 episodes: int = 100,
                 key_length: int = 64,
                 max_steps: int = 20,
                 model_save_dir: str = "./models"):
        """
        Initialize trainer.
        
        Args:
            episodes: Number of training episodes
            key_length: Bits per BB84 run
            max_steps: Steps per episode
            model_save_dir: Directory to save models
        """
        self.episodes = episodes
        self.key_length = key_length
        self.max_steps = max_steps
        self.model_save_dir = model_save_dir
        
        # Create directories
        Path(model_save_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize environment and agent
        self.env = IntegratedQKDEnv(key_length=key_length, max_steps=max_steps)
        self.agent = DQNAgent(
            state_size=3,
            action_size=5,
            learning_rate=0.001,
            gamma=0.99,
            epsilon=1.0,
            epsilon_decay=0.995
        )
        
        # Training statistics
        self.episode_rewards = []
        self.episode_qbers = []
        self.episode_key_lengths = []
        self.training_log = []
    
    def train(self):
        """Run full training loop."""
        print("=" * 70)
        print("INTEGRATED QKD TRAINING: BB84 + DQN + Privacy Amplification")
        print("=" * 70)
        
        for episode in range(self.episodes):
            state = self.env.reset()
            episode_reward = 0
            episode_data = {
                'episode': episode,
                'steps': [],
                'final_qber': 0,
                'final_sifted_length': 0,
                'final_eve_likelihood': 0,
            }
            
            for step in range(self.max_steps):
                # Agent chooses action
                action = self.agent.choose_action(state, training=True)
                
                # Environment executes action (runs real BB84)
                next_state, reward, done = self.env.step(action)
                
                # Agent remembers experience
                self.agent.remember(state, action, reward, next_state, done)
                
                # Agent learns
                loss = self.agent.replay()
                
                episode_reward += reward
                state = next_state
                
                if done:
                    break
            
            # Episode statistics
            episode_data['final_qber'] = self.env.current_qber
            episode_data['final_sifted_length'] = self.env.current_sifted_length
            episode_data['final_eve_likelihood'] = self.env.current_eve_likelihood
            episode_data['total_reward'] = episode_reward
            
            self.episode_rewards.append(episode_reward)
            self.episode_qbers.append(self.env.current_qber)
            self.episode_key_lengths.append(self.env.current_sifted_length)
            self.training_log.append(episode_data)
            
            # Print progress
            if (episode + 1) % 10 == 0 or episode == 0:
                avg_reward = np.mean(self.episode_rewards[-10:])
                avg_qber = np.mean(self.episode_qbers[-10:])
                avg_key_len = np.mean(self.episode_key_lengths[-10:])
                
                print(f"\nEpisode {episode + 1}/{self.episodes}")
                print(f"  Episode Reward: {episode_reward:>8.2f} (avg10: {avg_reward:>8.2f})")
                print(f"  QBER: {self.env.current_qber:>6.4f} (avg10: {avg_qber:>6.4f})")
                print(f"  Sifted Key Length: {self.env.current_sifted_length:>3d} (avg10: {avg_key_len:>5.1f})")
                print(f"  Eve Likelihood: {self.env.current_eve_likelihood:>6.4f}")
                print(f"  Agent Epsilon: {self.agent.epsilon:>6.4f}")
                
                # Save model periodically
                if (episode + 1) % 20 == 0:
                    self._save_checkpoint(episode + 1)
        
        print("\n" + "=" * 70)
        print("TRAINING COMPLETE")
        print("=" * 70)
        self._save_final_model()
        self._save_training_log()
    
    def evaluate(self, num_episodes: int = 10):
        """
        Evaluate trained agent (exploitation only).
        """
        print("\n" + "=" * 70)
        print("EVALUATION MODE (No Exploration)")
        print("=" * 70)
        
        # Disable exploration
        original_epsilon = self.agent.epsilon
        self.agent.epsilon = 0.0
        
        eval_rewards = []
        eval_qbers = []
        eval_key_lengths = []
        
        for episode in range(num_episodes):
            state = self.env.reset()
            episode_reward = 0
            
            for step in range(self.max_steps):
                action = self.agent.choose_action(state, training=False)
                next_state, reward, done = self.env.step(action)
                episode_reward += reward
                state = next_state
                
                if done:
                    break
            
            eval_rewards.append(episode_reward)
            eval_qbers.append(self.env.current_qber)
            eval_key_lengths.append(self.env.current_sifted_length)
            
            if (episode + 1) % max(1, num_episodes // 5) == 0:
                print(f"  Episode {episode + 1}: Reward={episode_reward:>8.2f}, "
                      f"QBER={self.env.current_qber:>6.4f}, "
                      f"Key Length={self.env.current_sifted_length:>3d}")
        
        # Restore epsilon
        self.agent.epsilon = original_epsilon
        
        eval_stats = {
            'avg_reward': np.mean(eval_rewards),
            'avg_qber': np.mean(eval_qbers),
            'avg_key_length': np.mean(eval_key_lengths),
            'std_qber': np.std(eval_qbers),
        }
        
        print(f"\nEvaluation Results (n={num_episodes}):")
        print(f"  Avg Reward: {eval_stats['avg_reward']:>8.2f}")
        print(f"  Avg QBER: {eval_stats['avg_qber']:>6.4f} ± {eval_stats['std_qber']:>6.4f}")
        print(f"  Avg Key Length: {eval_stats['avg_key_length']:>5.1f}")
        
        return eval_stats
    
    def demonstrate_with_privacy_amplification(self):
        """
        Demonstrate the full pipeline with privacy amplification.
        """
        print("\n" + "=" * 70)
        print("DEMONSTRATION: Full Pipeline with Privacy Amplification")
        print("=" * 70)
        
        # Run one episode
        state = self.env.reset()
        print(f"\nInitial State: QBER={state[0]:.3f}, Eve={state[1]:.3f}, Key Ratio={state[2]:.3f}")
        
        for step in range(self.max_steps):
            action = self.agent.choose_action(state, training=False)
            next_state, reward, done = self.env.step(action)
            
            print(f"\nStep {step + 1}:")
            print(f"  Action: {action}")
            print(f"  Reward: {reward:>8.2f}")
            print(f"  New State: QBER={next_state[0]:.3f}, Eve={next_state[1]:.3f}, Key Ratio={next_state[2]:.3f}")
            
            state = next_state
            
            if done:
                break
        
        # Apply privacy amplification to final key
        if self.env.current_bb84.sifted_key:
            print(f"\n--- Privacy Amplification ---")
            print(f"Original sifted key length: {len(self.env.current_bb84.sifted_key)}")
            
            final_key, metadata = PrivacyAmplification.full_privacy_amplification_pipeline(
                self.env.current_bb84.sifted_key,
                eve_likelihood=self.env.current_eve_likelihood,
                method="parity"
            )
            
            print(f"After privacy amplification:")
            print(f"  Final key length: {len(final_key)}")
            print(f"  Reduction factor: {metadata['reduction_factor']:.2f}x")
            print(f"  Eve's info reduced by ~{(1 - self.env.current_eve_likelihood) * 100:.1f}%")
    
    def _save_checkpoint(self, episode: int):
        """Save model checkpoint."""
        checkpoint_path = os.path.join(self.model_save_dir, f"dqn_episode_{episode}.pt")
        self.agent.save(checkpoint_path)
    
    def _save_final_model(self):
        """Save final trained model."""
        final_path = os.path.join(self.model_save_dir, "dqn_final.pt")
        self.agent.save(final_path)
    
    def _save_training_log(self):
        """Save training statistics."""
        log_path = os.path.join(self.model_save_dir, "training_log.json")
        stats = {
            'total_episodes': self.episodes,
            'total_reward_mean': float(np.mean(self.episode_rewards)),
            'total_reward_std': float(np.std(self.episode_rewards)),
            'qber_mean': float(np.mean(self.episode_qbers)),
            'qber_std': float(np.std(self.episode_qbers)),
            'key_length_mean': float(np.mean(self.episode_key_lengths)),
        }
        
        with open(log_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✓ Training log saved to {log_path}")


if __name__ == "__main__":
    # Create and run trainer
    trainer = QKDTrainer(episodes=50, key_length=64, max_steps=15)
    
    # Train
    trainer.train()
    
    # Evaluate
    trainer.evaluate(num_episodes=5)
    
    # Demonstrate full pipeline
    trainer.demonstrate_with_privacy_amplification()
    
    print("\n✓ All done!")
