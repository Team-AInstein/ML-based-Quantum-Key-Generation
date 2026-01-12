# import json
# import random
# from constants import QBER_TEST_FRACTION, QBER_THRESHOLD
# from helpers import get_random_sequence_of_bits, get_random_sequence_of_bases, print_protocol_details

# KEY_LENGTH = 128 # The length of the initial random bit string

# def generate_key_for_sender(public_channel_file):
#     """Simulates the sender's (Alice) side of the BB84 protocol."""
#     alice_bits = get_random_sequence_of_bits(KEY_LENGTH)
#     alice_bases = get_random_sequence_of_bases(KEY_LENGTH)
#     bob_bases = get_random_sequence_of_bases(KEY_LENGTH)

#     print(f"   - Sender (Alice) generated {KEY_LENGTH} random bits and bases.")
#     print(f"   - Receiver (Bob) generated {KEY_LENGTH} random bases (simulated).")

#     # Display the full protocol details from the sender's perspective
#     print_protocol_details(alice_bits, alice_bases, bob_bases)

#     # Save the public information needed for the receiver to replicate the key
#     public_data = {
#         'alice_bases': alice_bases,
#         'bob_bases': bob_bases,
#         'simulated_alice_bits': alice_bits
#     }
#     with open(public_channel_file, 'w') as f:
#         json.dump(public_data, f, indent=4)
#     print(f"\n   - Public bases published to '{public_channel_file}'.")

#     # Sift the key based on the matching bases
#     sifted_key = ""
#     for i in range(KEY_LENGTH):
#         if alice_bases[i] == bob_bases[i]:
#             sifted_key += alice_bits[i]
            
#     return sifted_key

# def replicate_key_for_receiver(public_channel_file):
#     """Simulates the receiver's (Bob) side of the BB84 protocol."""
#     with open(public_channel_file, 'r') as f:
#         public_data = json.load(f)
        
#     alice_bases = public_data['alice_bases']
#     bob_bases = public_data['bob_bases']
#     alice_bits = public_data['simulated_alice_bits']
#     print(f"   - Receiver (Bob) read public bases from '{public_channel_file}'.")

#     # Display the full protocol details from the receiver's perspective
#     # The result will be identical to the sender's view, proving the concept.
#     print_protocol_details(alice_bits, alice_bases, bob_bases)

#     # Sift the key based on the public information
#     sifted_key = ""
#     for i in range(len(alice_bases)):
#         if alice_bases[i] == bob_bases[i]:
#             sifted_key += alice_bits[i]
            
           
#     return sifted_key


# import random

# QBER_TEST_FRACTION = 0.2  # 20% bits revealed

# def calculate_qber(alice_sifted_key, bob_sifted_key):
#     assert len(alice_sifted_key) == len(bob_sifted_key)

#     key_len = len(alice_sifted_key)
#     test_size = max(1, int(key_len * QBER_TEST_FRACTION))

#     test_indices = random.sample(range(key_len), test_size)

#     errors = 0
#     for i in test_indices:
#         if alice_sifted_key[i] != bob_sifted_key[i]:
#             errors += 1

#     qber = errors / test_size

#     # remove revealed bits
#     final_key = "".join(
#         alice_sifted_key[i]
#         for i in range(key_len)
#         if i not in test_indices
#     )

#     return qber, final_key



import json
import random
from helpers import (
    get_random_sequence_of_bits,
    get_random_sequence_of_bases,
    print_protocol_details
)

# ============================
# Alice (Sender)
# ============================
def generate_key_for_sender(
    public_channel_file,
    key_length=128,
    z_bias=0.5,
    verbose=False
):
    alice_bits = get_random_sequence_of_bits(key_length)
    alice_bases = get_random_sequence_of_bases(key_length, z_bias)
    bob_bases   = get_random_sequence_of_bases(key_length, z_bias)

    if verbose:
        print_protocol_details(alice_bits, alice_bases, bob_bases)

    public_data = {
        "alice_bases": alice_bases,
        "bob_bases": bob_bases,
        "simulated_alice_bits": alice_bits
    }

    with open(public_channel_file, "w") as f:
        json.dump(public_data, f, indent=4)

    sifted_key = "".join(
        alice_bits[i]
        for i in range(key_length)
        if alice_bases[i] == bob_bases[i]
    )

    return sifted_key


# ============================
# Bob (Receiver)
# ============================
def replicate_key_for_receiver(public_channel_file, verbose=False):
    with open(public_channel_file, "r") as f:
        public_data = json.load(f)

    alice_bits  = public_data["simulated_alice_bits"]
    alice_bases = public_data["alice_bases"]
    bob_bases   = public_data["bob_bases"]

    if verbose:
        print_protocol_details(alice_bits, alice_bases, bob_bases)

    sifted_key = "".join(
        alice_bits[i]
        for i in range(len(alice_bits))
        if alice_bases[i] == bob_bases[i]
    )

    return sifted_key


# ============================
# QBER Calculation
# ============================
def calculate_qber(
    alice_sifted_key,
    bob_sifted_key,
    test_fraction=0.2
):
    assert len(alice_sifted_key) == len(bob_sifted_key)

    key_len = len(alice_sifted_key)
    test_size = max(1, int(key_len * test_fraction))

    test_indices = random.sample(range(key_len), test_size)

    errors = sum(
        1
        for i in test_indices
        if alice_sifted_key[i] != bob_sifted_key[i]
    )

    qber = errors / test_size

    final_key = "".join(
        alice_sifted_key[i]
        for i in range(key_len)
        if i not in test_indices
    )

    return qber, final_key
