import json
from app.config import client, MODEL_NAME


def detect_red_flags(classified_transactions):

    prompt = f"""
You are an AI financial risk detection engine used by banks.

Analyze bank transactions and identify risk patterns.

STRICT INSTRUCTIONS:
- Return ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include extra text

Schema:

{{
  "red_flags": [
    {{
      "flag_type": "Overdraft | Bounced Cheque | Gambling Activity | Large Unexplained Transfer | Defaulted Loan EMI | Frequent Cash Withdrawal | Suspicious Spending Pattern",
      "description": "Clear financial risk explanation",
      "Credit": number or null,
      "Balance": number or null,
      "confidence": number (0 to 1),
      "related_transaction_dates": ["YYYY-MM-DD"]
    }}
  ]
}}

Detection rules:
- Look for financial stress patterns
- Detect repeated gambling merchants
- Detect EMI bounce / cheque bounce
- Detect sudden large transactions
- Detect cash withdrawal frequency spikes
- Detect abnormal spending vs normal behaviour
- Group related transactions into ONE red flag
- Confidence should reflect how certain the model is about the flag

Transactions:
{json.dumps(classified_transactions, indent=2)}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        raw_output = response.text.strip()

        #  CLEAN GEMINI OUTPUT
        cleaned = (
            raw_output
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        parsed = json.loads(cleaned)

        if "red_flags" not in parsed:
            return {"red_flags": []}

        #  NORMALIZATION
        for flag in parsed["red_flags"]:
            flag["Credit"] = (
                float(flag["Credit"]) if flag.get("Credit") not in [None, "null", ""] else None
            )
            flag["Balance"] = (
                float(flag["Balance"]) if flag.get("Balance") not in [None, "null", ""] else None
            )
            flag["confidence"] = (
                float(flag["confidence"]) if flag.get("confidence") not in [None, "null", ""] else 0.0
            )
            flag["related_transaction_dates"] = flag.get("related_transaction_dates", [])

        return parsed

    except json.JSONDecodeError:
        return {
            "error": "INVALID_JSON_FROM_MODEL",
            "raw_output": raw_output
        }

    except Exception as e:
        return {
            "error": "RED_FLAG_DETECTION_FAILED",
            "details": str(e)
        }