import os
import bb84_engine
from constants import QBER_THRESHOLD
from helpers import text_to_binary, binary_to_text, xor_encrypt_decrypt

PUBLIC_CHANNEL_FILE = "public_channel.json"
MESSAGE_FILE = "encrypted_message.txt"
FINAL_KEY_FILE = "final_key.txt"


# ===================== MENU =====================
def display_menu():
    print("\n" + "=" * 40)
    print("      BB84 Secure Messenger")
    print("=" * 40)
    print("1. Send a secure message (Alice)")
    print("2. Receive a secure message (Bob)")
    print("3. Exit")
    print("-" * 40)


# ===================== SENDER (ALICE) =====================
def sender_workflow():
    print("\n--- SENDER (ALICE) ---")

    message = input("Enter message to encrypt: ")

    print("\n[1] Running BB84 protocol (Alice)...")
    alice_sifted_key = bb84_engine.generate_key_for_sender(PUBLIC_CHANNEL_FILE)

    if not alice_sifted_key:
        print("❌ Key generation failed.")
        return

    print(f"✔ Alice sifted key length: {len(alice_sifted_key)} bits")

    # 🔐 Privacy amplification (simulation)
    qber, final_key = bb84_engine.calculate_qber(
        alice_sifted_key,
        alice_sifted_key
    )

    print(f"✔ QBER: {qber * 100:.2f}%")

    if qber > QBER_THRESHOLD:
        print("❌ QBER too high. Abort.")
        return

    print("✅ Secure key established.")

    # Save final key so Bob uses THE SAME ONE
    with open(FINAL_KEY_FILE, "w") as f:
        f.write(final_key)

    # ===================== ENCRYPT =====================
    binary_message = text_to_binary(message)

    usable_length = min(len(binary_message), len(final_key))
    usable_length = (usable_length // 8) * 8  # 🔑 byte alignment

    binary_message = binary_message[:usable_length]
    encryption_key = final_key[:usable_length]

    encrypted_binary = xor_encrypt_decrypt(binary_message, encryption_key)

    with open(MESSAGE_FILE, "w") as f:
        f.write(encrypted_binary)

    print("✔ Message encrypted and sent securely.")
    print("✔ Ask Bob to run option 2.\n")


# ===================== RECEIVER (BOB) =====================
def receiver_workflow():
    print("\n--- RECEIVER (BOB) ---")

    if not os.path.exists(PUBLIC_CHANNEL_FILE):
        print("❌ Public channel file not found.")
        return

    if not os.path.exists(FINAL_KEY_FILE):
        print("❌ Final key not found. Ask Alice to send message first.")
        return

    print("\n[1] Replicating sifted key (Bob)...")
    bob_sifted_key = bb84_engine.replicate_key_for_receiver(PUBLIC_CHANNEL_FILE)

    if not bob_sifted_key:
        print("❌ Key replication failed.")
        return

    print(f"✔ Bob sifted key length: {len(bob_sifted_key)} bits")

    # Bob loads SAME final key (no regeneration!)
    with open(FINAL_KEY_FILE, "r") as f:
        final_key = f.read()

    print(f"✔ Final secure key length: {len(final_key)} bits")

    # ===================== DECRYPT =====================
    print("\n[2] Decrypting message...")

    with open(MESSAGE_FILE, "r") as f:
        encrypted_binary = f.read()

    usable_length = min(len(encrypted_binary), len(final_key))
    usable_length = (usable_length // 8) * 8

    encrypted_binary = encrypted_binary[:usable_length]
    decryption_key = final_key[:usable_length]

    decrypted_binary = xor_encrypt_decrypt(encrypted_binary, decryption_key)
    decrypted_message = binary_to_text(decrypted_binary)

    print("\n✅ SUCCESS: Message decrypted!")
    print(f"Decoded Message: {decrypted_message}")


# ===================== MAIN =====================
def main():
    while True:
        display_menu()
        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            sender_workflow()
        elif choice == '2':
            receiver_workflow()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
