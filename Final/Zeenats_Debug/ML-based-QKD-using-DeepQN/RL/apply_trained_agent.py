"""
Simple utility that loads a saved DQN model, runs the IntegratedQKDEnv
for one episode using the greedy policy, prints QBER and generated key,
then exercises the frontend encryption module with the resulting key.

Usage:
    python apply_trained_agent.py path/to/model.pt

The script demonstrates how to take the output of a trained agent and use
it for real encryption tests.
"""

import os
import sys
import argparse

# append frontend path to import the quantum_encryption module
here = os.path.dirname(__file__)
frontend_path = os.path.abspath(os.path.join(here, '..', '..', 'frontend'))
if frontend_path not in sys.path:
    sys.path.insert(0, frontend_path)

from integrated_qkd_env import IntegratedQKDEnv
from dqn_agent import DQNAgent
from quantum_encryption import QuantumEncryption


def load_agent(model_path: str) -> DQNAgent:
    agent = DQNAgent(state_size=3, action_size=5)
    agent.load(model_path)
    # make sure exploration is turned off
    agent.epsilon = 0.0
    return agent


def main():
    parser = argparse.ArgumentParser(description="Use trained RL agent for QKD and encryption")
    parser.add_argument('model', help="path to saved DQN model (.pt file)")
    parser.add_argument('--noise', type=float, default=0.01,
                        help="baseline channel error rate for environment")
    parser.add_argument('--random-noise', action='store_true',
                        help="randomise noise each BB84 run")
    parser.add_argument('--message', default="Hello from RL agent!",
                        help="plaintext message to encrypt with generated key")
    args = parser.parse_args()

    env = IntegratedQKDEnv(key_length=128,
                            max_steps=20,
                            channel_error_rate=args.noise,
                            random_noise=args.random_noise,
                            eve_probability=0.5)
    agent = load_agent(args.model)

    state = env.reset()
    done = False
    steps = 0
    while not done and steps < env.max_steps:
        action = agent.choose_action(state, training=False)
        state, reward, done = env.step(action)
        steps += 1

    print(f"Final QBER: {env.current_qber:.6f}")
    print(f"Final sifted key length: {env.current_sifted_length}")
    print(f"Generated key: {env.current_bb84.sifted_key}\n")

    # try encrypting
    encryptor = QuantumEncryption(env.current_bb84.sifted_key)
    cipher = encryptor.encrypt(args.message)
    decrypted = encryptor.decrypt(cipher)

    print(f"Plaintext : {args.message}")
    print(f"Ciphertext: {cipher}")
    print(f"Decrypted : {decrypted}")


if __name__ == '__main__':
    main()
