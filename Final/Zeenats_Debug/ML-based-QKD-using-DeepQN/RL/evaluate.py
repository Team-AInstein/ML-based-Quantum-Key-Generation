from qkd_env import QKDEnvironment
from q_learning import QLearningAgent

env = QKDEnvironment()
agent = QLearningAgent(actions=env.actions)

# 🔒 Disable exploration
agent.epsilon = 0.0

state = env.reset()
print("Initial State:", state)

for step in range(10):
    action = agent.choose_action(state)
    next_state, reward, done = env.step(action)

    print(f"Step {step} | Action: {action} | State: {next_state}")

    state = next_state
    if done:
        print("🎯 Optimal secure state reached!")
        break
