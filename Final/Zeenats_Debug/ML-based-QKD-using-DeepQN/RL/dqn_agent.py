"""
Deep Q-Network (DQN) Implementation for QKD Optimization
Replaces tabular Q-learning with neural network-based function approximation
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
import random
import os
import json


class DQNNetwork(nn.Module):
    """
    Deep Q-Network: neural network that approximates Q(state, action)
    Architecture: 3-layer dense network with ReLU activation
    """
    
    def __init__(self, state_size: int = 3, action_size: int = 5, hidden_size: int = 128):
        """
        Initialize DQN network.
        
        Args:
            state_size: Dimension of state space
            action_size: Number of discrete actions
            hidden_size: Number of neurons in hidden layers
        """
        super(DQNNetwork, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(hidden_size, action_size)
        )
    
    def forward(self, state):
        """Forward pass: state -> Q-values for all actions."""
        return self.network(state)


class DQNAgent:
    """
    DQN Agent with experience replay and target network.
    Learns to make optimal decisions in QKD environment.
    """
    
    def __init__(self, state_size: int = 3, action_size: int = 5,
                 learning_rate: float = 0.0001, gamma: float = 0.99,
                 epsilon: float = 1.0, epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01, buffer_size: int = 10000,
                 batch_size: int = 32, target_update_frequency: int = 50):
        """
        Initialize DQN agent.
        
        Args:
            state_size: Dimension of state
            action_size: Number of actions
            learning_rate: Adam optimizer learning rate
            gamma: Discount factor
            epsilon: Exploration rate
            epsilon_decay: Decay factor for exploration
            epsilon_min: Minimum exploration rate
            buffer_size: Size of experience replay buffer
            batch_size: Minibatch size for replay updates
            target_update_frequency: Steps between target network syncs
        """
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Device (GPU if available)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Main and target networks
        self.q_network = DQNNetwork(state_size, action_size).to(self.device)
        self.target_network = DQNNetwork(state_size, action_size).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()
        
        # Optimizer and loss (Huber for stability)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        self.loss_fn = nn.SmoothL1Loss()
        
        # Experience replay buffer
        self.experience_buffer = deque(maxlen=buffer_size)
        self.batch_size = batch_size
        
        # Training metrics
        self.loss_history = []
        self.update_counter = 0
        self.target_update_frequency = target_update_frequency

    def update_epsilon(self):
        """Reduce epsilon according to schedule (call once per episode)."""
        if self.epsilon > self.epsilon_min:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer."""
        self.experience_buffer.append((state, action, reward, next_state, done))
    
    def choose_action(self, state, training: bool = True):
        """
        Choose action using epsilon-greedy strategy.
        
        Args:
            state: Current state (tuple or array)
            training: If True, use exploration; if False, exploit only
        
        Returns:
            action: Integer action index
        """
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        
        # Convert state to tensor
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
            action = q_values.argmax(dim=1).item()
        
        return action
    
    def replay(self, batch_size: int = None):
        """
        Train on mini-batch from experience buffer.
        Uses target network to stabilize learning.
        """
        if batch_size is None:
            batch_size = self.batch_size
        
        if len(self.experience_buffer) < batch_size:
            return None  # Not enough samples yet
        
        # Sample mini-batch
        mini_batch = random.sample(self.experience_buffer, batch_size)
        
        states = np.array([exp[0] for exp in mini_batch])
        actions = np.array([exp[1] for exp in mini_batch])
        rewards = np.array([exp[2] for exp in mini_batch])
        next_states = np.array([exp[3] for exp in mini_batch])
        dones = np.array([exp[4] for exp in mini_batch])
        
        # Convert to tensors
        states_t = torch.FloatTensor(states).to(self.device)
        actions_t = torch.LongTensor(actions).to(self.device)
        rewards_t = torch.FloatTensor(rewards).to(self.device)
        next_states_t = torch.FloatTensor(next_states).to(self.device)
        dones_t = torch.FloatTensor(dones).to(self.device)
        
        # Current Q-values
        q_values = self.q_network(states_t)
        q_values = q_values.gather(1, actions_t.unsqueeze(1)).squeeze(1)
        
        # Target Q-values
        with torch.no_grad():
            next_q_values = self.target_network(next_states_t).max(1)[0]
            target_q_values = rewards_t + (1 - dones_t) * self.gamma * next_q_values
        
        # Compute loss and update
        loss = self.loss_fn(q_values, target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()
        
        # Update target network periodically
        self.update_counter += 1
        if self.update_counter % self.target_update_frequency == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        # NOTE: epsilon decay moved to explicit method so that training
        # loop can control when the exploration rate is reduced (e.g. once
        # per episode instead of every replay step).
        # previously this code caused epsilon to hit its minimum early in an
        # episode; the trainer now calls ``update_epsilon()`` instead.
        pass
        
        loss_value = loss.item()
        self.loss_history.append(loss_value)
        
        return loss_value
    
    def save(self, filepath: str):
        """Save model weights and hyperparameters."""
        checkpoint = {
            'q_network_state': self.q_network.state_dict(),
            'target_network_state': self.target_network.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'loss_history': self.loss_history,
            'state_size': self.state_size,
            'action_size': self.action_size,
            'learning_rate': self.learning_rate,
            'gamma': self.gamma,
        }
        torch.save(checkpoint, filepath)
        print(f"✓ DQN model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model weights and hyperparameters."""
        if not os.path.exists(filepath):
            print(f"⚠ Model file not found: {filepath}")
            return False
        
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.q_network.load_state_dict(checkpoint['q_network_state'])
        self.target_network.load_state_dict(checkpoint['target_network_state'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state'])
        self.epsilon = checkpoint['epsilon']
        self.loss_history = checkpoint['loss_history']
        
        print(f"✓ DQN model loaded from {filepath}")
        return True
    
    def get_summary(self) -> dict:
        """Return agent summary for logging."""
        return {
            'epsilon': self.epsilon,
            'buffer_size': len(self.experience_buffer),
            'loss_history_avg': np.mean(self.loss_history[-100:]) if self.loss_history else 0,
            'num_updates': self.update_counter,
        }


if __name__ == "__main__":
    # Test DQN agent
    agent = DQNAgent(state_size=3, action_size=5, learning_rate=0.001)
    
    # Simulate some experiences
    print("Testing DQN Agent...")
    
    state = (0.1, 0.2, 0.8)
    for _ in range(100):
        action = agent.choose_action(state, training=True)
        next_state = (0.15, 0.25, 0.75)
        reward = random.random() * 10
        done = random.random() < 0.1
        
        agent.remember(state, action, reward, next_state, done)
    
    # Train
    for _ in range(50):
        loss = agent.replay()
    
    print(f"Sample loss: {agent.loss_history[-1]:.4f}")
    
    # Test save/load
    agent.save("test_dqn_model.pt")
    
    agent2 = DQNAgent(state_size=3, action_size=5)
    agent2.load("test_dqn_model.pt")
    
    print(f"Agent epsilon after load: {agent2.epsilon}")
    print("✓ DQN test passed!")
