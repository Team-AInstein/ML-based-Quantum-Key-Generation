"""
Privacy Amplification for QKD
Reduces Eve's information about the final key through:
1. Parity checks (Toeplitz matrix approach)
2. XOR compression
3. Error correction integration
"""

import numpy as np
from typing import Tuple


class PrivacyAmplification:
    """
    Privacy amplification techniques to reduce Eve's information
    from O(1/2) down to O(2^-k) after k rounds.
    """
    
    @staticmethod
    def toeplitz_matrix_pa(sifted_key: str, compression_factor: float = 0.5) -> str:
        """
        Toeplitz matrix-based privacy amplification.
        XOR subsets of key bits to compress key and reduce Eve's knowledge.
        
        Args:
            sifted_key: Binary string from BB84 sifting
            compression_factor: Fraction of key to keep (0.5 = 50% compression)
        
        Returns:
            Compressed key with Eve's information reduced by ~50%
        """
        if len(sifted_key) < 2:
            return sifted_key
        
        key_bits = [int(b) for b in sifted_key]
        n = len(key_bits)
        m = max(1, int(n * compression_factor))
        
        # Generate Toeplitz matrix: random but structured
        np.random.seed(42)  # For reproducibility in testing
        first_row = np.random.randint(0, 2, m)
        first_col = np.random.randint(0, 2, n)
        first_col[0] = first_row[0]
        
        toeplitz_matrix = np.zeros((m, n), dtype=int)
        for i in range(m):
            for j in range(n):
                if j >= i:
                    toeplitz_matrix[i, j] = first_row[j - i]
                else:
                    toeplitz_matrix[i, j] = first_col[i - j]
        
        # Apply matrix: result[i] = sum(matrix[i] * key) mod 2
        result = []
        for i in range(m):
            xor_sum = 0
            for j in range(n):
                xor_sum ^= (toeplitz_matrix[i, j] * key_bits[j])
            result.append(str(xor_sum))
        
        return "".join(result)
    
    @staticmethod
    def parity_check_pa(sifted_key: str, num_rounds: int = 3) -> str:
        """
        Iterative parity check-based privacy amplification.
        Each round: pair up bits and XOR them.
        After k rounds, Eve's information ≈ 2^-k of original.
        
        Args:
            sifted_key: Binary string
            num_rounds: Number of parity rounds
        
        Returns:
            Final amplified key
        """
        current_key = sifted_key
        
        for round_num in range(num_rounds):
            if len(current_key) < 2:
                break
            
            new_key = ""
            # Pair consecutive bits and XOR them
            for i in range(0, len(current_key) - 1, 2):
                bit1 = int(current_key[i])
                bit2 = int(current_key[i + 1])
                xor_result = bit1 ^ bit2
                new_key += str(xor_result)
            
            # If odd number of bits, keep last one for next round
            if len(current_key) % 2 == 1:
                new_key += current_key[-1]
            
            current_key = new_key
        
        return current_key
    
    @staticmethod
    def xor_compression(sifted_key: str, group_size: int = 4) -> str:
        """
        Simple XOR-based key compression.
        Groups of bits are XORed together.
        
        Args:
            sifted_key: Binary string
            group_size: Number of bits to group (default 4)
        
        Returns:
            Compressed key
        """
        if len(sifted_key) < group_size:
            return sifted_key
        
        result = ""
        for i in range(0, len(sifted_key), group_size):
            group = sifted_key[i:i+group_size]
            xor_result = 0
            for bit in group:
                xor_result ^= int(bit)
            result += str(xor_result)
        
        return result
    
    @staticmethod
    def apply_error_correction(sifted_key: str, eve_probability: float = 0.5) -> str:
        """
        Apply error correction if Eve has likely introduced errors.
        Uses simple majority voting on groups.
        
        Args:
            sifted_key: Binary string
            eve_probability: Estimated probability Eve was eavesdropping
        
        Returns:
            Error-corrected key
        """
        if eve_probability < 0.3 or len(sifted_key) < 3:
            return sifted_key
        
        # Simple error correction: majority voting in groups of 3
        result = ""
        for i in range(0, len(sifted_key) - 2, 3):
            bit1 = int(sifted_key[i])
            bit2 = int(sifted_key[i + 1])
            bit3 = int(sifted_key[i + 2])
            
            majority = (bit1 + bit2 + bit3) >= 2
            result += str(int(majority))
        
        # Handle remaining bits
        if len(sifted_key) % 3 == 1:
            result += sifted_key[-1]
        elif len(sifted_key) % 3 == 2:
            # Majority vote of last 2 bits (if tie, take first)
            bit1 = int(sifted_key[-2])
            bit2 = int(sifted_key[-1])
            result += str(max(bit1, bit2))
        
        return result
    
    @staticmethod
    def full_privacy_amplification_pipeline(sifted_key: str, 
                                           eve_likelihood: float = 0.0,
                                           method: str = "parity") -> Tuple[str, dict]:
        """
        Complete privacy amplification pipeline.
        
        Args:
            sifted_key: Initial sifted key from BB84
            eve_likelihood: Estimated probability of eavesdropping
            method: "parity", "toeplitz", or "xor"
        
        Returns:
            (final_key, metadata_dict)
        """
        if not sifted_key:
            return "", {
                'original_length': 0,
                'final_length': 0,
                'method_used': method,
                'eve_likelihood': eve_likelihood,
                'reduction_factor': 0,
            }
        
        original_length = len(sifted_key)
        
        # Step 1: Error correction (if Eve present)
        if eve_likelihood > 0.5:
            corrected_key = PrivacyAmplification.apply_error_correction(
                sifted_key, eve_likelihood
            )
        else:
            corrected_key = sifted_key
        
        # Step 2: Privacy amplification
        if method == "parity":
            final_key = PrivacyAmplification.parity_check_pa(corrected_key, num_rounds=3)
        elif method == "toeplitz":
            final_key = PrivacyAmplification.toeplitz_matrix_pa(corrected_key, compression_factor=0.5)
        elif method == "xor":
            final_key = PrivacyAmplification.xor_compression(corrected_key, group_size=4)
        else:
            final_key = corrected_key
        
        final_length = len(final_key)
        reduction_factor = original_length / final_length if final_length > 0 else float('inf')
        
        metadata = {
            'original_length': original_length,
            'final_length': final_length,
            'method_used': method,
            'eve_likelihood': eve_likelihood,
            'reduction_factor': reduction_factor,
            'error_correction_applied': eve_likelihood > 0.5,
        }
        
        return final_key, metadata


if __name__ == "__main__":
    # Test privacy amplification
    test_key = "11010110101101101010"
    print(f"Original key: {test_key} (length: {len(test_key)})")
    
    # Test parity-based PA
    parity_key, metadata = PrivacyAmplification.full_privacy_amplification_pipeline(
        test_key, eve_likelihood=0.7, method="parity"
    )
    print(f"\nParity-based PA:")
    print(f"  Final key: {parity_key}")
    print(f"  Metadata: {metadata}")
    
    # Test Toeplitz-based PA
    toeplitz_key, metadata = PrivacyAmplification.full_privacy_amplification_pipeline(
        test_key, eve_likelihood=0.7, method="toeplitz"
    )
    print(f"\nToeplitz-based PA:")
    print(f"  Final key: {toeplitz_key}")
    print(f"  Metadata: {metadata}")
    
    # Test XOR-based PA
    xor_key, metadata = PrivacyAmplification.full_privacy_amplification_pipeline(
        test_key, eve_likelihood=0.7, method="xor"
    )
    print(f"\nXOR-based PA:")
    print(f"  Final key: {xor_key}")
    print(f"  Metadata: {metadata}")
