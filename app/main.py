# import os
# import shutil
# from fastapi import FastAPI, UploadFile, File

# from app.parsers.csv_parser import parse_csv
# from app.parsers.pdf_parser import parse_pdf
# from app.gemini.classifier import classify_transactions
# from app.evaluation.metrics import evaluate_predictions

# app = FastAPI()


# @app.post("/analyze/")
# async def analyze_bank_statement(file: UploadFile = File(...)):
#     temp_path = f"temp_{file.filename}"

#     with open(temp_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     if file.filename.endswith(".csv"):
#         parsed_data = parse_csv(temp_path)
#     elif file.filename.endswith(".pdf"):
#         parsed_data = parse_pdf(temp_path)
#     else:
#         return {"error": "Unsupported file type"}

#     result = classify_transactions(parsed_data)

#     if isinstance(result, dict) and "error" in result:
#         return result

#     return {
#         "total_transactions": len(result),
#         "classified_transactions": result
#     }


# @app.post("/evaluate/")
# def evaluate(payload: dict):
#     predictions = payload.get("predictions")
#     ground_truth = payload.get("ground_truth")

#     if not predictions or not ground_truth:
#         return {"error": "Missing predictions or ground_truth"}

#     return evaluate_predictions(predictions, ground_truth)
import os
import shutil
from fastapi import FastAPI, UploadFile, File

from app.parsers.csv_parser import parse_csv
from app.parsers.pdf_parser import parse_pdf
from app.gemini.classifier import classify_transactions
from app.evaluation.metrics import evaluate_confidence_metrics
app = FastAPI()

# In-memory storage
LAST_ANALYSIS_RESULT = []
LAST_GROUND_TRUTH = []


@app.post("/analyze/")
async def analyze_bank_statement(file: UploadFile = File(...)):
    global LAST_ANALYSIS_RESULT, LAST_GROUND_TRUTH

    try:
        temp_path = f"temp_{file.filename}"

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ---- Parse file ----
        if file.filename.endswith(".csv"):
            parsed_data = parse_csv(temp_path)
        elif file.filename.endswith(".pdf"):
            parsed_data = parse_pdf(temp_path)
        else:
            return {"error": "Unsupported file type"}

        # Extract ground truth if present 
        # (Optional column: true_label)
        LAST_GROUND_TRUTH = [
            row["true_label"]
            for row in parsed_data
            if "true_label" in row
        ]

        #Gemini classification 
        gemini_output = classify_transactions(parsed_data)

        if isinstance(gemini_output, dict) and "error" in gemini_output:
            return gemini_output

        # Store for evaluation
        LAST_ANALYSIS_RESULT = gemini_output

        # RETURN full output to user
        return {
            "status": "success",
            "total_transactions": len(gemini_output),
            "transactions": gemini_output
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
