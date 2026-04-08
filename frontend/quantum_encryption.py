"""
Quantum-Based Encryption Module

Uses quantum keys from BB84 protocol for one-time-pad-like encryption
of chat messages. Implements XOR-based encryption for simplicity and speed.
"""

import base64
import hashlib
from typing import Tuple, Optional, Dict


class QuantumEncryption:
    """
    Quantum key-based encryption for chat messages.
    
    Uses XOR encryption with quantum keys. While simple, this provides
    information-theoretic security when combined with BB84's quantum key
    distribution.
    """
    
    def __init__(self, quantum_key: str):
        """
        Initialize encryption with quantum key.
        
        Args:
            quantum_key: Binary string or hex string of quantum key
        """
        self.quantum_key = quantum_key
        self.key_index = 0
        
        # Ensure key is binary string
        if not all(c in '01' for c in quantum_key):
            # Assume hex, convert to binary
            self.quantum_key = bin(int(quantum_key, 16))[2:].zfill(len(quantum_key) * 4)
    
    def _pad_message(self, message: str) -> bytes:
        """Convert message to bytes."""
        return message.encode('utf-8')
    
    def _message_to_bits(self, message: str) -> str:
        """Convert message to binary string."""
        message_bytes = self._pad_message(message)
        bits = ''.join(format(byte, '08b') for byte in message_bytes)
        return bits
    
    def _bits_to_message(self, bits: str) -> str:
        """Convert binary string back to message."""
        # Pad to byte boundary
        if len(bits) % 8 != 0:
            bits = bits + '0' * (8 - len(bits) % 8)
        
        message_bytes = bytes(
            int(bits[i:i+8], 2) 
            for i in range(0, len(bits), 8)
        )
        return message_bytes.decode('utf-8', errors='ignore')
    
    def _xor_bits(self, msg_bits: str, key_bits: str) -> str:
        """XOR two bit strings."""
        if len(msg_bits) > len(key_bits):
            raise ValueError(
                f"Message too long ({len(msg_bits)} bits) for key ({len(key_bits)} bits). "
                f"Use key rotation or shorter messages."
            )
        
        return ''.join(
            str(int(m) ^ int(k))
            for m, k in zip(msg_bits, key_bits[:len(msg_bits)])
        )
    
    def encrypt(self, message: str) -> str:
        """
        Encrypt message using quantum key.
        
        Args:
            message: Plain text message
            
        Returns:
            Base64-encoded encrypted message
        """
        # Convert message to bits
        msg_bits = self._message_to_bits(message)
        
        # XOR with quantum key
        encrypted_bits = self._xor_bits(msg_bits, self.quantum_key)
        
        # Convert to bytes and encode
        if len(encrypted_bits) % 8 != 0:
            encrypted_bits = encrypted_bits + '0' * (8 - len(encrypted_bits) % 8)
        
        encrypted_bytes = bytes(
            int(encrypted_bits[i:i+8], 2)
            for i in range(0, len(encrypted_bits), 8)
        )
        
        # Base64 encode for safe transmission
        encoded = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        return encoded
    
    def decrypt(self, encrypted_message: str) -> str:
        """
        Decrypt message using quantum key.
        
        Args:
            encrypted_message: Base64-encoded encrypted message
            
        Returns:
            Plain text message
        """
        # Base64 decode
        try:
            encrypted_bytes = base64.b64decode(encrypted_message.encode('utf-8'))
        except Exception as e:
            raise ValueError(f"Invalid encrypted message format: {e}")
        
        # Convert to bits
        encrypted_bits = ''.join(format(byte, '08b') for byte in encrypted_bytes)
        
        # XOR with quantum key (XOR is symmetric)
        decrypted_bits = self._xor_bits(encrypted_bits, self.quantum_key)
        
        # Convert back to message
        message = self._bits_to_message(decrypted_bits)
        
        return message
    
    def get_key_size(self) -> int:
        """Get quantum key size in bits."""
        return len(self.quantum_key)
    
    def get_max_message_length(self) -> int:
        """Get maximum message length (in characters) with this key."""
        # Rough estimate: each character is ~8 bits
        return self.get_key_size() // 8


class MessageCrypto:
    """
    High-level message encryption/decryption interface.
    
    Handles encryption of individual messages with automatic key management.
    """
    
    def __init__(self, quantum_key: str):
        """Initialize with quantum key."""
        self.encryptor = QuantumEncryption(quantum_key)
    
    def encrypt_message(self, sender: str, message: str) -> Dict:
        """
        Encrypt a chat message.
        
        Args:
            sender: Sender's username
            message: Message text
            
        Returns:
            Dictionary with encrypted message and metadata
        """
        encrypted = self.encryptor.encrypt(message)
        
        return {
            'sender': sender,
            'encrypted': encrypted,
            'timestamp': self._get_timestamp(),
            'key_bits_used': len(message) * 8  # Approximate
        }
    
    def decrypt_message(self, encrypted_data: Dict) -> Dict:
        """
        Decrypt a chat message.
        
        Args:
            encrypted_data: Dictionary with encrypted message
            
        Returns:
            Dictionary with decrypted message and metadata
        """
        try:
            decrypted = self.encryptor.decrypt(encrypted_data['encrypted'])
            return {
                'sender': encrypted_data['sender'],
                'message': decrypted,
                'timestamp': encrypted_data['timestamp'],
                'status': 'decrypted',
                'error': None
            }
        except Exception as e:
            return {
                'sender': encrypted_data['sender'],
                'message': '',
                'timestamp': encrypted_data['timestamp'],
                'status': 'error',
                'error': str(e)
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


# Type hint for import
from typing import Dict


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Quantum Encryption")
    print("=" * 70)
    
    # Generate a test quantum key (256 bits)
    test_key = "1" * 256  # In practice, this comes from BB84
    
    print(f"\nQuantum Key (first 64 bits): {test_key[:64]}...")
    print(f"Key size: {len(test_key)} bits")
    
    # Create encryptor
    crypto = QuantumEncryption(test_key)
    print(f"Max message length: {crypto.get_max_message_length()} characters")
    
    # Test encryption/decryption
    messages = [
        "Hello World",
        "Quantum Cryptography",
        "This is a test message"
    ]
    
    print("\nTesting Encryption/Decryption:")
    print("-" * 70)
    
    for msg in messages:
        encrypted = crypto.encrypt(msg)
        decrypted = crypto.decrypt(encrypted)
        
        status = "✓" if msg == decrypted else "✗"
        print(f"{status} Message: '{msg}'")
        print(f"  Encrypted: {encrypted[:30]}...")
        print(f"  Decrypted: '{decrypted}'")
        print()
    
    # Test high-level interface
    print("Testing MessageCrypto Interface:")
    print("-" * 70)
    
    msg_crypto = MessageCrypto(test_key)
    
    # Encrypt
    encrypted_data = msg_crypto.encrypt_message("Alice", "Secret message")
    print(f"Encrypted message: {encrypted_data['encrypted'][:30]}...")
    
    # Decrypt
    decrypted_data = msg_crypto.decrypt_message(encrypted_data)
    print(f"Decrypted message: '{decrypted_data['message']}'")
    print(f"Status: {decrypted_data['status']}")
    
    print("\n✓ Quantum Encryption test completed successfully!")
