import requests
import json

BASE_URL = "http://localhost:8000"

def test_cumulative_direct_export():
    print("Testing cumulative direct input and export...")
    
    # 1. First direct input
    payload1 = {"smiles": "CC(=O)OC1=CC=CC=C1C(=O)O", "name": "Aspirin"}
    resp1 = requests.post(f"{BASE_URL}/predict-direct", json=payload1)
    resp1.raise_for_status()
    data1 = resp1.json()
    session_id = data1["session_id"]
    print(f"Session Created: {session_id}")
    
    # 2. Second direct input with same session_id
    payload2 = {"smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C", "name": "Caffeine", "session_id": session_id}
    resp2 = requests.post(f"{BASE_URL}/predict-direct", json=payload2)
    resp2.raise_for_status()
    print(f"Added Caffeine to Session {session_id}")
    
    # 3. Try to export
    export_url = f"{BASE_URL}/export/{session_id}?format=csv"
    resp_export = requests.get(export_url)
    resp_export.raise_for_status()
    
    csv_content = resp_export.text
    print("\nExported CSV Snippet:")
    print("\n".join(csv_content.splitlines()[:5]))
    
    if "Aspirin" in csv_content and "Caffeine" in csv_content:
        print("\nSUCCESS: Both compounds found in export!")
    else:
        print("\nFAILED: Compounds missing from export.")

if __name__ == "__main__":
    test_cumulative_direct_export()
