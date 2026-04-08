"""
Integrated QKD Environment that runs REAL BB84 protocol
State includes QBER, Eve likelihood, sifted key length
Agent adjusts protocol parameters to optimize key generation under attack
"""

import random
import numpy as np
from bb84_wrapper import BB84Wrapper


class IntegratedQKDEnv:
    """
    RL Environment that interfaces with real BB84 protocol.
    
    State: (QBER, Eve_Likelihood, Sifted_Key_Length_Ratio)
    Actions: 
        0 = Maintain parameters (baseline)
        1 = Increase error correction strength
        2 = Decrease error correction (faster but noisier)
        3 = Reduce key length (abort if too many errors)
        4 = Continue with privacy amplification
    
    Reward: Based on key quality, QBER, and Eve detection
    """
    
    def __init__(self, key_length: int = 64, max_steps: int = 20,
                 channel_error_rate: float = 0.01,
                 random_noise: bool = False,
                 eve_probability: float = 0.5):
        """Initialize environment.

        Args:
            key_length: number of qubits in each BB84 run
            max_steps: maximum RL steps per episode
            channel_error_rate: baseline probability of a bit flip due to
                physical channel noise (0.0 to 1.0).
            random_noise: if True, each BB84 invocation will draw a new
                error rate uniformly between 0 and 2*channel_error_rate.
            eve_probability: chance that Eve is present at the start of an
                episode; if present her intercept ratio is randomized.
        """
        self.key_length = key_length
        self.max_steps = max_steps
        self.current_step = 0
        self.episode_history = []
        
        # Protocol parameters (adjustable by agent)
        self.error_correction_strength = 1.0  # 0.5 to 2.0
        self.key_length_factor = 1.0  # 0.5 to 1.0
        
        # Thresholds
        self.qber_threshold_abort = 0.25  # If QBER > 25%, abort
        self.qber_threshold_warning = 0.11  # If QBER > 11%, likely Eve
        
        # environment configuration
        self.base_channel_error_rate = channel_error_rate
        self.random_noise = random_noise
        self.eve_probability = eve_probability

        # state that persists across steps in an episode
        self.eve_present = False
        self.eve_intercept_ratio = 0.0
        
        self.actions = [0, 1, 2, 3, 4]
        
    def reset(self):
        """Reset environment for new episode and choose fresh noise/eavesdrop state."""
        self.current_step = 0
        self.error_correction_strength = 1.0
        self.key_length_factor = 1.0
        self.episode_history = []
        self.prev_qber = None
        
        # pick whether Eve is on duty this episode and how aggressive she is
        self.eve_present = random.random() < self.eve_probability
        self.eve_intercept_ratio = (
            random.uniform(0.3, 1.0) if self.eve_present else 0.0
        )
        
        # run initial BB84, channel noise may vary if random_noise enabled
        bb84 = BB84Wrapper(
            key_length=self.key_length,
            eve_present=self.eve_present,
            eve_intercept_ratio=self.eve_intercept_ratio,
            channel_error_rate=self._get_channel_error()
        )
        result = bb84.run_protocol()
        
        self.current_bb84 = bb84
        self.current_qber = result['qber']
        self.current_eve_likelihood = bb84.calculate_eve_likelihood()
        self.current_sifted_length = result['sifted_length']
        
        state = self._get_state()
        return state
    
    def _get_state(self):
        """Encode current state as normalized tuple."""
        qber_norm = min(1.0, self.current_qber / self.qber_threshold_abort)
        sifted_norm = min(1.0, self.current_sifted_length / self.key_length)
        
        return (
            round(qber_norm, 3),
            round(self.current_eve_likelihood, 3),
            round(sifted_norm, 3)
        )
    
    def step(self, action: int):
        """
        Execute action and get next state.
        
        Returns:
            next_state: New environment state
            reward: Scalar reward signal
            done: Whether episode terminates
        """
        if action not in self.actions:
            raise ValueError(f"Invalid action: {action}")
        
        self.current_step += 1
        
        # Apply action to protocol parameters
        if action == 0:  # Maintain
            pass
        elif action == 1:  # Increase EC strength
            self.error_correction_strength = min(2.0, self.error_correction_strength + 0.2)
        elif action == 2:  # Decrease EC strength
            self.error_correction_strength = max(0.5, self.error_correction_strength - 0.2)
        elif action == 3:  # Reduce key length
            self.key_length_factor = max(0.5, self.key_length_factor - 0.2)
        elif action == 4:  # Privacy amplification (discussed below)
            self.apply_privacy_amplification()
        
        # Run BB84 with adjusted parameters (noise/eavesdrop state carried forward)
        adjusted_key_length = max(8, int(self.key_length * self.key_length_factor))
        bb84 = BB84Wrapper(
            key_length=adjusted_key_length,
            eve_present=self.eve_present,
            eve_intercept_ratio=self.eve_intercept_ratio,
            channel_error_rate=self._get_channel_error()
        )
        result = bb84.run_protocol()
        
        self.current_bb84 = bb84
        self.current_qber = result['qber']
        self.current_eve_likelihood = bb84.calculate_eve_likelihood()
        self.current_sifted_length = result['sifted_length']
        
        # Compute reward
        reward = self._compute_reward(action)
        
        # Check termination
        done = (self.current_step >= self.max_steps or 
                self.current_qber >= self.qber_threshold_abort or
                self.current_sifted_length == 0)
        
        next_state = self._get_state()
        
        # Log for debugging
        self.episode_history.append({
            'step': self.current_step,
            'action': action,
            'qber': self.current_qber,
            'eve_likelihood': self.current_eve_likelihood,
            'sifted_length': self.current_sifted_length,
            'reward': reward,
            'done': done
        })
        
        return next_state, reward, done
    
    def _compute_reward(self, action: int) -> float:
        """
        Compute reward based on:
        - Quality of sifted key
        - Detection of eavesdropping
        - Efficiency (bits generated)
        - Reduction in error rate (QBER)
        """
        reward = 0.0

        # Reward for generating key bits (smaller multiplier so QBER matters more)
        reward += self.current_sifted_length * 0.05

        # Reward improvement in QBER compared to the previous step
        if getattr(self, 'prev_qber', None) is not None:
            reward += 40 * (self.prev_qber - self.current_qber)
        self.prev_qber = self.current_qber

        # Penalty for high QBER; bonus for low QBER
        if self.current_qber > self.qber_threshold_abort:
            reward -= 100  # Severe penalty for compromised security
        elif self.current_qber > self.qber_threshold_warning:
            reward -= 10 * self.current_qber  # Growing penalty
        else:
            reward += 20  # Bonus for low QBER

        # Reward for detecting Eve
        if self.current_eve_likelihood > 0.7:
            reward += 30  # Good detection

        # Penalty for action 3 (reduce key length) unless necessary
        if action == 3 and self.current_qber < self.qber_threshold_warning:
            reward -= 5

        return reward
    
    def apply_privacy_amplification(self):
        """Apply privacy amplification when agent requests it."""
        if len(self.current_bb84.sifted_key) < 8:
            return  # Key too short
        
        # Simple PA: XOR with parity bits
        sifted = self.current_bb84.sifted_key
        parity_bits = ""
        for i in range(0, len(sifted) - 1, 2):
            parity = int(sifted[i]) ^ int(sifted[i + 1])
            parity_bits += str(parity)
        
        # Reduce Eve's information by ~50% per round
        self.current_bb84.sifted_key = parity_bits
        self.current_sifted_length = len(parity_bits)


    def _get_channel_error(self) -> float:
        """Return an error rate for the next BB84 execution.

        The rate is drawn from a fixed value or uniformly randomized when
        ``random_noise`` is True. The value is clipped to [0,1].
        """
        if self.random_noise:
            rate = random.uniform(0.0, self.base_channel_error_rate * 2)
        else:
            rate = self.base_channel_error_rate
        # enforce a tiny floor so that extremely lucky zero-error episodes
        # are extremely unlikely; this keeps QBER from becoming exactly
        # zero when noise is meant to be active.
        return max(rate, 1e-4)


if __name__ == "__main__":
    env = IntegratedQKDEnv(key_length=64, max_steps=10)
    
    state = env.reset()
    print(f"Initial State: {state}")
    
    total_reward = 0
    for step in range(10):
        action = random.choice(env.actions)
        next_state, reward, done = env.step(action)
        total_reward += reward
        
        print(f"Step {step} | Action: {action} | QBER: {env.current_qber:.4f} | "
              f"Reward: {reward:.2f} | Done: {done}")
        
        if done:
            break
    
    print(f"\nTotal Reward: {total_reward:.2f}")
    print(f"Episode History:")
    for entry in env.episode_history:
        print(f"  {entry}")
