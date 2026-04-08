"""
BB84 Protocol Wrapper for RL Integration
Executes real BB84 protocol and extracts RL-relevant metrics
"""

import sys
import os
import json
import random
from typing import Tuple, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


class BB84Wrapper:
    """
    Wrapper around BB84 protocol for RL integration.
    Returns: (sifted_key, qber, eve_detected_likelihood, measurements_data)
    """
    
    def __init__(self, key_length: int = 64, use_simulator: bool = True, 
                 eve_present: bool = False, eve_intercept_ratio: float = 1.0,
                 channel_error_rate: float = 0.01):
        """
        Initialize BB84 wrapper.
        
        Args:
            key_length: Number of qubits to send
            use_simulator: Use QasmSimulator (True) or IBM hardware (False)
            eve_present: Whether Eve is eavesdropping
            eve_intercept_ratio: Fraction of qubits Eve intercepts (0.0 to 1.0)
            channel_error_rate: Probability of bit flip due to channel noise (0.0 to 1.0)
        """
        self.key_length = key_length
        self.use_simulator = use_simulator
        self.eve_present = eve_present
        self.eve_intercept_ratio = eve_intercept_ratio
        self.channel_error_rate = channel_error_rate  # Realistic quantum channel noise
        
        self.simulator = AerSimulator()
        self.shots = 1
        self.accuracy_threshold = 95
        
        # Protocol state
        self.alice_bits = []
        self.alice_bases = []
        self.bob_bases = []
        self.eve_bases = []
        self.eve_measurements = []
        self.bob_measurements = []
        self.sifted_key = ""
        self.qber = 0.0
        
    def get_random_bits(self, size: int) -> list:
        """Generate random bits using quantum randomness."""
        circuit = QuantumCircuit(size, size)
        circuit.h(range(size))
        circuit.measure(range(size), range(size))
        
        compiled = transpile(circuit, self.simulator)
        job = self.simulator.run(compiled, shots=1, memory=True)
        result = job.result()
        bits_str = result.get_memory(compiled)[0]
        return [int(b) for b in bits_str]
    
    def get_random_bases(self, size: int) -> list:
        """Generate random basis sequence (0=Z, 1=X)."""
        return [random.randint(0, 1) for _ in range(size)]
    
    def prepare_state(self, bit: int, basis: int) -> str:
        """Prepare quantum state given bit and basis."""
        if bit == 0:
            return "0" if basis == 0 else "+"  # |0> or |+>
        else:
            return "1" if basis == 0 else "-"  # |1> or |->
    
    def run_protocol(self) -> Dict:
        """Execute full BB84 protocol."""
        # Alice prepares
        self.alice_bits = self.get_random_bits(self.key_length)
        self.alice_bases = self.get_random_bases(self.key_length)
        
        # Eve's strategy (if present)
        if self.eve_present:
            num_to_intercept = max(1, int(self.key_length * self.eve_intercept_ratio))
            eve_intercept_positions = random.sample(range(self.key_length), num_to_intercept)
            self.eve_bases = [
                self.get_random_bases(1)[0] if i in eve_intercept_positions 
                else self.alice_bases[i]  # Eve tries to guess when not intercepting
                for i in range(self.key_length)
            ]
            # Eve measures intercepted qubits
            self.eve_measurements = [
                self.alice_bits[i] if self.alice_bases[i] == self.eve_bases[i]
                else random.randint(0, 1)
                for i in range(self.key_length)
            ]
        else:
            self.eve_bases = [None] * self.key_length
            self.eve_measurements = [None] * self.key_length
        
        # Bob prepares measurement bases
        self.bob_bases = self.get_random_bases(self.key_length)
        
        # Bob's measurements (simulating quantum measurement + channel noise)
        bob_ideal = [
            self.eve_measurements[i] if self.eve_present and self.eve_bases[i] == self.bob_bases[i]
            else (self.alice_bits[i] if self.alice_bases[i] == self.bob_bases[i]
                  else random.randint(0, 1))
            for i in range(self.key_length)
        ]
        
        # Add channel noise: each bit has channel_error_rate probability of flipping
        self.bob_measurements = [
            1 - bit if random.random() < self.channel_error_rate else bit
            for bit in bob_ideal
        ]
        
        # Sifting: keep only bits where Alice & Bob used same basis
        sift_positions = [i for i in range(self.key_length) 
                         if self.alice_bases[i] == self.bob_bases[i]]
        
        alice_sifted = [self.alice_bits[i] for i in sift_positions]
        bob_sifted = [self.bob_measurements[i] for i in sift_positions]
        
        self.sifted_key = "".join(str(b) for b in alice_sifted)
        
        # Calculate QBER (Quantum Bit Error Rate)
        if len(alice_sifted) > 0:
            errors = sum(1 for a, b in zip(alice_sifted, bob_sifted) if a != b)
            # If we are simulating a non-zero error channel, it's statistically
            # possible (especially with short keys) that *no* bit is flipped.
            # In training this led to long runs of QBER=0 and a flat Eve
            # likelihood, which confused the DQN agent.  To provide a clearer
            # learning signal we ensure at least one error when
            # channel_error_rate>0 by flipping a random sifted bit if
            # ``errors`` is zero.
            if errors == 0 and self.channel_error_rate > 0:
                # flip one random position in the sifted arrays
                import random as _rnd
                idx = _rnd.randrange(len(alice_sifted))
                bob_sifted[idx] = 1 - bob_sifted[idx]
                errors = 1
            self.qber = errors / len(alice_sifted)
        else:
            self.qber = 0.0
        
        return {
            'sifted_key': self.sifted_key,
            'qber': self.qber,
            'sifted_length': len(alice_sifted),
            'alice_bits': self.alice_bits,
            'alice_bases': self.alice_bases,
            'bob_bases': self.bob_bases,
            'bob_measurements': self.bob_measurements,
            'eve_bases': self.eve_bases,
            'eve_measurements': self.eve_measurements,
        }
    
    def calculate_eve_likelihood(self) -> float:
        """
        Estimate likelihood of eavesdropping using Bayesian inference.
        Higher QBER + correlated errors = higher Eve likelihood.

        The previous implementation returned **0.0** for any QBER below
        5%. that led to a constant 0 value when the channel was only
        slightly noisy.  Instead we now provide a smooth mapping even for
        small error rates, producing a tiny nonzero likelihood that the
        training agent can observe.
        """
        # small QBER should still produce a small likelihood rather than
        # clamping to zero. we scale linearly up to 0.05 (5%), then follow
        # the earlier piecewise behaviour.
        if self.qber < 0.05:
            # map [0,0.05] → [0,0.1]
            return min(0.1, self.qber / 0.05 * 0.1)
        elif self.qber < 0.11:
            return min(0.5, self.qber * 2)  # gradual increase
        else:
            return min(1.0, self.qber)  # high confidence in Eve
    
    def to_json(self) -> str:
        """Export protocol trace for logging."""
        return json.dumps({
            'alice_bits': self.alice_bits,
            'alice_bases': self.alice_bases,
            'bob_bases': self.bob_bases,
            'bob_measurements': self.bob_measurements,
            'eve_bases': self.eve_bases,
            'eve_measurements': self.eve_measurements,
            'qber': self.qber,
        }, indent=2)


if __name__ == "__main__":
    # Test: run without Eve
    bb84 = BB84Wrapper(key_length=32, eve_present=False)
    result = bb84.run_protocol()
    print("=== BB84 Without Eve ===")
    print(f"Sifted Key Length: {result['sifted_length']}")
    print(f"QBER: {result['qber']:.4f}")
    print(f"Eve Likelihood: {bb84.calculate_eve_likelihood():.4f}")
    
    # Test: run with Eve
    bb84_eve = BB84Wrapper(key_length=32, eve_present=True, eve_intercept_ratio=0.5)
    result_eve = bb84_eve.run_protocol()
    print("\n=== BB84 With Eve (50% interception) ===")
    print(f"Sifted Key Length: {result_eve['sifted_length']}")
    print(f"QBER: {result_eve['qber']:.4f}")
    print(f"Eve Likelihood: {bb84_eve.calculate_eve_likelihood():.4f}")
