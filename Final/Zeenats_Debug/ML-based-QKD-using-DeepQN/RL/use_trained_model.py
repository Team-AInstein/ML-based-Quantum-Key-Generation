"""
Load a trained DQN model, run the environment to produce a secure key,
and optionally encrypt a user-provided message using that key.

Usage:
    python use_trained_model.py --model path/to/dqn_final.pt --message "Hello"

If no message is provided, the script will simply generate the key and
print it to the console (and save to file).
"""

import argparse
import os
from pathlib import Path

import sys, os
# make sure the workspace root is on the path so frontend modules can be imported
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from train_integrated import QKDTrainer
# frontend folder is sibling to this RL directory
from frontend.quantum_encryption import MessageCrypto


def main():
    parser = argparse.ArgumentParser(description="Use trained DQN model to generate key and encrypt a message")
    parser.add_argument('--model', type=str, required=True,
                        help='Path to saved DQN model file (e.g. dqn_final.pt)')
    parser.add_argument('--message', type=str, default=None,
                        help='Optional plaintext message to encrypt with generated key')
    parser.add_argument('--key-out', type=str, default='generated_key_from_model.txt',
                        help='Path where the generated key will be written')

    args = parser.parse_args()

    # ensure model file exists
    if not os.path.exists(args.model):
        raise FileNotFoundError(f"Model file not found: {args.model}")

    # create a trainer with the same parameters used during training
    trainer = QKDTrainer()

    # load the trained weights into the agent
    trainer.agent.load(args.model)
    print(f"Loaded trained model from {args.model}")

    # run a single demonstration to get a key
    print("Running one secured episode to generate key...")
    final_key, metadata = trainer.demonstrate_with_privacy_amplification()

    if final_key:
        with open(args.key_out, 'w') as f:
            f.write(final_key)
        print(f"Final key ({len(final_key)} bits) saved to {args.key_out}")
    else:
        print("No key was generated (sifted key may have been empty)")

    # if the user wants to encrypt a message
    if args.message:
        crypto = MessageCrypto(final_key)
        encrypted = crypto.encrypt_message('agent', args.message)
        print(f"\nEncrypted message payload (base64): {encrypted['encrypted']}")
        # show decryption to verify
        decrypted = crypto.decrypt_message(encrypted)
        print(f"Decrypted back: {decrypted['message']}")


if __name__ == '__main__':
    main()
