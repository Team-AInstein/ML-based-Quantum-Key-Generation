import json
import random
from helpers import (get_random_sequence_of_bits, get_random_sequence_of_bases,
                     print_protocol_details, print_protocol_details_with_eve)

KEY_LENGTH = 128 

def generate_key_for_sender(public_channel_file):
    """Simulates the sender's (Alice) side of the BB84 protocol without Eve."""
    alice_bits = get_random_sequence_of_bits(KEY_LENGTH)
    alice_bases = get_random_sequence_of_bases(KEY_LENGTH)
    bob_bases = get_random_sequence_of_bases(KEY_LENGTH)

    print(f"   - Sender (Alice) generated {KEY_LENGTH} random bits and bases.")
    print(f"   - Receiver (Bob) generated {KEY_LENGTH} random bases (simulated).")

    print_protocol_details(alice_bits, alice_bases, bob_bases)

    public_data = {'alice_bases': alice_bases, 'bob_bases': bob_bases, 'simulated_alice_bits': alice_bits}
    with open(public_channel_file, 'w') as f:
        json.dump(public_data, f, indent=4)
    print(f"\n   - Public bases published to '{public_channel_file}'.")

    sifted_key = "".join([alice_bits[i] for i in range(KEY_LENGTH) if alice_bases[i] == bob_bases[i]])
    return sifted_key

def generate_key_with_eavesdropper(public_channel_file):
    """
    Simulates the BB84 protocol with an intercept-resend attack from Eve.
    Returns both Alice's and Bob's potentially different sifted keys.
    """
    
    alice_bits = get_random_sequence_of_bits(KEY_LENGTH)
    alice_bases = get_random_sequence_of_bases(KEY_LENGTH)
    print(f"   - Alice generated {KEY_LENGTH} random bits and bases.")

    
    eve_bases = get_random_sequence_of_bases(KEY_LENGTH)
    print(f"   - Eve generated {KEY_LENGTH} random bases for interception.")

   
    bob_bases = get_random_sequence_of_bases(KEY_LENGTH)
    print(f"   - Bob generated {KEY_LENGTH} random bases for receiving.")

   
    eve_measured_bits = [
        alice_bits[i] if alice_bases[i] == eve_bases[i] else str(random.randint(0, 1))
        for i in range(KEY_LENGTH)
    ]

   
    bob_measured_bits = [
        eve_measured_bits[i] if eve_bases[i] == bob_bases[i] else str(random.randint(0, 1))
        for i in range(KEY_LENGTH)
    ]

    
    print_protocol_details_with_eve(alice_bits, alice_bases, eve_bases, eve_measured_bits, bob_bases, bob_measured_bits)

    
    public_data = {'alice_bases': alice_bases, 'bob_bases': bob_bases, 'simulated_alice_bits': alice_bits}
    with open(public_channel_file, 'w') as f:
        json.dump(public_data, f, indent=4)
    print(f"\n   - Alice and Bob publish their bases to '{public_channel_file}'.")

    # Sifting process
   
    alice_sifted_key = "".join([alice_bits[i] for i in range(KEY_LENGTH) if alice_bases[i] == bob_bases[i]])
    
    bob_sifted_key = "".join([bob_measured_bits[i] for i in range(KEY_LENGTH) if alice_bases[i] == bob_bases[i]])

    return alice_sifted_key, bob_sifted_key


def replicate_key_for_receiver(public_channel_file):
    """Simulates the receiver's (Bob) side of the BB84 protocol."""
    with open(public_channel_file, 'r') as f:
        public_data = json.load(f)
        
    alice_bases = public_data['alice_bases']
    bob_bases = public_data['bob_bases']
    alice_bits = public_data['simulated_alice_bits']
    print(f"   - Receiver (Bob) read public bases from '{public_channel_file}'.")

    print_protocol_details(alice_bits, alice_bases, bob_bases)

    sifted_key = "".join([alice_bits[i] for i in range(len(alice_bases)) if alice_bases[i] == bob_bases[i]])
    return sifted_key