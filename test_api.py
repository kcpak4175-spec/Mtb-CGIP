import requests
import os

url_predict = "http://localhost:8000/predict"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(SCRIPT_DIR, "Data", "Mtb_inhibitors", "Mtb_inhibitors.csv")

def test_prediction():
    if os.path.exists(csv_path):
        print(f"Testing prediction API with {csv_path}...")
        try:
            with open(csv_path, 'rb') as f:
                files = {'file': ('Mtb_inhibitors.csv', f, 'text/csv')}
                response = requests.post(url_predict, files=files)
                
            if response.status_code == 200:
                data = response.json()
                print("Predict API Test Successful!")
                session_id = data.get('session_id')
                print(f"Session ID: {session_id}")
                
                # Check summary
                results = data.get('results', [])
                if results:
                    summary = results[0].get('Expert_Summary', '')
                    print(f"Summary Check: {summary}")
                    if "주요 기전" in summary:
                        print("WARNING: Mechanism still found in summary!")
                    else:
                        print("SUCCESS: Mechanism removed from summary.")
                
                return session_id
            else:
                print(f"Predict API Test Failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    return None

def test_export(session_id, fmt):
    url_export = f"http://localhost:8000/export/{session_id}?format={fmt}"
    print(f"Testing {fmt} export...")
    try:
        response = requests.get(url_export)
        if response.status_code == 200:
            print(f"{fmt} Export Successful! Size: {len(response.content)} bytes")
            # For CSV, check BOM
            if fmt == 'csv':
                if response.content.startswith(b'\xef\xbb\xbf'):
                    print("SUCCESS: CSV has UTF-8 BOM (utf-8-sig).")
                else:
                    print("WARNING: CSV lacks UTF-8 BOM.")
        else:
            print(f"{fmt} Export Failed: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure server is running before this
    sid = test_prediction()
    if sid:
        test_export(sid, "csv")
        test_export(sid, "excel")
