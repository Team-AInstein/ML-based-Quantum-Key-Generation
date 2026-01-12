import os
import bb84_engine
from helpers import text_to_binary, binary_to_text, xor_encrypt_decrypt, colors

PUBLIC_CHANNEL_FILE = "public_channel.json"
MESSAGE_FILE = "encrypted_message.txt"

def display_menu():
    """Prints the main menu."""
    print("\n" + "="*50)
    print("              BB84 Secure Messenger")
    print("="*50)
    print("1. Send a secure message (No Eavesdropper)")
    print(f"2. {colors.RED}Send a message (Eavesdropper is PRESENT){colors.ENDC}")
    print("3. Receive a secure message (Decode)")
    print("4. Exit")
    print("-"*50)

def sender_workflow(with_eve=False):
    """Handles the process of encoding and sending a message."""
    if with_eve:
        print("\n--- SENDER (ALICE) --- [EVE IS LISTENING] ---")
    else:
        print("\n--- SENDER (ALICE) --- [SECURE CHANNEL] ---")

    message = input("Enter the message you want to send: ")

    if with_eve:
        print("\nStep 1: Running BB84 Protocol with EVE's INTERFERENCE. Details below:")
        alice_sifted_key, bob_sifted_key = bb84_engine.generate_key_with_eavesdropper(PUBLIC_CHANNEL_FILE)
    else:
        print("\nStep 1: Running BB84 Protocol to establish a secure key. Details below:")
        alice_sifted_key = bb84_engine.generate_key_for_sender(PUBLIC_CHANNEL_FILE)
        bob_sifted_key = alice_sifted_key # In a secure channel, their keys are identical.

    if not alice_sifted_key:
        print("\nKey generation failed. Aborting.")
        return

    print(f"\nSUCCESS: Key sifting complete.")
    print(f"  - Alice's Final Key ({len(alice_sifted_key)} bits): {alice_sifted_key}")
    if with_eve:
        print(f"  - Bob's Final Key   ({len(bob_sifted_key)} bits): {bob_sifted_key}")
        # Compare the keys to explicitly show Eve's impact
        if alice_sifted_key != bob_sifted_key:
            print(f"\n{colors.RED}!! SECURITY ALERT !!{colors.ENDC}")
            print("Alice's and Bob's keys DO NOT MATCH. An eavesdropper was detected!")
            print("Protocol would be aborted in a real-world scenario.")
        else:
            print(f"\n{colors.GREEN}Keys match. Eve was not detected (by luck).{colors.ENDC}")


    print("\nStep 2: Encrypting message with ALICE's secure key...")
    binary_message = text_to_binary(message)
    encrypted_binary = xor_encrypt_decrypt(binary_message, alice_sifted_key)

    with open(MESSAGE_FILE, 'w') as f:
        f.write(encrypted_binary)

    print("SUCCESS: Message encrypted.")
    print(f"Final Ciphertext (saved to file): {encrypted_binary}")
    print(f"\nThe receiver can now run option 3 to decode.")


def receiver_workflow():
    """Handles the process of decoding a received message."""
    print("\n--- RECEIVER (BOB) ---")

    if not os.path.exists(PUBLIC_CHANNEL_FILE) or not os.path.exists(MESSAGE_FILE):
        print("\nERROR: Cannot find required files. Run a sender option first.")
        return

    print("\nStep 1: Replicating secure key using public data. Details below:")
    sifted_key = bb84_engine.replicate_key_for_receiver(PUBLIC_CHANNEL_FILE)

    if not sifted_key:
        print("\nKey replication failed. Aborting.")
        return
        
    print(f"\nSUCCESS: Secure key replicated through sifting.")
    print(f"Final Replicated Key ({len(sifted_key)} bits): {sifted_key}")

    print("\nStep 2: Decrypting message with the replicated key...")
    with open(MESSAGE_FILE, 'r') as f:
        encrypted_binary = f.read()
    
    print(f"Received Ciphertext (from file): {encrypted_binary}")

    decrypted_binary = xor_encrypt_decrypt(encrypted_binary, sifted_key)
    decrypted_message = binary_to_text(decrypted_binary)

    print("\nSUCCESS: Message decrypted!")
    print(f"Decoded Message: {colors.YELLOW}{decrypted_message}{colors.ENDC}")


def main():
    while True:
        display_menu()
        choice = input("Enter your choice (1-4): ")
        if choice == '1':
            sender_workflow(with_eve=False)
        elif choice == '2':
            sender_workflow(with_eve=True)
        elif choice == '3':
            receiver_workflow()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()