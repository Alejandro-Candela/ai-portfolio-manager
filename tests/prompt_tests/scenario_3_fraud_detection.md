# Prompt Test: Scenario 3 — Fraud Detection

## Overview
Tests the intake agent with a critical fraud detection use case.
Copy and paste each user message in order into the chat UI.

---

## Conversation Flow

### User Message 1: Problem
```
We lose millions annually to payment fraud that our current rules miss
```

### User Message 2: Who's affected
```
Finance, risk management, and our customers who get charged fraudulently
```

### User Message 3: What data do we have
```
PostgreSQL database with 5 years of transactions—amount, merchant, location, IP, device, time—plus flagged fraud cases
```

### User Message 4: What would success look like
```
Catch 90% of fraud attempts in real-time before the charge completes
```

### User Message 5: How urgent
```
critical—this is a revenue leak we need to stop now
```

---

## Expected Agent Output

Should produce JSON:
```json
{
  "extraction_complete": true,
  "use_case": {
    "title": "Real-time Payment Fraud Detection",
    "problem_statement": "Losing millions annually to undetected payment fraud",
    "stakeholders": ["Finance Team", "Risk Management", "Customers"],
    "available_data": "PostgreSQL database with 5 years of transactions: amount, merchant, location, IP, device, time, flagged fraud labels",
    "expected_outcome": "Detect 90% of fraud attempts in real-time before charge completes",
    "urgency": "critical"
  }
}
```
