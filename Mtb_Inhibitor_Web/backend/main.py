import numpy as np
import sys
import argparse
import torch
import os
import io
import uuid
import pandas as pd
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# Monkeypatch numpy for legacy chemprop
if not hasattr(np, 'VisibleDeprecationWarning'):
    np.VisibleDeprecationWarning = DeprecationWarning

# Allow-list globals for torch.load in PyTorch 2.6+
if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([argparse.Namespace])

# Standard imports for the service
from model_service import MtbModelService, COG_MAPPING, TASK_NAMES

app = FastAPI(title="Mtb-Inhibitor Finder AI API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BACKEND_DIR))
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")
MODEL_PATH = os.path.join(PROJECT_ROOT, "Results", "Trained_model", "DMPNN_RN_Ensemble_5", "fold_0")

# Initialize Model Service
model_service = MtbModelService(MODEL_PATH)

# Store results in memory
results_store = {}

@app.post("/predict")
async def predict_compounds(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    smiles_col = next((col for col in df.columns if col.lower() == 'smiles'), None)
    if smiles_col is None:
        raise HTTPException(status_code=400, detail="Column 'smiles' not found in CSV.")
    
    name_col = next((col for col in df.columns if col.lower() in ['name', 'id', 'compound']), None)
    
    smiles_list = df[smiles_col].tolist()
    names = df[name_col].tolist() if name_col else [f"Compound_{i}" for i in range(len(smiles_list))]
    
    # Run prediction
    avg_scores = model_service.predict_smiles(smiles_list)
    
    if avg_scores is None:
        raise HTTPException(status_code=500, detail="Model prediction failed.")
    
    results = []
    for i, (smiles, name) in enumerate(zip(smiles_list, names)):
        row_data = {
            "ID": name,
            "SMILES": smiles,
            "Probabilities": {},
            "Active": {}
        }
        hit_count = 0
        for j, task in enumerate(TASK_NAMES):
            prob = float(avg_scores[i, j])
            cutoff = model_service.cutoffs.get(task, 0.05)
            is_active = int(prob >= cutoff)
            row_data["Probabilities"][task] = round(prob, 4)
            row_data["Active"][task] = is_active
            hit_count += is_active
        
        row_data["Hit_Count"] = hit_count
        row_data["Image"] = model_service.get_mol_image_base64(smiles)
        row_data["Radar"] = model_service.get_radar_data({f"{t}_Prob": row_data["Probabilities"][t] for t in TASK_NAMES})
        
        # Drug Properties
        row_data["Properties"] = model_service.get_drug_properties(smiles)
        
        # Expert Summary Logic (Simplified: removed mechanism details as requested)
        if hit_count > 0:
            row_data["Expert_Summary"] = f"이 화합물은 {hit_count}개의 필수 클러스터를 저해할 것으로 예상됩니다."
        else:
            row_data["Expert_Summary"] = "유의미한 저해 효과가 예측되지 않았습니다."
            
        results.append(row_data)
    
    # Sort by Hit_Count
    results = sorted(results, key=lambda x: x["Hit_Count"], reverse=True)
    
    session_id = str(uuid.uuid4())
    results_store[session_id] = results
    
    return {"session_id": session_id, "results": results}

@app.post("/predict-direct")
async def predict_direct(data: dict):
    smiles = data.get("smiles")
    name = data.get("name") or "Unknown"
    session_id = data.get("session_id")
    
    if not smiles:
        raise HTTPException(status_code=400, detail="SMILES is required.")
    
    # Run prediction
    avg_scores = model_service.predict_smiles([smiles])
    if avg_scores is None:
        raise HTTPException(status_code=500, detail="Model prediction failed.")
    
    row_data = {
        "ID": name,
        "SMILES": smiles,
        "Probabilities": {},
        "Active": {}
    }
    hit_count = 0
    for j, task in enumerate(TASK_NAMES):
        prob = float(avg_scores[0, j])
        cutoff = model_service.cutoffs.get(task, 0.05)
        is_active = int(prob >= cutoff)
        row_data["Probabilities"][task] = round(prob, 4)
        row_data["Active"][task] = is_active
        hit_count += is_active
    
    row_data["Hit_Count"] = hit_count
    row_data["Image"] = model_service.get_mol_image_base64(smiles)
    row_data["Radar"] = model_service.get_radar_data({f"{t}_Prob": row_data["Probabilities"][t] for t in TASK_NAMES})
    row_data["Properties"] = model_service.get_drug_properties(smiles)
    
    if hit_count > 0:
        row_data["Expert_Summary"] = f"이 화합물은 {hit_count}개의 필수 클러스터를 저해할 것으로 예상됩니다."
    else:
        row_data["Expert_Summary"] = "유의미한 저해 효과가 예측되지 않았습니다."
    
    # Session Management
    if not session_id or session_id not in results_store:
        session_id = str(uuid.uuid4())
        results_store[session_id] = []
    
    results_store[session_id].append(row_data)
        
    return {"session_id": session_id, "results": [row_data]}

@app.get("/export/{session_id}")
async def export_results(session_id: str, format: str = "csv"):
    if session_id not in results_store:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    results = results_store[session_id]
    export_data = []
    for r in results:
        item = {
            "Name": r["ID"],
            "SMILES": r["SMILES"],
            "Hit_Count": r["Hit_Count"]
        }
        # Drug Properties
        if r.get("Properties"):
            for prop_name, prop_data in r["Properties"].items():
                item[f"{prop_name}_Value"] = prop_data["value"]
                item[f"{prop_name}_Unit"] = prop_data["unit"]
                item[f"{prop_name}_Status"] = prop_data["status"]
        
        for t in TASK_NAMES:
            item[f"{t}_Prob"] = r["Probabilities"][t]
            item[f"{t}_Active"] = r["Active"][t]
        item["Expert_Summary"] = r["Expert_Summary"]
        export_data.append(item)
    
    df = pd.DataFrame(export_data)
    
    if format == "csv":
        output = io.StringIO()
        # Use utf-8-sig to prevent Korean character corruption in Excel
        df.to_csv(output, index=False, encoding='utf-8-sig')
        content = output.getvalue().encode('utf-8-sig')
        return StreamingResponse(
            io.BytesIO(content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=Mtb_Screening_Report.csv"}
        )
    elif format == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return StreamingResponse(
            output, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=Mtb_Screening_Report.xlsx"}
        )

# Serve Frontend
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    print(f"Warning: Frontend directory not found at {FRONTEND_DIR}")

if __name__ == "__main__":
    import uvicorn
    # Hugging Face Spaces port is 7860
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
