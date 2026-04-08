"""Run a hyperparameter sweep over epsilon decay values and plot reward learning curves.

This script trains the same DQN agent for multiple epsilon-decay settings and
produces a comparison plot of average reward vs episode. It is intended to help
find the "Goldilocks" decay rate that balances exploration and exploitation.

Usage:
    python decay_experiment.py --episodes 200 --decays 0.85 0.90 0.95 0.99

Output:
    - decay_experiment_results.json
    - decay_experiment_plot.png

"""

import json
import os
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from train_integrated import QKDTrainer


def run_decay_experiment(episodes=200, decay_values=None, output_dir="."):
    if decay_values is None:
        decay_values = [0.85, 0.90, 0.95, 0.99]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    for decay in decay_values:
        print(f"\n=== Running decay={decay} ===")
        trainer = QKDTrainer(
            episodes=episodes,
            key_length=64,
            max_steps=20,
            env_config={
                'channel_error_rate': 0.01,
                'random_noise': True,
                'eve_probability': 0.5,
            },
            agent_config={
                'epsilon_decay': decay,
                'epsilon_min': 0.000000,
            },
            model_save_dir=str(output_dir / f"models_decay_{decay:.3f}"),
        )

        trainer.train()

        # Save raw per-episode reward curve
        results[decay] = {
            'episode_rewards': trainer.episode_rewards,
            'episode_qbers': trainer.episode_qbers,
            'episode_key_lengths': trainer.episode_key_lengths,
            'final_epsilon': trainer.agent.epsilon,
        }

        # Save a summary file for this decay
        summary_path = output_dir / f"summary_decay_{decay:.3f}.json"
        with open(summary_path, 'w') as f:
            json.dump(results[decay], f, indent=2)

    # Save combined results
    combined_path = output_dir / "decay_experiment_results.json"
    with open(combined_path, 'w') as f:
        json.dump(results, f, indent=2)

    # Plot (optional)
    if plt is None:
        print("\nmatplotlib is not installed; skipping plot generation.")
        print("Install it with: pip install matplotlib")
        return

    plt.figure(figsize=(10, 6))
    for decay, data in results.items():
        rewards = data['episode_rewards']
        # smooth with a 10-episode moving average
        window = 10
        smoothed = [
            sum(rewards[max(0, i - window + 1): i + 1]) /
            (min(i + 1, window))
            for i in range(len(rewards))
        ]
        plt.plot(smoothed, label=f"decay={decay:.3f}")

    plt.title("Average Reward (10-episode MA) vs Episode")
    plt.xlabel("Episode")
    plt.ylabel("Avg Reward")
    plt.legend()
    plt.grid(True)

    plot_path = output_dir / "decay_experiment_plot.png"
    plt.tight_layout()
    plt.savefig(plot_path)
    print(f"\nSaved plot to {plot_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run epsilon-decay sweep experiments")
    parser.add_argument('--episodes', type=int, default=200,
                        help='Number of episodes per decay value')
    parser.add_argument('--decays', type=float, nargs='+',
                        default=[0.85, 0.90, 0.95, 0.99],
                        help='List of epsilon decay values to test')
    parser.add_argument('--out', type=str, default='decay_experiment_results',
                        help='Output directory for results and plot')
    args = parser.parse_args()

    run_decay_experiment(episodes=args.episodes, decay_values=args.decays, output_dir=args.out)
