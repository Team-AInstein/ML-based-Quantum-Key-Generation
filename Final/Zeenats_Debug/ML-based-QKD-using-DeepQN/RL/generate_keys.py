"""
Generate Secure Quantum Keys using BB84 + Privacy Amplification
"""

from bb84_wrapper import BB84Wrapper
from privacy_amplification import PrivacyAmplification


def generate_secure_key(key_length=256, eve_present=False, apply_pa=True):
    """
    Generate a secure quantum key using BB84 protocol.
    
    Args:
        key_length: Number of qubits to send (higher = more key bits)
        eve_present: Whether to simulate Eve eavesdropping
        apply_pa: Apply privacy amplification (recommended)
    
    Returns:
        Dictionary with key info
    """
    
    print("\n" + "="*70)
    print("QUANTUM KEY GENERATION USING BB84 PROTOCOL")
    print("="*70)
    
    # Configuration
    print(f"\n📋 Configuration:")
    print(f"   Key Length: {key_length} qubits")
    print(f"   Eve Present: {'Yes' if eve_present else 'No'}")
    print(f"   Privacy Amplification: {'Yes' if apply_pa else 'No'}")
    
    # Step 1: Run BB84 protocol
    print(f"\n⏳ Step 1: Running BB84 Protocol...")
    
    bb84 = BB84Wrapper(
        key_length=key_length,
        use_simulator=True,
        eve_present=eve_present,
        eve_intercept_ratio=0.8 if eve_present else 0.0  # Eve intercepts 80%
    )
    
    result = bb84.run_protocol()
    
    # Extract results
    sifted_key = result['sifted_key']
    qber = result['qber']
    sifted_length = result['sifted_length']
    
    print(f"   ✓ BB84 protocol complete!")
    print(f"     - Sent: {key_length} qubits")
    print(f"     - Sifted Key Length: {sifted_length} bits")
    print(f"     - QBER: {qber:.4f} ({qber*100:.2f}%)")
    
    # Step 2: Check security
    eve_likelihood = bb84.calculate_eve_likelihood()
    print(f"     - Eve Likelihood: {eve_likelihood:.4f}")
    
    if eve_likelihood > 0.5:
        print(f"     ⚠ WARNING: Likely eavesdropping detected!")
        print(f"     Proceeding with privacy amplification...")
    else:
        print(f"     ✓ Channel appears secure")
    
    # Step 3: Apply privacy amplification
    if apply_pa and sifted_length > 0:
        print(f"\n⏳ Step 2: Applying Privacy Amplification...")
        
        final_key, metadata = PrivacyAmplification.full_privacy_amplification_pipeline(
            sifted_key=sifted_key,
            eve_likelihood=eve_likelihood,
            method="parity"
        )
        
        print(f"   ✓ Privacy amplification complete!")
        print(f"     - Original Length: {metadata['original_length']} bits")
        print(f"     - Final Length: {metadata['final_length']} bits")
        print(f"     - Reduction Factor: {metadata['reduction_factor']:.2f}x")
        print(f"     - Error Correction Applied: {metadata['error_correction_applied']}")
    else:
        final_key = sifted_key
        metadata = {
            'original_length': sifted_length,
            'final_length': sifted_length,
            'reduction_factor': 1.0,
            'error_correction_applied': False
        }
        print(f"\n⏳ Step 2: Skipping Privacy Amplification")
    
    # Step 4: Display results
    print(f"\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\n📊 Key Statistics:")
    print(f"   Initial Qubits: {key_length}")
    print(f"   After BB84 Sifting: {sifted_length} bits ({sifted_length/key_length*100:.1f}%)")
    print(f"   After Privacy Amplification: {metadata['final_length']} bits")
    print(f"   Compression Ratio: {metadata['reduction_factor']:.2f}x")
    
    print(f"\n🔒 Security Information:")
    print(f"   QBER: {qber:.4f} (Theoretical min without Eve: 0%)")
    print(f"   Eve Likelihood: {eve_likelihood:.4f}")
    print(f"   Error Correction Applied: {metadata['error_correction_applied']}")
    
    # Display the actual key (binary)
    print(f"\n🔑 Sifted Key (before PA):")
    print(f"   Length: {len(sifted_key)} bits")
    print(f"   Key: {sifted_key}")
    
    if apply_pa:
        print(f"\n🔐 Final Secure Key (after PA):")
        print(f"   Length: {len(final_key)} bits")
        print(f"   Key: {final_key}")
    
    # Info about key security
    if eve_likelihood > 0.5:
        print(f"\n⚠️  SECURITY NOTICE:")
        print(f"   Eve's information has been reduced by ~{(1-eve_likelihood)*100:.1f}%")
        print(f"   This key should be used cautiously")
    else:
        print(f"\n✅ SECURITY STATUS:")
        print(f"   Key appears secure (low Eve likelihood)")
        print(f"   Safe to use for encryption")
    
    return {
        'sifted_key': sifted_key,
        'final_key': final_key,
        'qber': qber,
        'eve_likelihood': eve_likelihood,
        'sifted_length': sifted_length,
        'final_length': len(final_key),
        'metadata': metadata
    }


def demo_multiple_keys():
    """Generate and display multiple keys."""
    
    print("\n" + "="*70)
    print("DEMO: GENERATING 3 SECURE KEYS")
    print("="*70)
    
    for i in range(1, 4):
        print(f"\n{'─'*70}")
        print(f"KEY #{i}")
        print(f"{'─'*70}")
        
        eve_present = i == 3  # Third key has Eve
        result = generate_secure_key(key_length=256, eve_present=eve_present)
        
        print(f"\n✓ Key #{i} generated: {result['final_length']} bits")


def main():
    """Main function - choose what to do."""
    
    print("\n" + "="*70)
    print("BB84 SECURE KEY GENERATION")
    print("="*70)
    print("\nChoose an option:")
    print("  1. Generate ONE secure key (256 qubits)")
    print("  2. Generate key WITH Eve eavesdropping")
    print("  3. Generate WITHOUT privacy amplification")
    print("  4. Demo: Generate 3 keys (one with Eve)")
    print("  5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        print("\n→ Generating 1 secure key (256 qubits, no Eve, with PA)...")
        result = generate_secure_key(key_length=256, eve_present=False, apply_pa=True)
        
    elif choice == "2":
        print("\n→ Generating key with Eve eavesdropping (256 qubits)...")
        result = generate_secure_key(key_length=256, eve_present=True, apply_pa=True)
        
    elif choice == "3":
        print("\n→ Generating key without privacy amplification (256 qubits)...")
        result = generate_secure_key(key_length=256, eve_present=False, apply_pa=False)
        
    elif choice == "4":
        demo_multiple_keys()
        return
        
    else:
        print("Exiting...")
        return
    
    # Save results
    print(f"\n" + "="*70)
    print("SAVING RESULTS")
    print("="*70)
    
    with open("generated_key.txt", "w") as f:
        f.write(f"Sifted Key ({result['sifted_length']} bits):\n")
        f.write(result['sifted_key'] + "\n\n")
        f.write(f"Final Key ({result['final_length']} bits):\n")
        f.write(result['final_key'] + "\n\n")
        f.write(f"QBER: {result['qber']:.4f}\n")
        f.write(f"Eve Likelihood: {result['eve_likelihood']:.4f}\n")
    
    print("✓ Key saved to: generated_key.txt")
    print("\n✅ Done!")


if __name__ == "__main__":
    # Quick demo (non-interactive)
    print("\n" + "="*70)
    print("AUTOMATIC DEMO: Generating 1 Secure Key")
    print("="*70)
    
    result = generate_secure_key(key_length=256, eve_present=False, apply_pa=True)
    
    print(f"\n" + "="*70)
    print("✅ KEY GENERATION COMPLETE")
    print("="*70)
    print(f"\nYou now have:")
    print(f"  • Sifted Key: {result['sifted_length']} bits")
    print(f"  • Secure Key (after PA): {result['final_length']} bits")
    print(f"  • Security Level: {'High ✅' if result['eve_likelihood'] < 0.5 else 'Compromised ⚠️'}")
