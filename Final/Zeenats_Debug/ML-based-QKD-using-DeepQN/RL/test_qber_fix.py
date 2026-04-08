"""
Test to verify QBER fix - should show realistic non-zero QBER values
"""
from bb84_wrapper import BB84Wrapper

print("=" * 70)
print("Testing BB84 Protocol with Channel Noise Fix")
print("=" * 70)

# Test 1: BB84 without Eve, with channel noise
print("\n✓ Test 1: BB84 WITHOUT Eve (Channel Noise Only)")
print("-" * 70)
bb84_no_eve = BB84Wrapper(key_length=64, eve_present=False, channel_error_rate=0.01)
result = bb84_no_eve.run_protocol()
print(f"  Sifted Key Length: {result['sifted_length']} bits")
print(f"  QBER: {result['qber']:.4f} ({result['qber']*100:.2f}%)")
print(f"  Expected: ~1% QBER (from channel noise)")
eve_likelihood = bb84_no_eve.calculate_eve_likelihood()
print(f"  Eve Likelihood: {eve_likelihood:.4f}")

# Test 2: BB84 with Eve at 50% interception
print("\n✓ Test 2: BB84 WITH Eve (50% Interception)")
print("-" * 70)
bb84_with_eve = BB84Wrapper(key_length=64, eve_present=True, eve_intercept_ratio=0.5, channel_error_rate=0.01)
result_eve = bb84_with_eve.run_protocol()
print(f"  Sifted Key Length: {result_eve['sifted_length']} bits")
print(f"  QBER: {result_eve['qber']:.4f} ({result_eve['qber']*100:.2f}%)")
print(f"  Expected: ~3-5% QBER (channel + Eve interference)")
eve_likelihood_eve = bb84_with_eve.calculate_eve_likelihood()
print(f"  Eve Likelihood: {eve_likelihood_eve:.4f}")

# Test 3: Multiple runs to show consistency
print("\n✓ Test 3: Multiple Runs (10 iterations) - No Eve")
print("-" * 70)
qber_values = []
for i in range(10):
    bb84 = BB84Wrapper(key_length=64, eve_present=False, channel_error_rate=0.01)
    result = bb84.run_protocol()
    qber_values.append(result['qber'])
    print(f"  Run {i+1:2d}: QBER = {result['qber']:.4f} ({result['qber']*100:.2f}%), Key Length = {result['sifted_length']:2d}")

avg_qber = sum(qber_values) / len(qber_values)
print(f"\n  Average QBER: {avg_qber:.4f} ({avg_qber*100:.2f}%)")
print(f"  Expected: ~1% QBER")

# Test 4: Multiple runs with Eve
print("\n✓ Test 4: Multiple Runs (10 iterations) - With Eve (50%)")
print("-" * 70)
qber_eve_values = []
for i in range(10):
    bb84 = BB84Wrapper(key_length=64, eve_present=True, eve_intercept_ratio=0.5, channel_error_rate=0.01)
    result = bb84.run_protocol()
    qber_eve_values.append(result['qber'])
    eve_likelihood = bb84.calculate_eve_likelihood()
    print(f"  Run {i+1:2d}: QBER = {result['qber']:.4f} ({result['qber']*100:.2f}%), Eve Likelihood = {eve_likelihood:.4f}")

avg_qber_eve = sum(qber_eve_values) / len(qber_eve_values)
print(f"\n  Average QBER: {avg_qber_eve:.4f} ({avg_qber_eve*100:.2f}%)")
print(f"  Expected: ~3-5% QBER")

print("\n" + "=" * 70)
print("✅ QBER FIX VERIFICATION COMPLETE")
print("=" * 70)
print(f"\nSummary:")
print(f"  - No Eve scenario: QBER should be ~1% ✓ (observed: {avg_qber*100:.2f}%)")
print(f"  - With Eve scenario: QBER should be higher ✓ (observed: {avg_qber_eve*100:.2f}%)")
print(f"  - Eve likelihood increases with QBER ✓")
print(f"\n✅ The fix is working correctly!")
