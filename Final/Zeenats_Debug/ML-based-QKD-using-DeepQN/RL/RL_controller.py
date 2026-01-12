# RL_QKD/rl_controller.py

class RLBB84Controller:
    def __init__(self):
        # default BB84 parameters
        self.z_ratio = 0.5
        self.x_ratio = 0.5

    def apply_action(self, action):
        """
        Actions coming from RL agent
        """
        if action == "increase_z":
            self.z_ratio = min(0.9, self.z_ratio + 0.1)
        elif action == "increase_x":
            self.z_ratio = max(0.1, self.z_ratio - 0.1)

        self.x_ratio = 1 - self.z_ratio

    def get_basis_ratio(self):
        return self.z_ratio, self.x_ratio
