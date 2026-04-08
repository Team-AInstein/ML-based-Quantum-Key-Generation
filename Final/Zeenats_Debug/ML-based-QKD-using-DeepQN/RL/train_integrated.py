"""
Integrated Training Script: Real BB84 + DQN + Privacy Amplification
Trains DQN agent to optimize QKD parameters under eavesdropping attacks
"""

import os
import json
import numpy as np
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from integrated_qkd_env import IntegratedQKDEnv
from dqn_agent import DQNAgent
from privacy_amplification import PrivacyAmplification


class QKDTrainer:
    """Orchestrates training of DQN agent on integrated QKD environment."""
    
    def __init__(self, 
                 episodes: int = 100,
                 key_length: int = 128,
                 max_steps: int = 20,
                 model_save_dir: str = "./models",
                 env_config: dict = None,
                 agent_config: dict = None,
                 live_plot: bool = False):
        """
        Initialize trainer.
        
        Args:
            episodes: Number of training episodes
            key_length: Bits per BB84 run
            max_steps: Steps per episode
            model_save_dir: Directory to save models
            env_config: Optional dictionary of parameters to pass to
                ``IntegratedQKDEnv`` (channel_error_rate, random_noise, etc.)
            agent_config: Optional parameters for ``DQNAgent`` (learning_rate,
                gamma, epsilon_decay, epsilon_min, etc.)
        """
        self.episodes = episodes
        self.key_length = key_length
        self.max_steps = max_steps
        self.model_save_dir = model_save_dir
        
        # Create directories
        Path(model_save_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize environment and agent
        self.env = IntegratedQKDEnv(key_length=key_length, max_steps=max_steps,
                                     **(env_config or {}))
        agent_params = {
            'state_size': 3,
            'action_size': 5,
            'learning_rate': 0.0001,
            'gamma': 0.99,
            'epsilon': 1.0,
            'epsilon_decay': 0.995,
            'epsilon_min': 0.01,
            'batch_size': 32,
            'target_update_frequency': 50,
        }
        if agent_config:
            agent_params.update(agent_config)
        self.agent = DQNAgent(**agent_params)
        self.live_plot = live_plot and (plt is not None)

        # Training statistics
        self.episode_rewards = []
        self.episode_losses = []
        self.episode_qbers = []
        self.episode_key_lengths = []
        self.training_log = []

        # Track baseline QBER to report percent reduction
        self._initial_qber = None

        # Optional live plot
        self._plot_data = None
        if self.live_plot:
            self._init_live_plot()
    
    def _init_live_plot(self):
        """Initialize live plotting windows."""
        plt.ion()
        fig = plt.figure(figsize=(10, 8))
        ax1 = fig.add_subplot(3, 1, 1)
        ax2 = fig.add_subplot(3, 1, 2)
        ax3 = fig.add_subplot(3, 1, 3)

        ax1.set_title('Average Reward (10-episode MA)')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Reward')
        ax2.set_title('Average Loss (10-episode MA)')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Loss')
        ax3.set_title('Average QBER (10-episode MA)')
        ax3.set_xlabel('Episode')
        ax3.set_ylabel('QBER')

        self._plot_data = {
            'fig': fig,
            'ax_reward': ax1,
            'ax_loss': ax2,
            'ax_qber': ax3,
            'line_reward': ax1.plot([], [], label='reward')[0],
            'line_loss': ax2.plot([], [], label='loss')[0],
            'line_qber': ax3.plot([], [], label='qber')[0],
        }
        ax1.legend()
        ax2.legend()
        ax3.legend()

    def _update_live_plot(self):
        """Update live plot with latest stats."""
        if not self.live_plot or self._plot_data is None:
            return

        window = 10
        def moving_average(xs):
            return [
                sum(xs[max(0, i - window + 1): i + 1]) / min(i + 1, window)
                for i in range(len(xs))
            ]

        rewards_ma = moving_average(self.episode_rewards)
        losses_ma = moving_average(self.episode_losses)
        qbers_ma = moving_average(self.episode_qbers)

        reduced_pct = 0.0
        if self._initial_qber is not None and self._initial_qber > 0:
            reduced_pct = (self._initial_qber - qbers_ma[-1]) / self._initial_qber * 100

        self._plot_data['line_reward'].set_data(range(len(rewards_ma)), rewards_ma)
        self._plot_data['line_loss'].set_data(range(len(losses_ma)), losses_ma)
        self._plot_data['line_qber'].set_data(range(len(qbers_ma)), qbers_ma)

        # Update QBER axis title with percent reduction
        self._plot_data['ax_qber'].set_title(
            f"Average QBER (10-episode MA) — reduced {reduced_pct:.1f}%"
        )

        self._plot_data['ax_reward'].relim()
        self._plot_data['ax_reward'].autoscale_view()
        self._plot_data['ax_loss'].relim()
        self._plot_data['ax_loss'].autoscale_view()
        self._plot_data['ax_qber'].relim()
        self._plot_data['ax_qber'].autoscale_view()

        plt.pause(0.001)

    def train(self):
        """Run full training loop."""
        print("=" * 70)
        print("INTEGRATED QKD TRAINING: BB84 + DQN + Privacy Amplification")
        print("=" * 70)
        
        for episode in range(self.episodes):
            state = self.env.reset()

            # Record initial QBER for percentage reduction reporting
            if self._initial_qber is None:
                self._initial_qber = self.env.current_qber

            episode_reward = 0
            episode_losses = []
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
                if loss is not None:
                    episode_losses.append(loss)
                
                episode_reward += reward
                state = next_state
                
                if done:
                    break
            # decay exploration after each episode instead of per step
            self.agent.update_epsilon()

            # Episode statistics
            avg_loss = float(np.mean(episode_losses)) if episode_losses else 0.0
            self.episode_losses.append(avg_loss)
            
            # Episode statistics
            episode_data['final_qber'] = self.env.current_qber
            episode_data['final_sifted_length'] = self.env.current_sifted_length
            episode_data['final_eve_likelihood'] = self.env.current_eve_likelihood
            episode_data['total_reward'] = episode_reward
            
            self.episode_rewards.append(episode_reward)
            self.episode_qbers.append(self.env.current_qber)
            self.episode_key_lengths.append(self.env.current_sifted_length)
            self.training_log.append(episode_data)

            # Update live plot (if enabled)
            self._update_live_plot()
            
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
                print(f"  Agent Epsilon: {self.agent.epsilon:>8.6f} (min {self.agent.epsilon_min:.6f})")
                if self.agent.epsilon <= self.agent.epsilon_min:
                    print("  ⚠ Epsilon reached minimum; agent is now effectively greedy")
                
                # Save model periodically
                if (episode + 1) % 20 == 0:
                    self._save_checkpoint(episode + 1)
        
        print("\n" + "=" * 70)
        print("TRAINING COMPLETE")
        print("=" * 70)
        self._save_final_model()
        self._save_training_log()

        # If live plotting was used, save the final plot image for later review
        if self.live_plot and self._plot_data is not None:
            plot_path = os.path.join(self.model_save_dir, "training_plot.png")
            try:
                self._plot_data['fig'].savefig(plot_path)
                print(f"✓ Live training plot saved to {plot_path}")
            except Exception as e:
                print(f"⚠ Failed to save live plot: {e}")
    
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
        eval_keys = []
        
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
            eval_keys.append(self.env.current_bb84.sifted_key)
            
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
            'final_keys': eval_keys
        }
        
        print(f"\nEvaluation Results (n={num_episodes}):")
        print(f"  Avg Reward: {eval_stats['avg_reward']:>8.2f}")
        print(f"  Avg QBER: {eval_stats['avg_qber']:>6.4f} ± {eval_stats['std_qber']:>6.4f}")
        print(f"  Avg Key Length: {eval_stats['avg_key_length']:>5.1f}")
        
        return eval_stats
    
    def demonstrate_with_privacy_amplification(self):
        """
        Demonstrate the full pipeline with privacy amplification.

        Returns:
            Tuple[str, dict]: final_key and metadata produced by PA. Useful for
            downstream encryption or saving to disk.
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
        
        final_key = ""
        metadata = {}
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
        else:
            print("\nNo sifted key available; skipping privacy amplification.")
        
        return final_key, metadata
    
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
        
        # Save last 20 steps of episode history for debugging QBER spikes
        history_path = os.path.join(self.model_save_dir, "episode_history_last20.json")
        try:
            with open(history_path, 'w') as f:
                json.dump(self.env.episode_history[-20:], f, indent=2)
            print(f"✓ Last 20 steps of episode history saved to {history_path}")
        except Exception:
            print("⚠ Unable to save episode history; skipping.")

        print(f"✓ Training log saved to {log_path}")


if __name__ == "__main__":
    # Example showing how to pass a noisy environment and run evaluation
    env_kwargs = {
        'channel_error_rate': 0.02,
        'random_noise': True,
        'eve_probability': 0.5
    }
    trainer = QKDTrainer(
        episodes=100,
        key_length=128,
        max_steps=20,
        env_config=env_kwargs
    )
    
    # Train
    trainer.train()
    
    # Evaluate
    stats = trainer.evaluate(num_episodes=5)
    
    # Demonstrate full pipeline
    trainer.demonstrate_with_privacy_amplification()
    
    # save last evaluation stats for later inspection
    with open(os.path.join(trainer.model_save_dir, 'last_evaluation.json'), 'w') as f:
        json.dump(stats, f, indent=2)
    print("\n✓ All done!")
