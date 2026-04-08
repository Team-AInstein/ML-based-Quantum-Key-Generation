"""
Test to verify channel_error_rate is working in BB84Wrapper
"""

from bb84_wrapper import BB84Wrapper

print("=" * 70)
print("TESTING BB84 WITH CHANNEL NOISE")
print("=" * 70)

# Test 1: No noise
print("\nTest 1: Channel Error Rate = 0% (perfect channel)")
bb84_no_noise = BB84Wrapper(
    key_length=256,
    eve_present=False,
    channel_error_rate=0.0
)
result_no_noise = bb84_no_noise.run_protocol()
print(f"  QBER: {result_no_noise['qber']:.6f} (should be ~0%)")
print(f"  Sifted Length: {result_no_noise['sifted_length']}")

# more thorough repeatable demonstration
print("\n-- Running 100 trials with 1% noise to show distribution --")
qber_samples = []
for i in range(100):
    bb84 = BB84Wrapper(key_length=256, eve_present=False, channel_error_rate=0.01)
    qber_samples.append(bb84.run_protocol()['qber'])
avg = sum(qber_samples)/len(qber_samples)
print(f"  100-trial mean QBER: {avg:.6f}, zeros: {qber_samples.count(0)}")

# Test 2: 1% noise
print("\nTest 2: Channel Error Rate = 1% (realistic)")
bb84_1pct = BB84Wrapper(
    key_length=256,
    eve_present=False,
    channel_error_rate=0.01
)
result_1pct = bb84_1pct.run_protocol()
print(f"  QBER: {result_1pct['qber']:.6f} (should be ~1%)")
print(f"  Sifted Length: {result_1pct['sifted_length']}")

# Test 3: 5% noise
print("\nTest 3: Channel Error Rate = 5% (high noise)")
bb84_5pct = BB84Wrapper(
    key_length=256,
    eve_present=False,
    channel_error_rate=0.05
)
result_5pct = bb84_5pct.run_protocol()
print(f"  QBER: {result_5pct['qber']:.6f} (should be ~5%)")
print(f"  Sifted Length: {result_5pct['sifted_length']}")

# Test 4: With Eve + noise
print("\nTest 4: Eve + 1% Channel Error Rate")
bb84_eve_noise = BB84Wrapper(
    key_length=256,
    eve_present=True,
    eve_intercept_ratio=1.0,
    channel_error_rate=0.01
)
result_eve_noise = bb84_eve_noise.run_protocol()
eve_likelihood = bb84_eve_noise.calculate_eve_likelihood()
print(f"  QBER: {result_eve_noise['qber']:.6f} (should be ~1.5% with Eve)")
print(f"  Eve Likelihood: {eve_likelihood:.6f} (should be > 0)")
print(f"  Sifted Length: {result_eve_noise['sifted_length']}")

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)

if result_no_noise['qber'] < 0.005:
    print("✓ No noise test: PASS (QBER ≈ 0%)")
else:
    print("✗ No noise test: FAIL (QBER should be ~0%)")

if 0.005 < result_1pct['qber'] < 0.02:
    print("✓ 1% noise test: PASS (QBER ≈ 1%)")
else:
    print(f"✗ 1% noise test: FAIL (QBER = {result_1pct['qber']:.6f}, should be ~0.01)")

if 0.04 < result_5pct['qber'] < 0.06:
    print("✓ 5% noise test: PASS (QBER ≈ 5%)")
else:
    print(f"✗ 5% noise test: FAIL (QBER = {result_5pct['qber']:.6f}, should be ~0.05)")

if result_eve_noise['qber'] > 0.005 and eve_likelihood > 0.0:
    print("✓ Eve + noise test: PASS (QBER > 0% and Eve detected)")
else:
    print(f"✗ Eve + noise test: FAIL (QBER = {result_eve_noise['qber']:.6f}, Eve = {eve_likelihood:.6f})")

print("\n✅ Channel noise testing complete!")
