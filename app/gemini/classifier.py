import json
import time
from google.genai.errors import ClientError
from app.config import client, MODEL_NAME

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # seconds


def classify_transactions(data, chunk_size=15):
    all_results = []

    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]

        prompt = f"""
You are a financial analysis assistant.

For EACH transaction:
- Assign exactly ONE label from:
  salary_credit, emi_debit, negative_behavior, normal_transaction
- Provide a confidence score between 0 and 1

Rules:
- Do NOT group transactions
- Preserve all input fields
- Return ONLY valid JSON array

Example:
[
  {{
    "date": "2022-02-05",
    "amount": 52521,
    "label": "salary_credit",
    "confidence": 0.93
  }}
]

Transactions:
{chunk}
"""

        retries = 0
        backoff = INITIAL_BACKOFF

        while retries < MAX_RETRIES:
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt
                )

                text_output = response.text.strip()

                # Remove markdown if Gemini adds it
                if text_output.startswith("```"):
                    text_output = (
                        text_output.replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )

                parsed = json.loads(text_output)
                all_results.extend(parsed)
                break  # success → exit retry loop

            # FIXED ERROR HANDLING HERE
            except ClientError as e:
                if e.code == 429:
                    retries += 1
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    return {
                        "error": "GEMINI_API_ERROR",
                        "message": str(e)
                    }

            except json.JSONDecodeError:
                return {
                    "error": "INVALID_GEMINI_JSON",
                    "raw_output": text_output
                }

            except Exception as e:
                return {
                    "error": "UNEXPECTED_ERROR",
                    "details": str(e)
                }

        # Retries exhausted
        if retries == MAX_RETRIES:
            return {
                "error": "GEMINI_QUOTA_EXHAUSTED",
                "message": "Retry limit exceeded due to Gemini quota or rate limits."
            }

    return all_results
