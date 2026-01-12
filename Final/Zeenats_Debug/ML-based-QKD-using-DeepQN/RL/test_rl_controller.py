from rl_bb84_controller import RLBb84Controller

controller = RLBb84Controller()

for qber in [0.01, 0.05, 0.12, 0.25]:
    action = controller.decide(qber)
    print(f"QBER={qber} → RL Action={action}")
