import numpy as np
from qiskit import QuantumCircuit, transpile, Aer
from qiskit.providers.aer import AerSimulator
from qiskit.execute_function import execute
from qiskit.quantum_info.operators import Operator
from qiskit.quantum_info import Statevector
from random import seed, randint

# --- 1. Configuration Data (From Table 1 in the Paper) ---
QPP_CONFIG = {
    2: {'gates': 56, 'dispatch_bits': 6}, 
    3: {'gates': 17, 'dispatch_bits': 5}, 
    4: {'gates': 6,  'dispatch_bits': 3}, 
    5: {'gates': 3,  'dispatch_bits': 2}  
}

# --- 2. User Input ---
print("--- QUANTUM PERMUTATION PAD ENCRYPTION SYSTEM ---")
while True:
    try:
        user_choice = int(input("Select encryption security level (2, 3, 4, or 5 qubits): "))
        if user_choice in QPP_CONFIG:
            num_of_qubits = user_choice
            break
        else:
            print("Invalid choice. Please enter 2, 3, 4, or 5.")
    except ValueError:
        print("Please enter a number.")

plaintext_input = input("\nEnter the text message to encrypt: ")

# --- 3. Setup Parameters ---
config = QPP_CONFIG[num_of_qubits]
num_of_perm_in_pad = config['gates']
pad_selection_key_size = config['dispatch_bits']
dim = 2 ** num_of_qubits 
bits_in_block = 8 

print(f"\n[BACKEND] INITIALIZING {num_of_qubits}-QUBIT SYSTEM...")
print(f"-> Matrix Dimension: {dim}x{dim}")
print(f"-> Permutation Gates in Pad: {num_of_perm_in_pad}")

# Generate Secret Key
seed(42) 
secret_key_len = 2048 
secret_key = "".join([str(randint(0, 1)) for _ in range(secret_key_len)])
print(f"-> Generated Secret Key (Truncated): {secret_key[:20]}...")

# --- 4. Build Permutation Pad ---
print("-> Building Quantum Permutation Pad...")

def randomize(arr, n):
    for i in range(n-1, 0, -1):
        j = randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

Permutation_Pad = []
for num_of_perm in range(num_of_perm_in_pad):
    my_array = list(range(dim))
    shuffled_array = randomize(my_array, dim)
    matrix_of_zeros = np.zeros((dim, dim), dtype=int)
    for k in range(dim):
        matrix_of_zeros[k][shuffled_array[k]] = 1
    Permutation_Pad.append(Operator(matrix_of_zeros))

# Dispatching Array Logic
pad_selection_blocks = [secret_key[i:i+pad_selection_key_size] for i in range(0, len(secret_key), pad_selection_key_size)]
for num in range(len(pad_selection_blocks)):
    pad_selection_blocks[num] = int(pad_selection_blocks[num], 2) % num_of_perm_in_pad

# --- 5. Input Processing ---
print("\n[BACKEND] PROCESSING INPUT...")
plaintext_bytes = plaintext_input.encode('utf-8')
message = "".join([format(byte, '08b') for byte in plaintext_bytes])
print(f"-> Original Bits:      {message}")

# XOR Randomization
key_for_xor_list = [secret_key[x % len(secret_key)] for x in range(len(message))]
key_for_xor = "".join(key_for_xor_list)
randomized_message = "".join([str(int(message[i]) ^ int(key_for_xor[i])) for i in range(len(message))])

print(f"-> Key Stream Used:    {key_for_xor}")
print(f"-> Randomized (XOR):   {randomized_message}")

# Chunking
chunk_size = num_of_qubits
message_chunks = [randomized_message[i:i+chunk_size] for i in range(0, len(randomized_message), chunk_size)]
print(f"-> Total Chunks: {len(message_chunks)} (Processing as {num_of_qubits}-bit blocks)")

# --- 6. Quantum Encryption ---
qcomp = Aer.get_backend('aer_simulator')
list_of_ciphers = []

print(f"\n[BACKEND] QUANTUM ENCRYPTION STARTED...")
for x in range(len(message_chunks)):
    input_bits = message_chunks[x]
    
    if len(input_bits) < num_of_qubits:
        input_bits = input_bits.ljust(num_of_qubits, '0')

    gate_index = pad_selection_blocks[x % len(pad_selection_blocks)]
    
    # Build Circuit
    qc = QuantumCircuit(num_of_qubits, num_of_qubits)
    qc.initialize(Statevector.from_label(input_bits)) 
    qc.barrier()
    qc.append(Permutation_Pad[gate_index], range(num_of_qubits)) 
    qc.barrier()
    qc.measure(range(num_of_qubits), range(num_of_qubits)) 
    
    # Execute
    qc = transpile(qc, backend=qcomp, optimization_level=0)
    job = execute(qc, backend=qcomp, shots=1)
    result = job.result().get_counts()
    measured_output = list(result.keys())[0]
    
    list_of_ciphers.append(measured_output)
    
    # Print process for first 5 chunks
    if x < 5:
        print(f"   Chunk {x}: Input |{input_bits}> -> Permutation Gate[{gate_index}] -> Measured |{measured_output}>")
    elif x == 5:
        print("   ... (Logging suppressed for remaining chunks to save space) ...")

    # DRAW CIRCUIT (First Chunk)
    if x == 0:
        print("\n   [VISUALIZATION] Quantum Circuit for Chunk 0:")
        print(qc.draw(output='text'))
        print("   (Note: 'unitary' block is the Permutation Gate)\n")

print(f"Encryption Complete.")

# --- 7. Quantum Decryption ---
print(f"\n[BACKEND] QUANTUM DECRYPTION STARTED...")
cipher_chunks = list_of_ciphers
Inverse_Pad = [op.adjoint() for op in Permutation_Pad]
list_of_messages = []

for x in range(len(cipher_chunks)):
    input_cipher = cipher_chunks[x]
    gate_index = pad_selection_blocks[x % len(pad_selection_blocks)]
    
    qc_dec = QuantumCircuit(num_of_qubits, num_of_qubits)
    qc_dec.initialize(Statevector.from_label(input_cipher))
    qc_dec.barrier()
    qc_dec.append(Inverse_Pad[gate_index], range(num_of_qubits)) 
    qc_dec.barrier()
    qc_dec.measure(range(num_of_qubits), range(num_of_qubits))
    
    qc_dec = transpile(qc_dec, backend=qcomp, optimization_level=0)
    job = execute(qc_dec, backend=qcomp, shots=1)
    result = job.result().get_counts()
    decrypted_chunk = list(result.keys())[0]
    
    list_of_messages.append(decrypted_chunk)

    if x < 5:
        print(f"   Chunk {x}: Cipher |{input_cipher}> -> Inverse Gate[{gate_index}] -> Decrypted |{decrypted_chunk}>")

print(f"Decryption Complete.")

# --- 8. Reconstruction ---
print("\n[BACKEND] RECONSTRUCTION...")
reconstructed_bits = "".join(list_of_messages)
reconstructed_bits = reconstructed_bits[:len(randomized_message)] # Remove padding

# XOR De-randomization
final_bits_list = [str(int(reconstructed_bits[i]) ^ int(key_for_xor[i])) for i in range(len(reconstructed_bits))]
final_bits = "".join(final_bits_list)
print(f"-> Reconstructed Bits: {final_bits}")

# Convert back to text
try:
    chars = []
    for i in range(0, len(final_bits), 8):
        byte = final_bits[i:i+8]
        chars.append(chr(int(byte, 2)))
    final_text = "".join(chars)
    
    print(f"\nFinal Result: '{final_text}'")
    if final_text == plaintext_input:
        print("✅ SUCCESS: The system works perfectly.")
    else:
        print("❌ FAILURE: Mismatch detected.")
except Exception as e:
    print(f"Error reconstructing text: {e}")