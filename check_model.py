import numpy as np
import sys
import argparse
import torch

# Monkeypatch numpy for legacy chemprop
if not hasattr(np, 'VisibleDeprecationWarning'):
    np.VisibleDeprecationWarning = DeprecationWarning

# Allow-list globals for torch.load in PyTorch 2.6+
if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([argparse.Namespace])

import os
from chemprop.utils import load_checkpoint

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(SCRIPT_DIR, "Results", "Trained_model", "DMPNN_RN_Ensemble_5", "fold_0", "model_0", "model.pt")

if os.path.exists(model_path):
    print(f"Loading model from {model_path}")
    model = load_checkpoint(model_path)
    print("Model loaded successfully")
    
    print(f"Model keys: {dir(model)}")
    if hasattr(model, 'readout'):
        print(f"Readout: {model.readout}")
        for layer in model.readout:
             if hasattr(layer, 'in_features'):
                print(f"Readout in_features: {layer.in_features}")
                # hidden_size is usually the first part
                # If hidden_size=300 and total=500, then features=200
                break
    
    # Try to find hidden_size
    try:
        # In chemprop 1.6, the encoder output size
        print(f"Features size: {model.features_size if hasattr(model, 'features_size') else 'Not found'}")
    except:
        pass
else:
    print("Model not found")
