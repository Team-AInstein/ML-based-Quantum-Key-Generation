"""
Quick test of integrated training with minimal episodes
"""
from train_integrated import QKDTrainer

if __name__ == "__main__":
    print("Starting quick integration test...\n")
    
    # Small test: 3 episodes
    trainer = QKDTrainer(episodes=3, key_length=32, max_steps=5, model_save_dir="./models_test")
    trainer.train()
    
    print("\n✓ Integration test completed successfully!")
