CONFIDENCE_THRESHOLD = 0.7


def evaluate_confidence_metrics(predictions):
    if not predictions:
        return {"error": "No predictions available for evaluation"}

    total_transactions = len(predictions)

    high_confidence = [
        p for p in predictions if p.get("confidence", 0) >= CONFIDENCE_THRESHOLD
    ]

    high_confidence_count = len(high_confidence)

    salary_high_conf = [
        p for p in high_confidence if p.get("label") == "salary_credit"
    ]

    negative_high_conf = [
        p for p in high_confidence if p.get("label") == "negative_behavior"
    ]

    avg_confidence = round(
        sum(p.get("confidence", 0) for p in predictions) / total_transactions, 3
    )

    return {
        "total_transactions": total_transactions,

        #  Core metric
        "high_confidence_coverage": round(
            high_confidence_count / total_transactions, 3
        ),

        # Task-aligned metrics
        "salary_high_confidence_rate": round(
            len(salary_high_conf) / high_confidence_count, 3
        ) if high_confidence_count else 0,

        "negative_behavior_high_confidence_rate": round(
            len(negative_high_conf) / high_confidence_count, 3
        ) if high_confidence_count else 0,

        # Health metric
        "average_confidence": avg_confidence,

        "confidence_threshold": CONFIDENCE_THRESHOLD
    }
