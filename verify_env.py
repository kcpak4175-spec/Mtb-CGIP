import sys
import os

# Try importing chemprop parts
try:
    from chemprop.utils import load_checkpoint
    from chemprop.data import MoleculeDataLoader, get_data
    print("Chemprop imports successful (legacy style).")
except ImportError as e:
    print(f"Chemprop legacy imports failed: {e}")
    try:
        import chemprop
        print(f"Chemprop version: {chemprop.__version__}")
    except:
        print("Chemprop import failed entirely.")

import torch
import numpy as np

# Test model loading if a model exists
# Test model loading if a model exists
# Modified to be relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_MODEL_PATH = os.path.join(SCRIPT_DIR, "Results", "Trained_model", "DMPNN_RN_Ensemble_5", "fold_0")
model_path = os.path.join(BASE_MODEL_PATH, "model_0", "model.pt")

if os.path.exists(model_path):
    print(f"Model found at {model_path}")
    try:
        # Check if we can load it
        from chemprop.utils import load_checkpoint
        device = torch.device('cpu')
        model = load_checkpoint(model_path, device=device)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Model loading failed: {e}")
else:
    print(f"Model not found at {model_path}")

# Test RDKit
try:
    from rdkit import Chem
    from rdkit.Chem import Draw
    mol = Chem.MolFromSmiles("CCO")
    img = Draw.MolToImage(mol)
    print("RDKit test successful.")
except Exception as e:
    print(f"RDKit test failed: {e}")
