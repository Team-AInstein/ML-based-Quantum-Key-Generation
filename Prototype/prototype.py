import numpy as np
import os
# Importing standard Qiskit libraries
from qiskit import QuantumCircuit, transpile, Aer
from qiskit.providers.aer import AerSimulator
from qiskit import execute
from qiskit.quantum_info.operators import Operator
from qiskit.quantum_info import Statevector
from random import seed, randint

# Image processing libraries
from PIL import Image
from io import BytesIO
from bitstring import BitStream, BitArray

# --- 1. Define Parameters ---
n = 4 
num_of_bits = 448
bits_in_block = 8
num_of_qubits = 2 # 2-qubit QPP
num_of_perm_in_pad = 56 # 56 permutation matrices
pad_selection_key_size = 6 

# The secret key (truly random in practice)
# For the code to run, we generate a dummy 448-bit key here.
seed(42) # Fixed seed for reproducibility
secret_key = "".join([str(randint(0, 1)) for _ in range(448)])

# Break the secret key into blocks
secret_key_blocks = [secret_key[i:i+bits_in_block] for i in range(0, len(secret_key), bits_in_block)]

# --- 2. Fisher-Yates Shuffling Function ---
def randomize(arr, n):
    for i in range(n-1, 0, -1):
        j = randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

# --- 3. Create Permutation Pad ---
Permutation_Pad = []

for num_of_perm in range(num_of_perm_in_pad):
    my_array = []
    for num in range(n):
        my_array.append(num)
    
    array_of_n_num = my_array.copy()
    key_block = secret_key_blocks[num_of_perm]
    key_chunks = [key_block[i:i+num_of_qubits] for i in range(0, len(key_block), num_of_qubits)]
    
    len_of_array = len(my_array)
    shuffled_array = randomize(my_array, len_of_array)
    
    matrix_of_zeros = np.zeros((n, n), dtype=int)
    my_matrix = matrix_of_zeros
    
    for num in range(n):
        my_matrix[array_of_n_num[num]][shuffled_array[num]] = 1
        
    Permutation_Pad.append(Operator(my_matrix))

# Create an array used for dispatching
pad_selection_blocks = [secret_key[i:i+pad_selection_key_size] for i in range(0, len(secret_key), pad_selection_key_size)]

for num in range(len(pad_selection_blocks)):
    pad_selection_blocks[num] = int(pad_selection_blocks[num], 2) % num_of_perm_in_pad

# --- 4. Image Processing (Encryption Prep) ---
out = BytesIO()

# Ensure dummy image exists if original is missing
if not os.path.exists("epj.png"):
    print("Creating dummy epj.png...")
    img = Image.new('RGB', (50, 50), color = 'red')
    img.save('epj.png')

original_size = (0,0)
try:
    with Image.open("epj.png") as img:
        original_size = img.size
        img.save(out, format="png")
    
    image_in_bytes = out.getvalue()
    message = "".join([format(n, '08b') for n in image_in_bytes])
except FileNotFoundError:
    print("Error: 'epj.png' not found.")
    exit()

# XOR Randomization
key_for_xor_list = []
for x in range(len(message)):
    key_for_xor_list.append(secret_key[x % len(secret_key)])
key_for_xor = "".join(key_for_xor_list)

randomized_message = [str(int(message[i]) ^ int(key_for_xor[i])) for i in range(len(message))]
randomized_message = "".join(randomized_message)

chunk_size = num_of_qubits
message_chunks = [randomized_message[i:i+chunk_size] for i in range(0, len(randomized_message), chunk_size)]
list_of_ciphers = []

# --- 5. Encryption Process ---
qcomp = Aer.get_backend('aer_simulator')

print(f"Starting Encryption of {len(message_chunks)} chunks (Original Image)...")

for x in range(len(message_chunks)):
    # Progress bar
    if x % 100 == 0:
        print(f"Encrypting chunk {x}/{len(message_chunks)}...", end="\r")

    state_vector_str = message_chunks[x]
    
    # Padding if last chunk is small
    if len(state_vector_str) < num_of_qubits:
        state_vector_str = state_vector_str.ljust(num_of_qubits, '0')

    qc = QuantumCircuit(num_of_qubits, num_of_qubits)
    qc.initialize(Statevector.from_label(state_vector_str))
    qc.barrier()
    
    j = pad_selection_blocks[x % len(pad_selection_blocks)]
    qc.append(Permutation_Pad[j], range(num_of_qubits))
    qc.barrier()
    
    qc.measure([0, 1], [0, 1])
    
    # Optimization level 0 for speed on simulator
    qc = transpile(qc, backend=qcomp, optimization_level=0)
    
    # 1 shot is sufficient for simulator
    job = execute(qc, backend=qcomp, shots=1)
    result = job.result()
    counts = result.get_counts()
    
    list_of_ciphers.append(list(counts.keys())[0])

print(f"\nEncryption Complete. Processing outputs...")

# --- 6. Save Encrypted Outputs ---

# Combine cipher bits
full_cipher_str = "".join(list_of_ciphers)

# Pad to multiple of 8
padding = 8 - (len(full_cipher_str) % 8)
if padding != 8:
    full_cipher_str += "0" * padding

# Convert to bytes
bytes_cipher = bytes(int(full_cipher_str[i:i+8], 2) for i in range(0, len(full_cipher_str), 8))

# Save Binary File
with open("ciphertext_to_send.bin", "wb") as file_cipher:
    file_cipher.write(bytes_cipher)
print("Saved binary: ciphertext_to_send.bin")

# --- VISUALIZE ENCRYPTED IMAGE ---
# We attempt to reconstruct an image from the raw encrypted bytes to show the noise.
# Note: The file size might change slightly due to headers, so we calculate dimension roughly or just save raw.
try:
    # We try to use the original dimensions. 
    # If bytes don't match exactly (due to PNG compression vs raw bytes), we just save the stream.
    # The paper mentions converting "ciphertext binary file converted to raw pixels".
    
    # Create an image from the raw encrypted bytes (Visual Noise)
    # We use the same buffer size as the original image data if possible, or just square.
    import math
    num_pixels = len(bytes_cipher) // 3 # Assuming RGB
    side = int(math.sqrt(num_pixels))
    
    # Creates a raw visualization of the ciphertext
    img_encrypted = Image.frombytes('RGB', (side, side), bytes_cipher[:side*side*3])
    img_encrypted.save("encrypted_visual.png")
    print("Saved visual: encrypted_visual.png (Check this to see the encrypted noise)")
except Exception as e:
    print(f"Could not generate visual representation: {e}")


# --- 7. Decryption Process ---
print("Starting Decryption...")

Inverse_Permutation_Pad = []
for op in Permutation_Pad:
    Inverse_Permutation_Pad.append(op.adjoint())

# Read ciphertext
with open("ciphertext_to_send.bin", "rb") as f:
    a = BitArray(f.read())
ciphertext = a.bin

# Remove padding if added (logic simplified here, assumes perfect block match for demo)
cipher_chunks = [ciphertext[i:i+chunk_size] for i in range(0, len(ciphertext), chunk_size)]
# Truncate to match original message length if padding made it longer
cipher_chunks = cipher_chunks[:len(message_chunks)]

list_of_messages = []

for x in range(len(cipher_chunks)):
    if x % 100 == 0:
        print(f"Decrypting chunk {x}/{len(cipher_chunks)}...", end="\r")

    qc_decrypt = QuantumCircuit(num_of_qubits, num_of_qubits)
    qc_decrypt.initialize(Statevector.from_label(cipher_chunks[x]))
    qc_decrypt.barrier()
    
    j = pad_selection_blocks[x % len(pad_selection_blocks)]
    qc_decrypt.append(Inverse_Permutation_Pad[j], range(num_of_qubits))
    qc_decrypt.barrier()
    
    qc_decrypt.measure([0, 1], [0, 1])
    
    qc_decrypt = transpile(qc_decrypt, backend=qcomp, optimization_level=0)
    job = execute(qc_decrypt, backend=qcomp, shots=1)
    result = job.result()
    counts = result.get_counts()
    
    most_freq = list(counts.keys())[0]
    list_of_messages.append(most_freq)

print("\nDecryption Complete.")
randomized_decrypted_cipher = "".join(list_of_messages)

# De-randomize (XOR back)
decrypted_message_list = [str(int(randomized_decrypted_cipher[i]) ^ int(key_for_xor[i])) 
                          for i in range(len(randomized_decrypted_cipher))]
decrypted_message = "".join(decrypted_message_list)

# Convert to bytes
decrypted_bytes = [int(decrypted_message[i:i+8], 2) for i in range(0, len(decrypted_message), 8)]

# Save decrypted image
with open('decrypted_pic.png', 'wb') as f:
    f.write(bytes(decrypted_bytes))

print("Decryption complete. Saved to 'decrypted_pic.png'.")