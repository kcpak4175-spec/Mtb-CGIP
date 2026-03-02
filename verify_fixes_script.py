import os

base_dir = r"c:\Users\asia\Desktop\Mtb_CGIP_final_Pred-main"
hardcoded_substr = "c:\\Users\\kcpak"

files_to_check = [
    "verify_env.py",
    "check_model.py",
    "predict_check.py",
    "test_api.py"
]

print("Checking for hardcoded paths...")
for fname in files_to_check:
    fpath = os.path.join(base_dir, fname)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            if hardcoded_substr in content:
                print(f"[FAIL] {fname} still contains hardcoded path '{hardcoded_substr}'")
            else:
                print(f"[PASS] {fname} is clean.")
    else:
        print(f"[WARN] {fname} not found.")

print("\nChecking batch files...")
start_bat = os.path.join(base_dir, "Start_Env_Setup.bat")
with open(start_bat, "r", encoding="utf-8") as f:
    content = f.read()
    if "requirements.txt" in content:
        print("[PASS] Start_Env_Setup.bat uses requirements.txt")
    else:
        print("[FAIL] Start_Env_Setup.bat does NOT use requirements.txt")

run_bat = os.path.join(base_dir, "Mtb-Inhibitor Finder AI.bat")
with open(run_bat, "r", encoding="utf-8") as f:
    content = f.read()
    if "netstat -an" in content and "8000" in content:
        print("[PASS] Mtb-Inhibitor Finder AI.bat has port check loop.")
    else:
        print("[FAIL] Mtb-Inhibitor Finder AI.bat does NOT have port check loop.")

req_file = os.path.join(base_dir, "requirements.txt")
if os.path.exists(req_file):
    print("[PASS] requirements.txt exists.")
else:
    print("[FAIL] requirements.txt missing.")
