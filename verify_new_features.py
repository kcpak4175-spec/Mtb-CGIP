import requests
import json

BASE_URL = "http://localhost:8000"

def test_predict_direct():
    print("Testing /predict-direct endpoint...")
    # Imatinib SMILES
    smiles = "CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5"
    payload = {
        "smiles": smiles,
        "name": "Imatinib"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict-direct", json=payload)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        if not results:
            print("FAILED: No results returned.")
            return

        compound = results[0]
        print(f"ID: {compound['ID']}")
        print(f"Hit Count: {compound['Hit_Count']}")
        
        properties = compound.get("Properties")
        if properties:
            print("Drug-likeness Properties:")
            for k, v in properties.items():
                print(f"  - {k}: {v['value']}{v['unit']} ({v['status']})")
        else:
            print("FAILED: No Properties found in response.")

    except Exception as e:
        print(f"ERROR: {e}")

def test_predict_direct_unnamed():
    print("\nTesting /predict-direct endpoint with unnamed compound...")
    smiles = "CC(=O)OC1=CC=CC=C1C(=O)O" # Aspirin
    payload = {
        "smiles": smiles
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict-direct", json=payload)
        response.raise_for_status()
        data = response.json()
        
        compound = data.get("results", [])[0]
        print(f"ID (should be Unknown): {compound['ID']}")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_predict_direct()
    test_predict_direct_unnamed()
