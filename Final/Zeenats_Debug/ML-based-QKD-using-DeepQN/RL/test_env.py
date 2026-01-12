# from qkd_env import QKDEnv

# env = QKDEnv()
# state = env.reset()
# print("Initial state:", state)

# for _ in range(5):
#     action = 0
#     next_state, reward, done = env.step(action)
#     print("Next:", next_state, "Reward:", reward, "Done:", done)


# qkd_env.py
# RL Environment for BB84 QKD Optimization

# class QKDEnv:
#     """
#     State:
#         (basis_ratio, noise_level)
#         basis_ratio: 0 = low, 1 = medium, 2 = high
#         noise_level: 0 = low, 1 = medium, 2 = high

#     Actions:
#         0 -> decrease basis ratio
#         1 -> increase basis ratio
#         2 -> decrease noise
#         3 -> increase noise
#         4 -> do nothing
#     """

#     def __init__(self):
#         self.max_steps = 10
#         self.current_step = 0
#         self.reset()

#     def reset(self):
#         self.state = (2, 0)  # Start with high basis ratio, low noise
#         self.current_step = 0
#         return self.state

#     def step(self, action):
#         basis_ratio, noise = self.state

#         # ---- Apply Action ----
#         if action == 0:
#             basis_ratio = max(0, basis_ratio - 1)
#         elif action == 1:
#             basis_ratio = min(2, basis_ratio + 1)
#         elif action == 2:
#             noise = max(0, noise - 1)
#         elif action == 3:
#             noise = min(2, noise + 1)
#         elif action == 4:
#             pass  # no operation

#         # ---- Reward Design ----
#         # Lower noise and balanced basis ratio is preferred
#         reward = 10
#         reward -= noise * 15

#         if basis_ratio == 1:  # ideal BB84 balance
#             reward += 10
#         else:
#             reward -= 5

#         # ---- Update State ----
#         self.state = (basis_ratio, noise)
#         self.current_step += 1

#         # ---- Termination ----
#         done = self.current_step >= self.max_steps

#         return self.state, reward, done


from qkd_env import QKDEnv

env = QKDEnv()

state = env.reset()
print("Initial State:", state)

for step in range(5):
    action = step % 5  # try different actions
    next_state, reward, done = env.step(action)

    print(
        f"Step {step} | Action: {action} | "
        f"Next State: {next_state} | Reward: {reward} | Done: {done}"
    )
