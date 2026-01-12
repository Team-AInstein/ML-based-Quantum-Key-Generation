from qkd_env import QKDEnv
from q_learning import QLearningAgent

env = QKDEnv()
agent = QLearningAgent(actions=env.actions)

episodes = 200

for episode in range(episodes):
    state = env.reset()

    for step in range(20):
        action = agent.choose_action(state)
        next_state, reward, done = env.step(action)

        agent.update(state, action, reward, next_state)
        state = next_state

        if done:
            break

    if episode % 20 == 0:
        print(f"Episode {episode} | Final State: {state}")
