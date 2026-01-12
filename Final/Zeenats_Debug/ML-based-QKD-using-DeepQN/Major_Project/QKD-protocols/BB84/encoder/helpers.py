from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from constants import *
import random

# ANSI color codes for better terminal output
class colors:
    GREEN = '\033[92m'  # For matches
    RED = '\033[91m'    # For mismatches
    BLUE = '\033[94m'   # For states
    YELLOW = '\033[93m' # For key bits
    ENDC = '\033[0m'    # End color

def get_random_sequence_of_bits(size):
    """Generates a random sequence of bits using a quantum simulator."""
    simulator = AerSimulator()
    circuit = QuantumCircuit(size, size)
    circuit.h(range(size))
    circuit.measure(range(size), range(size))
    
    compiled_circuit = transpile(circuit, simulator)
    job = simulator.run(compiled_circuit, shots=1, memory=True)
    result = job.result()
    str_sequence = result.get_memory(compiled_circuit)[0]
    return list(str_sequence)
def get_random_sequence_of_bases(size, z_bias=0.5):
    """
    Generates a random sequence of bases with controllable bias.
    z_bias = probability of choosing Z basis
    """
    bases = [
        Z_BASE if random.random() < z_bias else X_BASE
        for _ in range(size)
    ]
    return bases


def get_state(bit, base):
    """Determines the quantum state based on the bit and basis."""
    if bit == BIT_0:
        return STATE_PLUS if base == X_BASE else STATE_0
    else: # BIT_1
        return STATE_MINUS if base == X_BASE else STATE_1

def print_protocol_details(alice_bits, alice_bases, bob_bases):
    """Prints a detailed, colored log of the BB84 base comparison."""
    
    alice_states = [get_state(bit, base) for bit, base in zip(alice_bits, alice_bases)]

    # Define column widths
    w_index, w_bit, w_basis, w_state, w_match = 7, 12, 14, 12, 14

    # --- Print Header ---
    header_parts = [
        "Index".ljust(w_index),
        "Alice's Bit".ljust(w_bit),
        "Alice's Basis".ljust(w_basis),
        "Sent State".ljust(w_state),
        "Bob's Basis".ljust(w_basis),
        "Bases Match?".ljust(w_match),
        "Resulting Bit"
    ]
    header = " | ".join(header_parts)
    print(header)
    print("-" * len(header))

    sifted_bits_count = 0
    for i in range(len(alice_bits)):
        match = (alice_bases[i] == bob_bases[i])
        
        # Determine colored strings for this row
        if match:
            match_text = "MATCH"
            match_str = f"{colors.GREEN}{match_text}{colors.ENDC}"
            result_bit = f"{colors.YELLOW}{alice_bits[i]}{colors.ENDC}"
            sifted_bits_count += 1
        else:
            match_text = "MISMATCH"
            match_str = f"{colors.RED}{match_text}{colors.ENDC}"
            result_bit = "(discarded)"
        
        # Add padding to the colored string manually
        padded_match_str = match_str + " " * (w_match - len(match_text))
        
        # --- Build and Print Row using a list and join (more robust) ---
        row_parts = [
            str(i).ljust(w_index),
            alice_bits[i].ljust(w_bit),
            alice_bases[i].ljust(w_basis),
            (f"{colors.BLUE}{alice_states[i]}{colors.ENDC}").ljust(w_state + len(colors.BLUE) + len(colors.ENDC)),
            bob_bases[i].ljust(w_basis),
            padded_match_str,
            result_bit
        ]
        print(" | ".join(row_parts))
    
    print("-" * len(header))
    print(f"Total bits sifted (where bases matched): {sifted_bits_count}")

# --- Encryption Helper Functions (unchanged) ---

def text_to_binary(text):
    """Converts a string of text to a binary string."""
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary_string):
    """Converts a binary string back to text."""
    if len(binary_string) % 8 != 0:
        padding = 8 - (len(binary_string) % 8)
        binary_string = '0' * padding + binary_string
    chars = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    text = ''.join(chr(int(char, 2)) for char in chars)
    return text

def xor_encrypt_decrypt(binary_input, binary_key):
    """Encrypts or decrypts a binary string using a binary key with XOR."""
    key_length = len(binary_key)
    if key_length == 0:
        raise ValueError("Encryption key cannot be empty.")
    result = []
    for i in range(len(binary_input)):
        input_bit = int(binary_input[i])
        key_bit = int(binary_key[i % key_length])
        xor_result = input_bit ^ key_bit
        result.append(str(xor_result))
    return "".join(result)