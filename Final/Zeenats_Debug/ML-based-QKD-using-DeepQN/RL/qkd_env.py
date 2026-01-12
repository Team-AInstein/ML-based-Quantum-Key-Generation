# import random

# class QKDEnvironment:
#     def __init__(self):
#         # State = (qber_level, key_level)
#         # qber_level: 0=low, 1=medium, 2=high
#         # key_level: 0=low, 1=medium, 2=high
#         self.state = (2, 0)

#         self.actions = [
#             "change_basis_ratio",
#             "increase_sample_size",
#             "optimize_privacy_amplification"
#         ]

#     def reset(self):
#         self.state = (2, 0)
#         return self.state

#     def step(self, action):
#         qber, key = self.state

#         if action == "change_basis_ratio":
#             qber = max(0, qber - 1)

#         elif action == "increase_sample_size":
#             key = min(2, key + 1)

#         elif action == "optimize_privacy_amplification":
#             qber = max(0, qber - 1)
#             key = max(0, key - 1)

#         self.state = (qber, key)

#         # Reward function
#         if qber == 0 and key == 2:
#             reward = 100
#             done = True
#         elif qber == 2:
#             reward = -50
#             done = False
#         else:
#             reward = 10
#             done = False

#         return self.state, reward, done

import random

class QKDEnv:
    """
    Simple Reinforcement Learning environment
    for optimizing QKD parameters.
    """

    def __init__(self):
        # State: (noise_level, eavesdropper_present)
        self.noise_level = 0.05
        self.eavesdropper = 0

        self.max_noise = 3
        self.done = False
        self.actions = [0, 1, 2, 3, 4]
    def reset(self):
        self.noise_level = random.randint(0, self.max_noise)
        self.eavesdropper = random.randint(0, 1)
        self.done = False
        return (self.noise_level, self.eavesdropper)

    # def step(self, action):
    #     """
    #     Actions:
    #     0 -> Increase basis reconciliation
    #     1 -> Decrease basis reconciliation
    #     2 -> Increase key length
    #     3 -> Decrease key length
    #     4 -> Abort protocol
    #     """

    #     reward = 0

    #     if action == 4:  # Abort
    #         reward = -20
    #         self.done = True
    #     else:
    #         if self.eavesdropper == 1:
    #             reward = -10
    #         else:
    #             reward = 15

    #     # Environment dynamics
    #     self.noise_level = min(
    #         self.max_noise,
    #         max(0, self.noise_level + random.choice([-1, 0, 1]))
    #     )

    #     next_state = (self.noise_level, self.eavesdropper)
    #     return next_state, reward, self.done
    def step(self, action):
        """
        Actions:
        0 -> Increase basis reconciliation
        1 -> Decrease basis reconciliation
        2 -> Increase error correction
        3 -> Decrease error correction
        4 -> Abort protocol
        """

        if action == 4:
            return (round(self.noise_level, 3), self.eavesdropper), -50, True

        # Eve increases QBER
        if self.eavesdropper == 1:
            self.noise_level += random.uniform(0.02, 0.05)
        else:
            self.noise_level += random.uniform(-0.01, 0.01)

        # Agent actions influence QBER
        if action in [0, 2]:  # optimization actions
            self.noise_level -= 0.02
        elif action in [1, 3]:
            self.noise_level += 0.02

        # Clamp QBER (PHYSICALLY VALID)
        self.noise_level = max(0.0, min(self.noise_level, 0.25))

        # Reward logic
        if self.noise_level < 0.11:
            reward = 20
        elif self.noise_level < 0.20:
            reward = 5
        else:
            reward = -20

        done = self.noise_level >= 0.25

        return (round(self.noise_level, 3), self.eavesdropper), reward, done