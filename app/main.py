import os
import shutil
from fastapi import FastAPI, UploadFile, File

from app.parsers.csv_parser import parse_csv
from app.parsers.pdf_parser import parse_pdf
from app.gemini.classifier import classify_transactions
from app.evaluation.metrics import evaluate_confidence_metrics
from app.gemini.red_flags import detect_red_flags

app = FastAPI()

# In-memory storage
LAST_ANALYSIS_RESULT = []
LAST_GROUND_TRUTH = []


@app.post("/analyze/")
async def analyze_bank_statement(file: UploadFile = File(...)):
    global LAST_ANALYSIS_RESULT, LAST_GROUND_TRUTH

    try:
        temp_path = f"temp_{file.filename}"

        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Parsing
        if file.filename.endswith(".csv"):
            parsed_data = parse_csv(temp_path)
        elif file.filename.endswith(".pdf"):
            parsed_data = parse_pdf(temp_path)
        else:
            return {"error": "Unsupported file type"}

        # Extract ground truth (optional column) 
        LAST_GROUND_TRUTH = [
            row["true_label"]
            for row in parsed_data
            if "true_label" in row
        ]

        # transaction classification
        classified_output = classify_transactions(parsed_data)

        if isinstance(classified_output, dict) and "error" in classified_output:
            return classified_output

        # red flag detection
        red_flags_response = detect_red_flags(classified_output)

        
        if isinstance(red_flags_response, dict) and "error" in red_flags_response:
            red_flags = []
            red_flag_error = red_flags_response
        else:
            red_flags = red_flags_response.get("red_flags", [])
            red_flag_error = None

        # Storing results for evaluation later will use
        LAST_ANALYSIS_RESULT = classified_output

        # 
        return {
            "status": "success",
            "total_transactions": len(classified_output),
            "transactions": classified_output,
            "red_flags": red_flags,
            "red_flag_error": red_flag_error
        }

    except Exception as e:
        return {
            "error": "INTERNAL_SERVER_ERROR",
            "details": str(e)
        }


@app.post("/evaluate/")
def evaluate():
    if not LAST_ANALYSIS_RESULT:
        return {"error": "Run /analyze first"}

    return evaluate_confidence_metrics(LAST_ANALYSIS_RESULT)
