from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from explainability import ExplainabilityEngine
from file_validation_service import detect_file_type, get_results
from attrClassifier import MediaAnalyzer

import shutil, os, asyncio, random
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use absolute path relative to this file to ensure consistency regardless of where the server is run
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "media")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.mount("/media", StaticFiles(directory=UPLOAD_FOLDER), name="media")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    file_type = detect_file_type(file.filename)
    if file_type == "unknown":
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"File saved to: {filepath}")

    loop = asyncio.get_running_loop()
    try:
        # ai_scan_result, analysis_result = await loop.run_in_executor(None, get_results, filepath)
        
        # Using local analyzer and random verdict to save credits
        analyzer = MediaAnalyzer()
        if "video" in file_type.lower():
            analysis_result = await loop.run_in_executor(None, analyzer.analyze_video, filepath)
        else:
            analysis_result = await loop.run_in_executor(None, analyzer.analyze_image, filepath)
            
        is_fake = random.choice([True, False])
        ai_scan_result = {
            "ai_detected": is_fake,
            "deepfake_detected": is_fake,
            "ai_confidence": random.uniform(0.8, 0.99) if is_fake else random.uniform(0.01, 0.2),
            "deepfake_confidence": random.uniform(0.8, 0.99) if is_fake else random.uniform(0.01, 0.2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    explainer = ExplainabilityEngine()
    brief_overview = await explainer.explain_overall_analysis(analysis_result, ai_scan_result)
    
    return {
        "status": "success",
        "filename": file.filename,
        "path": f"/media/{file.filename}",
        "size": os.path.getsize(filepath),
        "type": file_type,
        "ai_scan_result": ai_scan_result,
        "analysis_result": analysis_result, # Frontend sends this back to /analyze/metrics
        "brief_overview": brief_overview
    }

class MetricRequest(BaseModel):
    analysis_result: Dict[str, Any]

@app.post("/analyze/metrics")
async def analyze_metrics(request: MetricRequest):
    """
    Step 2: Takes the analysis result from Step 1 and generates detailed metric explanations in parallel.
    """
    explainer = ExplainabilityEngine()
    metric_explanations = await explainer.analyze_all_metrics(request.analysis_result)

    return {
        "metricExplanations": metric_explanations,
    }