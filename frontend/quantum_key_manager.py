"""
Quantum Key Manager for Secure Chatbot Communication

Generates quantum keys using BB84 protocol and provides key management
for encryption/decryption of chat messages.
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# Add parent paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up from frontend to MAJOR_PROJECT
rl_path = os.path.join(project_root, 'Final', 'Zeenats_Debug', 'ML-based-QKD-using-DeepQN', 'RL')

# Insert at beginning of path
if rl_path not in sys.path:
    sys.path.insert(0, rl_path)

try:
    from bb84_wrapper import BB84Wrapper
    from privacy_amplification import PrivacyAmplification
except ImportError as e:
    print(f"Warning: Could not import quantum modules from {rl_path}")
    print(f"Error: {e}")
    raise


class QuantumKeyManager:
    """
    Manages quantum key generation and lifecycle for secure communication.
    
    Features:
    - Generates quantum keys using BB84 protocol
    - Applies privacy amplification for security
    - Stores and retrieves keys with expiration
    - Tracks key usage and statistics
    """
    
    def __init__(self, key_length: int = 4096, store_dir: str = "./quantum_keys"):
        """
        Initialize Quantum Key Manager.
        
        Args:
            key_length: Number of qubits for BB84 (default 2048 for longer messages)
            store_dir: Directory to store generated keys
        """
        self.key_length = key_length
        self.store_dir = store_dir
        self.active_keys: Dict[str, Dict] = {}  # session_id -> key_info
        self.key_cache: Dict[str, str] = {}     # session_id -> quantum_key
        self.expiration_hours = 24               # Keys expire after 24 hours
        
        # Create storage directory
        os.makedirs(store_dir, exist_ok=True)
        
        # Initialize BB84 and Privacy Amplification
        self.bb84 = None
        self.pa = PrivacyAmplification()
        
    def generate_quantum_key(self, session_id: str, eve_present: bool = False) -> Dict:
        """
        Generate a quantum key using BB84 protocol.
        
        Args:
            session_id: Unique session identifier
            eve_present: Whether to simulate Eve eavesdropping (default False)
            
        Returns:
            Dictionary with:
            - sifted_key: Raw sifted key from BB84
            - final_key: Privacy amplified key
            - qber: Quantum Bit Error Rate
            - eve_likelihood: Probability of eavesdropping
            - timestamp: Generation time
        """
        print(f"[QKM] Generating quantum key for session {session_id}...")
        
        # Run BB84 protocol
        bb84 = BB84Wrapper(
            key_length=self.key_length,
            eve_present=eve_present,
            eve_intercept_ratio=0.5 if eve_present else 0.0,
            channel_error_rate=0.01
        )
        result = bb84.run_protocol()
        
        sifted_key = result['sifted_key']
        qber = result['qber']
        eve_likelihood = bb84.calculate_eve_likelihood()
        sifted_length = result['sifted_length']
        
        # Check if secure
        is_secure = eve_likelihood < 0.5
        
        if not is_secure:
            raise SecurityError(f"Eavesdropping detected! Eve likelihood: {eve_likelihood:.4f}")
        
        # Apply Privacy Amplification
        final_key, pa_metadata = self.pa.full_privacy_amplification_pipeline(
            sifted_key=sifted_key,
            eve_likelihood=eve_likelihood,
            method="parity"
        )
        
        key_info = {
            'session_id': session_id,
            'sifted_key': sifted_key,
            'final_key': final_key,
            'qber': qber,
            'eve_likelihood': eve_likelihood,
            'sifted_length': sifted_length,
            'final_length': len(final_key),
            'timestamp': datetime.now().isoformat(),
            'expiration': (datetime.now() + timedelta(hours=self.expiration_hours)).isoformat(),
            'is_secure': is_secure,
            'usage_count': 0
        }
        
        # Store key
        self.active_keys[session_id] = key_info
        self.key_cache[session_id] = final_key
        
        # Save to disk
        self._save_key_to_disk(session_id, key_info)
        
        print(f"[QKM] Key generated successfully!")
        print(f"  - Sifted Key: {sifted_length} bits")
        print(f"  - Final Key: {len(final_key)} bits")
        print(f"  - QBER: {qber:.4f} ({qber*100:.2f}%)")
        print(f"  - Eve Likelihood: {eve_likelihood:.4f}")
        print(f"  - Secure: {'YES' if is_secure else 'NO'}")
        
        return {
            'success': True,
            'sifted_key_length': sifted_length,
            'final_key_length': len(final_key),
            'qber': qber,
            'eve_likelihood': eve_likelihood,
            'is_secure': is_secure
        }
    
    def get_key(self, session_id: str) -> Optional[str]:
        """
        Retrieve quantum key for session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Quantum key string or None if expired/not found
        """
        if session_id not in self.active_keys:
            # Try to load from disk
            key_info = self._load_key_from_disk(session_id)
            if key_info is None:
                return None
            self.active_keys[session_id] = key_info
            self.key_cache[session_id] = key_info['final_key']
        
        # Check expiration
        key_info = self.active_keys[session_id]
        expiration = datetime.fromisoformat(key_info['expiration'])
        if datetime.now() > expiration:
            del self.active_keys[session_id]
            if session_id in self.key_cache:
                del self.key_cache[session_id]
            return None
        
        # Update usage
        key_info['usage_count'] += 1
        
        return self.key_cache.get(session_id)
    
    def key_exists(self, session_id: str) -> bool:
        """Check if valid key exists for session."""
        key = self.get_key(session_id)
        return key is not None
    
    def get_key_info(self, session_id: str) -> Optional[Dict]:
        """Get metadata about a key."""
        if session_id not in self.active_keys:
            return None
        return self.active_keys[session_id]
    
    def revoke_key(self, session_id: str) -> bool:
        """Revoke a key (for security reasons)."""
        if session_id in self.active_keys:
            del self.active_keys[session_id]
        if session_id in self.key_cache:
            del self.key_cache[session_id]
        return True
    
    def rotate_key(self, session_id: str) -> Dict:
        """Generate a new key for session (rotate)."""
        self.revoke_key(session_id)
        return self.generate_quantum_key(session_id)
    
    def _save_key_to_disk(self, session_id: str, key_info: Dict):
        """Save key metadata to disk."""
        filepath = os.path.join(self.store_dir, f"{session_id}_key.json")
        with open(filepath, 'w') as f:
            # Don't save actual keys to disk (security)
            safe_info = {
                'session_id': key_info['session_id'],
                'qber': key_info['qber'],
                'eve_likelihood': key_info['eve_likelihood'],
                'sifted_length': key_info['sifted_length'],
                'final_length': key_info['final_length'],
                'timestamp': key_info['timestamp'],
                'expiration': key_info['expiration'],
                'is_secure': key_info['is_secure']
            }
            json.dump(safe_info, f, indent=2)
    
    def _load_key_from_disk(self, session_id: str) -> Optional[Dict]:
        """Load key metadata from disk (but not actual key)."""
        filepath = os.path.join(self.store_dir, f"{session_id}_key.json")
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def get_statistics(self) -> Dict:
        """Get statistics about active keys."""
        return {
            'active_keys': len(self.active_keys),
            'cached_keys': len(self.key_cache),
            'total_stored': len(os.listdir(self.store_dir)),
            'keys': [
                {
                    'session_id': info['session_id'],
                    'final_length': info['final_length'],
                    'usage_count': info['usage_count'],
                    'is_secure': info['is_secure']
                }
                for info in self.active_keys.values()
            ]
        }


class SecurityError(Exception):
    """Raised when security threat detected."""
    pass


if __name__ == "__main__":
    # Test the key manager
    print("=" * 70)
    print("Testing Quantum Key Manager")
    print("=" * 70)
    
    manager = QuantumKeyManager(key_length=256)
    
    # Generate key for user1
    print("\nGenerating key for User 1...")
    result1 = manager.generate_quantum_key("user1_session")
    
    # Generate key for user2
    print("\nGenerating key for User 2...")
    result2 = manager.generate_quantum_key("user2_session")
    
    # Retrieve keys
    print("\nRetrieving keys...")
    key1 = manager.get_key("user1_session")
    key2 = manager.get_key("user2_session")
    print(f"User 1 key length: {len(key1)} bits")
    print(f"User 2 key length: {len(key2)} bits")
    
    # Get statistics
    print("\nStatistics:")
    stats = manager.get_statistics()
    for session_data in stats['keys']:
        print(f"  {session_data['session_id']}: {session_data['final_length']} bits, "
              f"Usage: {session_data['usage_count']}, Secure: {session_data['is_secure']}")
    
    print("\n✓ Quantum Key Manager test completed successfully!")
