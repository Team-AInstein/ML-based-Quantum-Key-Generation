from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from constants import *
import random


class colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'

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

def get_random_sequence_of_bases(size):
    """Generates a random sequence of Z and X bases."""
    bases = [random.choice([Z_BASE, X_BASE]) for _ in range(size)]
    return bases

def get_state(bit, base):
    """Determines the quantum state based on the bit and basis."""
    if bit == '0':
        return STATE_PLUS if base == X_BASE else STATE_0
    else:
        return STATE_MINUS if base == X_BASE else STATE_1

def print_protocol_details(alice_bits, alice_bases, bob_bases):
    """Prints a detailed, colored log of the BB84 base comparison without Eve."""
    alice_states = [get_state(bit, base) for bit, base in zip(alice_bits, alice_bases)]
    
    header_parts = [
        "Index".ljust(7), "Alice's Bit".ljust(12), "Alice's Basis".ljust(14),
        "Sent State".ljust(12), "Bob's Basis".ljust(13), "Bases Match?".ljust(14),
        "Resulting Bit"
    ]
    header = " | ".join(header_parts)
    print(header)
    print("-" * len(header))

    sifted_bits_count = 0
    for i in range(len(alice_bits)):
        match = (alice_bases[i] == bob_bases[i])
        
        state_text = alice_states[i]
        colored_state = f"{colors.BLUE}{state_text}{colors.ENDC}"
        padded_state = colored_state + ' ' * (12 - len(state_text))

        if match:
            match_text = "MATCH"
            colored_match = f"{colors.GREEN}{match_text}{colors.ENDC}"
            colored_result = f"{colors.YELLOW}{alice_bits[i]}{colors.ENDC}"
            sifted_bits_count += 1
        else:
            match_text = "MISMATCH"
            colored_match = f"{colors.RED}{match_text}{colors.ENDC}"
            colored_result = "(discarded)"
        
        padded_match = colored_match + ' ' * (14 - len(match_text))
        
        
        row_parts = [
            str(i).ljust(7),
            alice_bits[i].ljust(12),
            alice_bases[i].ljust(14),
            padded_state,
            bob_bases[i].ljust(13),
            padded_match,
            colored_result
        ]
        print(" | ".join(row_parts))

    print("-" * len(header))
    print(f"Total bits sifted (where bases matched): {sifted_bits_count}")

def print_protocol_details_with_eve(alice_bits, alice_bases, eve_bases, eve_bits, bob_bases, bob_bits):
    """Prints a detailed log of the BB84 exchange WITH Eve's actions."""
    header_parts = [
        "Idx".ljust(4), "Alice Bit/Basis".ljust(17), "State to Eve".ljust(13),
        "Eve Basis/Bit".ljust(15), "State to Bob".ljust(13), "Bob Basis/Bit".ljust(15),
        "Final Result"
    ]
    header = "| ".join(header_parts)
    print(header)
    print("-" * 120)

    for i in range(len(alice_bits)):
       
        index_str = str(i).ljust(4)
        alice_str = f'{alice_bits[i]} ({alice_bases[i]})'.ljust(17)

        state_to_eve_text = get_state(alice_bits[i], alice_bases[i])
        colored_s2e = f"{colors.BLUE}{state_to_eve_text}{colors.ENDC}"
        padded_s2e = colored_s2e + ' ' * (13 - len(state_to_eve_text))

        eve_text = f"{eve_bases[i]} -> {eve_bits[i]}"
        colored_eve = f"{colors.MAGENTA}{eve_text}{colors.ENDC}"
        padded_eve = colored_eve + ' ' * (15 - len(eve_text))

        state_to_bob_text = get_state(eve_bits[i], eve_bases[i])
        colored_s2b = f"{colors.BLUE}{state_to_bob_text}{colors.ENDC}"
        padded_s2b = colored_s2b + ' ' * (13 - len(state_to_bob_text))
        
        bob_text = f"{bob_bases[i]} -> {bob_bits[i]}"
        colored_bob = f"{colors.CYAN}{bob_text}{colors.ENDC}"
        padded_bob = colored_bob + ' ' * (15 - len(bob_text))

        if alice_bases[i] == bob_bases[i]:
            if alice_bits[i] == bob_bits[i]:
                final_result = f"{colors.GREEN}SECURE BIT ({alice_bits[i]}){colors.ENDC}"
            else:
                final_result = f"{colors.RED}ERROR! ({alice_bits[i]} vs {bob_bits[i]}){colors.ENDC}"
        else:
            final_result = "(Bases Mismatch)"
        
        
        row_parts = [
            index_str, alice_str, padded_s2e, padded_eve, padded_s2b, padded_bob, final_result
        ]
        print("| ".join(row_parts))
        
    print("-" * 120)


def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary_string):
    if len(binary_string) % 8 != 0:
        padding = 8 - (len(binary_string) % 8)
        binary_string = '0' * padding + binary_string
    chars = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

def xor_encrypt_decrypt(binary_input, binary_key):
    key_length = len(binary_key)
    if key_length == 0:
        raise ValueError("Encryption key cannot be empty.")
    return "".join([str(int(input_bit) ^ int(binary_key[i % key_length])) for i, input_bit in enumerate(binary_input)])