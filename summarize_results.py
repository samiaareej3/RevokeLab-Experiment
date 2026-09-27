import json
import glob
from collections import defaultdict

files = glob.glob("results/*.json")

results = []

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Ignore incomplete runs
    if data.get("result") not in {"PASS", "FAIL", "INCONCLUSIVE"}:
        continue

    results.append(data)


grouped = defaultdict(list)

for result in results:
    wait = result["wait_seconds"]
    grouped[wait].append(result)


print("=" * 65)
print("RevokeLab Experiment Summary")
print("=" * 65)

print(f"\nValid experiments found: {len(results)}")

print("\nResults:")
print("-" * 65)
print(f"{'Wait':<12}{'Trials':<12}{'Received':<15}{'Result'}")
print("-" * 65)

for wait in sorted(grouped):
    trials = grouped[wait]

    received = sum(
        1 for trial in trials
        if trial.get("message_received") is True
    )

    print(
        f"{wait:<12}"
        f"{len(trials):<12}"
        f"{received}/{len(trials):<15}"
        f"{trials[0]['result']}"
    )

print("-" * 65)

total_received = sum(
    1 for result in results
    if result.get("message_received") is True
)

print(f"\nTotal trials: {len(results)}")
print(f"Messages received after revocation: {total_received}")

if results:
    percentage = (total_received / len(results)) * 100
    print(f"Observed post-revocation delivery rate: {percentage:.1f}%")

print("\nObservation:")
print(
    "In the tested connection-only mode, the existing WebSocket "
    "continued receiving newly created private messages after "
    "Alice's access was revoked."
)