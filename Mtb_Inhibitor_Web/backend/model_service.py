import os
import io
import base64
import numpy as np
import pandas as pd
import torch
from rdkit import Chem
from rdkit.Chem import Draw, Descriptors, rdMolDescriptors
from chemprop.utils import load_checkpoint, load_scalers
from chemprop.data import MoleculeDataLoader, MoleculeDataset, MoleculeDatapoint
from chemprop.train import predict
from chemprop.features import get_features_generator

# --- [Constants & Config] ---
TASK_NAMES = [f'C{i}' for i in range(1, 14)]
COG_MAPPING = {
    'C1':  {'Name': 'TCA 회로 및 중심 탄소 대사'},
    'C2':  {'Name': '번역 및 tRNA 합성'},
    'C3':  {'Name': '비방향족 아미노산 생합성'},
    'C4':  {'Name': '방향족 아미노산 생합성'},
    'C5':  {'Name': '스트레스 방어 및 대사 경로 평형 유지'},
    'C6':  {'Name': 'tRNA 및 초기 폴리펩타이드 변형'},
    'C7':  {'Name': '엽산 및 퓨린 대사'},
    'C8':  {'Name': 'DNA 복제 및 전사 조절'},
    'C9':  {'Name': '지질 및 지질 보조인자 합성'}, 
    'C10': {'Name': '당분해 및 당신생합성'},
    'C11': {'Name': '펩티도글리칸 및 전구체 합성'},
    'C12': {'Name': '퓨린 및 피리미딘 대사'},
    'C13': {'Name': '포르피린 화합물 합성'}
}

DEFAULT_CUTOFFS = {
    'C1': 0.04, 'C2': 0.02, 'C3': 0.05, 'C4': 0.06, 'C5': 0.04,
    'C6': 0.05, 'C7': 0.08, 'C8': 0.05, 'C9': 0.02, 'C10': 0.03,
    'C11': 0.07, 'C12': 0.05, 'C13': 0.06
}

class MtbModelService:
    def __init__(self, base_model_path):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_paths = [os.path.join(base_model_path, f'model_{i}', 'model.pt') for i in range(5)]
        self.features_generator = get_features_generator('rdkit_2d_normalized')
        
        # Optimize PyTorch threading for balance between speed and memory
        torch.set_num_threads(2)

    def predict_smiles(self, smiles_list):
        try:
            # Prepare datapoints with RDKit features
            datapoints = []
            for s in smiles_list:
                f = self.features_generator(s)
                dp = MoleculeDatapoint(smiles=[s], features=f)
                datapoints.append(dp)
            
            all_preds = []
            import gc
            
            for path in self.model_paths:
                if not os.path.exists(path):
                    continue
                
                # Load one model at a time to save memory on Render
                model = load_checkpoint(path, device=self.device)
                scalers = load_scalers(path)
                
                scaler, features_scaler, _, _, _ = scalers
                
                # Clone data to avoid repeated scaling
                current_test_data = MoleculeDataset(datapoints)
                if features_scaler is not None:
                    current_test_data.normalize_features(features_scaler)
                
                # num_workers=0, batch_size=8 to prevent memory spikes
                loader = MoleculeDataLoader(dataset=current_test_data, batch_size=8, num_workers=0)
                
                model_preds = predict(
                    model=model,
                    data_loader=loader,
                    scaler=scaler
                )
                all_preds.append(np.array(model_preds))
                
                # Release memory explicitly
                del model
                del scalers
                gc.collect()
            
            if not all_preds:
                return None
                
            avg_scores = np.mean(all_preds, axis=0)
            return avg_scores
        except Exception as e:
            print(f"Prediction Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_mol_image_base64(self, smiles):
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                img = Draw.MolToImage(mol, size=(300, 300))
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                return base64.b64encode(buffered.getvalue()).decode()
        except:
            pass
        return None

    def get_radar_data(self, prob_row):
        categories = TASK_NAMES
        values = [float(prob_row[f'{c}_Prob']) for c in categories]
        cutoffs = [float(self.cutoffs.get(c, 0.05)) for c in categories]
        
        return {
            "categories": categories,
            "values": values,
            "cutoffs": cutoffs,
            "labels": [COG_MAPPING[c]['Name'] for c in categories]
        }

    def get_drug_properties(self, smiles):
        try:
            mol = Chem.MolFromSmiles(smiles)
            if not mol:
                return None
            
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            tpsa = Descriptors.TPSA(mol)
            hbd = rdMolDescriptors.CalcNumHBD(mol)
            hba = rdMolDescriptors.CalcNumHBA(mol)
            
            return {
                "MW": {"value": round(mw, 2), "unit": "Da", "status": "적합" if mw <= 500 else "부적합"},
                "LogP": {"value": round(logp, 2), "unit": "", "status": "적합" if 0 <= logp <= 5 else "부적합"},
                "TPSA": {"value": round(tpsa, 2), "unit": "Å²", "status": "적합" if tpsa <= 140 else "부적합"},
                "HBD": {"value": hbd, "unit": "개", "status": "적합" if hbd <= 5 else "부적합"},
                "HBA": {"value": hba, "unit": "개", "status": "적합" if hba <= 10 else "부적합"}
            }
        except Exception as e:
            print(f"Property Calculation Error: {e}")
            return None
