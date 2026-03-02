import numpy as np
import sys
import argparse
import torch

# Monkeypatch numpy for legacy chemprop
if not hasattr(np, 'VisibleDeprecationWarning'):
    np.VisibleDeprecationWarning = DeprecationWarning

if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([argparse.Namespace])

import os
from chemprop.utils import load_checkpoint, load_scalers
from chemprop.data import MoleculeDataLoader, MoleculeDataset, MoleculeDatapoint
from chemprop.train import predict
from chemprop.features import get_features_generator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(SCRIPT_DIR, "Results", "Trained_model", "DMPNN_RN_Ensemble_5", "fold_0", "model_0", "model.pt")

smiles_list = ['CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5']

if os.path.exists(model_path):
    print("Loading model and scalers...")
    model = load_checkpoint(model_path)
    scaler, features_scaler, _, _, _ = load_scalers(model_path)
    
    # Generate features
    generator = get_features_generator('rdkit_2d_normalized')
    
    # Prepare data
    datapoints = []
    for s in smiles_list:
        f = generator(s)
        dp = MoleculeDatapoint(smiles=[s], features=f)
        datapoints.append(dp)
    
    test_data = MoleculeDataset(datapoints)
    
    if features_scaler is not None:
        test_data.normalize_features(features_scaler)
        
    # Set num_workers=0 for Windows compatibility
    loader = MoleculeDataLoader(dataset=test_data, batch_size=len(smiles_list), num_workers=0)
    
    # Predict
    model_preds = predict(
        model=model,
        data_loader=loader,
        scaler=scaler
    )
    print(f"Predictions: {model_preds}")
else:
    print("Model not found")
