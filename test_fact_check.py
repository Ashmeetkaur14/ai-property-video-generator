from script_generator import load_property, build_script
from fact_check import fact_check

prop = load_property("sample_property.json")
scenes = build_script(prop)

# Test 1: the real script should pass
print("Test 1 (clean script):", "PASS" if not fact_check(prop, scenes) else "FAIL")

# Test 2: a fake feature should be caught
bad = scenes + [{"caption": "Swimming pool", "subtitle": "", "voice": "Free gym for 100 families."}]
problems = fact_check(prop, bad)
print("Test 2 (fake facts caught):", "PASS" if problems else "FAIL")
for p in problems:
    print("  ", p)

# Test 3: a wrong price should be caught
wrong = [dict(scenes[0], voice="Priced at Rs. 30 Lakh.")]
print("Test 3 (wrong price caught):", "PASS" if fact_check(prop, wrong) else "FAIL")