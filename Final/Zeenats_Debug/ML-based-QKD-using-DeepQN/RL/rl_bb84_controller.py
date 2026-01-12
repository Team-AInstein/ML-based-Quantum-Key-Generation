from qkd_env import QKDEnv
from q_learning import QLearningAgent

class RLBb84Controller:
    def __init__(self):
        self.env = QKDEnv()
        self.agent = QLearningAgent(actions=self.env.actions)

    def decide(self, qber):
        self.env.qber = round(qber, 3)
        self.env.eavesdropper = 1 if qber > 0.11 else 0

        state = (self.env.qber, self.env.eavesdropper)
        action = self.agent.choose_action(state)

        return action
