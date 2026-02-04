# Bank-Statement-Analysis-using-genai


## Overview
This project analyzes bank statement data (CSV/PDF) using **Google Gemini** to classify each transaction and flag potential anomalies.  
Each transaction is labeled and assigned a confidence score to indicate how certain the model is about its classification.

The goal is to demonstrate **what the model outputs** for a given bank statement, not to run a live API demo during review.

---

## What the System Does
Given a bank statement file, the system:
- Parses transactions from CSV or PDF
- Classifies each transaction into:
  - `salary_credit`
  - `emi_debit`
  - `negative_behavior`
  - `normal_transaction`
- Assigns a **confidence score** (0–1) for every classification
- Computes **confidence-based evaluation metrics**

---
- For demonstration purposes, the dataset is limited to a manageable number of rows to stay within Gemini free-tier API limits.

---

## Model Output
The model output is saved as JSON and committed to the repository.


